import asyncio
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from masala_common.app import create_app
from masala_common.db import get_db
from masala_common.outbound import Upstream
from masala_common.security import caller_for, need_identity, need_role

SERVICE = "orders"
caller = caller_for(SERVICE)

# Reglas del negocio (las mismas de la carta)
CODIGO_DESCUENTO = "MASALA20"
PORC_DESCUENTO = 20
COSTO_DELIVERY = 2000
DELIVERY_GRATIS_SOBRE = 20000
MINUTOS_PARA_PAGAR = 15
# Un pedido sin pagar se cancela solo, un minuto después de vencer el plazo (margen para un pago en curso)
MINUTOS_DE_GRACIA = 1
SEGUNDOS_ENTRE_BARRIDOS = int(os.getenv("BARRIDO_SEGUNDOS", "60"))
MAX_POR_BARRIDO = 200

log = logging.getLogger("masala")

# Máquina de estados: estado actual -> estados permitidos
TRANSICIONES = {
    "PENDIENTE_PAGO": {"PAGADO", "CANCELADO"},
    "PAGADO": {"EN_PREPARACION", "CANCELADO"},
    "EN_PREPARACION": {"LISTO"},
    "LISTO": {"ENTREGADO"},
    "ENTREGADO": set(),
    "CANCELADO": set(),
}
ESTADOS = tuple(TRANSICIONES)
Estado = Literal["PENDIENTE_PAGO", "PAGADO", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO"]


def db():
    return get_db("masala_orders")


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ItemIn(BaseModel):
    product_id: str = Field(min_length=1, max_length=40)
    cantidad: int = Field(ge=1, le=20)


class OrderIn(BaseModel):
    items: list[ItemIn] = Field(min_length=1, max_length=30)
    tipo: Literal["retiro", "delivery"]
    direccion: str | None = Field(default=None, max_length=200)
    codigo: str | None = Field(default=None, max_length=30)
    notas: str | None = Field(default=None, max_length=500)


class PayIn(BaseModel):
    metodo: Literal["tarjeta", "transferencia"]
    token: str | None = Field(default=None, max_length=60)


class StatusIn(BaseModel):
    estado: Estado


async def init():
    await db().orders.create_index([("user_id", 1), ("creado_en", -1)])
    await db().orders.create_index("estado")


_barrido = None


async def _ciclo_de_barrido():
    while True:
        await asyncio.sleep(SEGUNDOS_ENTRE_BARRIDOS)
        try:
            cancelados = await barrer_vencidos()
            if cancelados:
                log.info("barrido: %d pedidos vencidos cancelados y su stock liberado", cancelados)
        except Exception:
            # Un fallo puntual no detiene el barrido; se reintenta en el siguiente ciclo
            log.exception("barrido de pedidos vencidos falló")


async def arrancar():
    global _barrido
    await init()

    if SEGUNDOS_ENTRE_BARRIDOS > 0:
        _barrido = asyncio.create_task(_ciclo_de_barrido())


async def detener():
    if _barrido:
        _barrido.cancel()


app = create_app(SERVICE, "Orders - Masala", on_start=arrancar, on_stop=detener)


def vista(o, admin=False):
    data = {"id": o["_id"], "estado": o["estado"], "tipo": o["tipo"], "direccion": o.get("direccion"),
            "items": o["items"], "subtotal": o["subtotal"], "descuento": o["descuento"],
            "envio": o["envio"], "total": o["total"], "codigo": o.get("codigo"),
            "notas": o.get("notas"), "pago_ref": o.get("pago_ref"), "creado_en": o["creado_en"].isoformat() + "Z"}

    if admin:
        data["user_id"] = o["user_id"]

    return data


# Solo el dueño o un administrador ven el pedido; para los demás no existe
async def cargar(order_id, identity):
    o = await db().orders.find_one({"_id": order_id})

    if not o or (identity.rol != "admin" and o["user_id"] != identity.id):
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    return o


# Cambio de estado atómico: solo si sigue en el estado esperado
async def mover(order_id, desde, hacia, extra=None):
    if hacia not in TRANSICIONES[desde]:
        raise HTTPException(status_code=409, detail=f"Transición no permitida: {desde} -> {hacia}")

    cambios = {"estado": hacia, **(extra or {})}
    return await db().orders.find_one_and_update(
        {"_id": order_id, "estado": desde}, {"$set": cambios}, return_document=True
    )


async def liberar_stock(order_id, request_id):
    try:
        r = await Upstream(SERVICE, "inventory").request(
            "POST", f"/internal/reservations/{order_id}/release", request_id=request_id
        )
        if r.status_code in (200, 404):
            return True
    except HTTPException:
        pass

    # Queda registrado para reintentarlo en el siguiente barrido; el estado del pedido no se pierde
    await db().orders.update_one({"_id": order_id}, {"$set": {"stock_pendiente_liberar": True}})
    return False


# Cancela los pedidos que nadie pagó a tiempo y devuelve su stock; reintenta las liberaciones que fallaron
async def barrer_vencidos(request_id="barrido"):
    limite = ahora() - timedelta(minutes=MINUTOS_PARA_PAGAR + MINUTOS_DE_GRACIA)
    vencidos = await db().orders.find(
        {"estado": "PENDIENTE_PAGO", "creado_en": {"$lt": limite}}
    ).to_list(length=MAX_POR_BARRIDO)

    cancelados = 0
    for o in vencidos:
        # Atómico: si el cliente pagó justo ahora, el pedido ya no está pendiente y no se toca
        if await mover(o["_id"], "PENDIENTE_PAGO", "CANCELADO", {"motivo": "tiempo de pago vencido (automático)"}):
            await liberar_stock(o["_id"], request_id)
            cancelados += 1

    pendientes = await db().orders.find(
        {"estado": "CANCELADO", "stock_pendiente_liberar": True}
    ).to_list(length=MAX_POR_BARRIDO)

    for o in pendientes:
        if await liberar_stock(o["_id"], request_id):
            await db().orders.update_one({"_id": o["_id"]}, {"$unset": {"stock_pendiente_liberar": ""}})

    return cancelados


def calcular(productos, items, tipo, codigo):
    lineas = []
    for item in items:
        p = productos[item.product_id]
        lineas.append({"product_id": item.product_id, "nombre": p["nombre"], "categoria": p["categoria"],
                       "precio_unitario": p["precio"], "cantidad": item.cantidad,
                       "subtotal": p["precio"] * item.cantidad})

    subtotal = sum(linea["subtotal"] for linea in lineas)
    descuento = subtotal * PORC_DESCUENTO // 100 if codigo else 0
    neto = subtotal - descuento
    envio = COSTO_DELIVERY if tipo == "delivery" and neto <= DELIVERY_GRATIS_SOBRE else 0

    return lineas, subtotal, descuento, envio, neto + envio


# Crear pedido: reserva stock y calcula el total con los precios del servidor
@app.post("/", status_code=201)
async def create_order(body: OrderIn, c=Depends(caller), idempotency_key: str | None = Header(default=None),
                       x_request_id: str | None = Header(default=None)):
    identity = need_role(c, "cliente")

    codigo = None
    if body.codigo:
        if body.codigo.strip().upper() != CODIGO_DESCUENTO:
            raise HTTPException(status_code=400, detail="Código de descuento inválido")
        codigo = CODIGO_DESCUENTO

    direccion = (body.direccion or "").strip()
    if body.tipo == "delivery" and not direccion:
        raise HTTPException(status_code=400, detail="El delivery requiere dirección")

    if idempotency_key is not None and not (8 <= len(idempotency_key) <= 80):
        raise HTTPException(status_code=400, detail="Idempotency-Key inválida")

    # Mismo producto repetido: se suma
    juntos = {}
    for item in body.items:
        juntos[item.product_id] = juntos.get(item.product_id, 0) + item.cantidad
    if any(cantidad > 20 for cantidad in juntos.values()):
        raise HTTPException(status_code=400, detail="Máximo 20 unidades por producto")
    items = [ItemIn(product_id=pid, cantidad=cant) for pid, cant in juntos.items()]

    order_id = "ORD-" + secrets.token_hex(4).upper()

    # Reintento con la misma clave: devuelve el pedido original
    clave = None
    if idempotency_key:
        clave = f"{identity.id}:{idempotency_key}"
        try:
            await db().idempotency.insert_one({"_id": clave, "order_id": order_id, "creado_en": ahora()})
        except DuplicateKeyError:
            previo = await db().idempotency.find_one({"_id": clave})
            o = await db().orders.find_one({"_id": previo["order_id"]})
            if not o:
                raise HTTPException(status_code=409, detail="Solicitud en proceso, reintenta en un momento")
            return vista(o)

    async def abortar():
        if clave:
            await db().idempotency.delete_one({"_id": clave})

    # Reserva de stock; devuelve nombre y precio vigentes
    try:
        r = await Upstream(SERVICE, "inventory").request(
            "POST", "/internal/reservations", request_id=x_request_id,
            json={"order_id": order_id,
                  "items": [{"product_id": i.product_id, "cantidad": i.cantidad} for i in items]}
        )
    except HTTPException:
        await abortar()
        raise

    if r.status_code != 201:
        await abortar()
        if r.status_code in (404, 409):
            raise HTTPException(status_code=409, detail=r.json().get("detail"))
        raise HTTPException(status_code=502, detail="Inventario no disponible")

    productos = {p["product_id"]: p for p in r.json()["productos"]}
    lineas, subtotal, descuento, envio, total = calcular(productos, items, body.tipo, codigo)

    pedido = {"_id": order_id, "user_id": identity.id, "estado": "PENDIENTE_PAGO", "tipo": body.tipo,
              "direccion": direccion or None, "items": lineas, "subtotal": subtotal,
              "descuento": descuento, "envio": envio, "total": total, "codigo": codigo,
              "notas": (body.notas or "").strip() or None, "creado_en": ahora()}

    try:
        await db().orders.insert_one(pedido)
    except Exception:
        await liberar_stock(order_id, x_request_id)
        await abortar()
        raise HTTPException(status_code=500, detail="No fue posible crear el pedido")

    return vista(pedido)


# Pago: llama al servicio payments; si lo aprueban queda PAGADO
@app.post("/{order_id}/pay")
async def pay(order_id: str, body: PayIn, c=Depends(caller), x_request_id: str | None = Header(default=None)):
    identity = need_role(c, "cliente")
    o = await cargar(order_id, identity)

    # Repetir el pago de un pedido ya pagado no cobra de nuevo
    if o["estado"] == "PAGADO":
        return vista(o)
    if o["estado"] != "PENDIENTE_PAGO":
        raise HTTPException(status_code=409, detail=f"El pedido está {o['estado']} y no admite pago")

    if o["creado_en"] < ahora() - timedelta(minutes=MINUTOS_PARA_PAGAR):
        await mover(order_id, "PENDIENTE_PAGO", "CANCELADO", {"motivo": "tiempo de pago vencido"})
        await liberar_stock(order_id, x_request_id)
        raise HTTPException(status_code=409, detail="El tiempo para pagar venció; crea el pedido de nuevo")

    r = await Upstream(SERVICE, "payments").request(
        "POST", "/internal/charges", request_id=x_request_id,
        json={"order_id": order_id, "user_id": identity.id, "monto": o["total"],
              "metodo": body.metodo, "token": body.token}
    )

    if r.status_code == 400:
        raise HTTPException(status_code=400, detail=r.json().get("detail", "Datos de pago inválidos"))
    if r.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail="Servicio de pagos no disponible")

    pago = r.json()

    if pago["estado"] == "RECHAZADO":
        await mover(order_id, "PENDIENTE_PAGO", "CANCELADO", {"motivo": "pago rechazado", "pago_ref": pago["ref"]})
        await liberar_stock(order_id, x_request_id)
        raise HTTPException(status_code=402, detail="Pago rechazado; el pedido fue cancelado")

    actualizado = await mover(order_id, "PENDIENTE_PAGO", "PAGADO", {"pago_ref": pago["ref"], "pagado_en": ahora()})
    if not actualizado:
        # El pedido se canceló mientras se cobraba: se devuelve el cobro para no dejarlo pagado sin pedido
        await Upstream(SERVICE, "payments").request(
            "POST", f"/internal/charges/{order_id}/refund", request_id=x_request_id
        )
        raise HTTPException(status_code=409, detail="El pedido se canceló mientras se pagaba; el cobro fue devuelto")

    return vista(actualizado)


# Cancelar: el cliente solo antes de preparar; reembolsa si ya estaba pagado
@app.post("/{order_id}/cancel")
async def cancel(order_id: str, c=Depends(caller), x_request_id: str | None = Header(default=None)):
    identity = need_identity(c)
    o = await cargar(order_id, identity)

    if o["estado"] == "CANCELADO":
        return vista(o)
    if "CANCELADO" not in TRANSICIONES[o["estado"]]:
        raise HTTPException(status_code=409, detail=f"No se puede cancelar un pedido {o['estado']}")

    if o["estado"] == "PAGADO":
        r = await Upstream(SERVICE, "payments").request(
            "POST", f"/internal/charges/{order_id}/refund", request_id=x_request_id
        )
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="No fue posible reembolsar el pago")

    actualizado = await mover(order_id, o["estado"], "CANCELADO", {"motivo": f"cancelado por {identity.rol}"})
    if not actualizado:
        raise HTTPException(status_code=409, detail="El pedido cambió de estado, reintenta")

    await liberar_stock(order_id, x_request_id)
    return vista(actualizado)


# Avance de estado de cocina (administrador)
@app.patch("/{order_id}/status")
async def change_status(order_id: str, body: StatusIn, c=Depends(caller)):
    identity = need_role(c, "admin")
    o = await cargar(order_id, identity)

    if body.estado == "CANCELADO":
        raise HTTPException(status_code=400, detail="Para cancelar usa /cancel")

    actualizado = await mover(order_id, o["estado"], body.estado)
    if not actualizado:
        raise HTTPException(status_code=409, detail="El pedido cambió de estado, reintenta")

    return vista(actualizado, True)


# Mis pedidos; el administrador ve todos
@app.get("/")
async def list_orders(c=Depends(caller), estado: str | None = Query(default=None, max_length=20),
                      limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    identity = need_identity(c)

    if estado and estado not in ESTADOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    filtro = {} if identity.rol == "admin" else {"user_id": identity.id}
    if estado:
        filtro["estado"] = estado

    admin = identity.rol == "admin"
    docs = await db().orders.find(filtro).sort("creado_en", -1).skip(offset).limit(limit).to_list(length=limit)
    return {"orders": [vista(o, admin) for o in docs]}


# Detalle
@app.get("/{order_id}")
async def get_order(order_id: str, c=Depends(caller)):
    identity = need_identity(c)
    return vista(await cargar(order_id, identity), identity.rol == "admin")
