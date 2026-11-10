import httpx
import pytest

from masala_common import outbound
from tests.helpers import login

BASE = {"items": [{"product_id": "chicken-tikka-masala", "cantidad": 2}, {"product_id": "samosas-vegetales", "cantidad": 1}],
        "tipo": "retiro"}


async def crear(api, cab, **cambios):
    return await api.post("/api/orders", json=BASE | cambios, headers=cab)


async def stock(api, admin, pid="chicken-tikka-masala"):
    return (await api.get(f"/api/products/{pid}", headers=admin)).json()["stock"]


@pytest.fixture
async def otro(api):
    await api.post("/api/auth/register", json={"nombre": "Otro Cliente", "email": "otro@correo.cl", "password": "clave12345"})
    return await login(api, "otro@correo.cl", "clave12345")


async def test_total_lo_calcula_el_servidor(api, cliente):
    r = await crear(api, cliente, total=1, subtotal=1, precio=1)
    o = r.json()
    assert r.status_code == 201
    assert (o["subtotal"], o["descuento"], o["envio"], o["total"]) == (23000, 0, 0, 23000)
    assert o["estado"] == "PENDIENTE_PAGO"
    assert o["items"][0]["precio_unitario"] == 9500


async def test_precio_manipulado_en_item(api, cliente):
    items = [{"product_id": "chicken-tikka-masala", "cantidad": 1, "precio_unitario": 1, "precio": 1}]
    assert (await crear(api, cliente, items=items)).json()["total"] == 9500


async def test_descuento_y_delivery(api, cliente):
    o = (await crear(api, cliente, tipo="delivery", direccion="Av. Providencia 123", codigo="masala20")).json()
    assert (o["subtotal"], o["descuento"], o["envio"], o["total"]) == (23000, 4600, 2000, 20400)

    chico = {"items": [{"product_id": "bebida-lata-350", "cantidad": 1}]}
    o = (await crear(api, cliente, tipo="delivery", direccion="Calle 1", **chico)).json()
    assert (o["envio"], o["total"]) == (2000, 4100)

    o = (await crear(api, cliente, tipo="delivery", direccion="Calle 1")).json()
    assert (o["envio"], o["total"]) == (0, 23000)


async def test_validaciones(api, cliente):
    assert (await crear(api, cliente, tipo="delivery")).status_code == 400
    assert (await crear(api, cliente, codigo="OTRO")).status_code == 400
    assert (await crear(api, cliente, items=[])).status_code == 400
    assert (await crear(api, cliente, tipo="volando")).status_code == 400
    assert (await crear(api, cliente, items=[{"product_id": "samosas-vegetales", "cantidad": 0}])).status_code == 400
    assert (await crear(api, cliente, items=[{"product_id": "samosas-vegetales", "cantidad": 21}])).status_code == 400
    assert (await crear(api, cliente, items=[{"product_id": "no-existe", "cantidad": 1}])).status_code == 409


async def test_admin_no_crea_pedidos_y_sin_token(api, admin):
    assert (await crear(api, admin)).status_code == 403
    assert (await api.post("/api/orders", json=BASE)).status_code == 401


async def test_stock_se_reserva_y_se_agota(api, cliente, admin):
    assert await stock(api, admin) == 40
    for _ in range(2):
        assert (await crear(api, cliente, items=[{"product_id": "chicken-tikka-masala", "cantidad": 20}])).status_code == 201
    assert await stock(api, admin) == 0

    r = await crear(api, cliente, items=[{"product_id": "chicken-tikka-masala", "cantidad": 1}])
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "STOCK_INSUFICIENTE"

    disponible = (await api.get("/api/products/chicken-tikka-masala")).json()["disponible"]
    assert disponible is False


async def test_stock_parcial_se_revierte(api, cliente, admin):
    await api.patch("/api/products/samosas-vegetales", json={"stock": 1}, headers=admin)
    items = [{"product_id": "chicken-tikka-masala", "cantidad": 3}, {"product_id": "samosas-vegetales", "cantidad": 5}]
    assert (await crear(api, cliente, items=items)).status_code == 409
    assert await stock(api, admin) == 40


async def test_idempotencia_al_crear(api, cliente, admin):
    cab = cliente | {"Idempotency-Key": "clave-unica-123"}
    a = await api.post("/api/orders", json=BASE, headers=cab)
    b = await api.post("/api/orders", json=BASE, headers=cab)
    assert a.status_code == 201 and b.status_code == 201
    assert a.json()["id"] == b.json()["id"]
    assert await stock(api, admin) == 38


async def test_pago_aprobado_y_repetido(api, cliente):
    o = (await crear(api, cliente)).json()
    pago = {"metodo": "tarjeta", "token": "tok_visa_prueba"}
    a = await api.post(f"/api/orders/{o['id']}/pay", json=pago, headers=cliente)
    b = await api.post(f"/api/orders/{o['id']}/pay", json=pago, headers=cliente)
    assert a.status_code == b.status_code == 200
    assert a.json()["estado"] == "PAGADO"
    assert a.json()["pago_ref"] == b.json()["pago_ref"]

    comprobante = (await api.get(f"/api/payments/{o['id']}", headers=cliente)).json()
    assert comprobante["estado"] == "APROBADO" and comprobante["monto"] == 23000
    assert len(comprobante["firma"]) == 64
    assert "tok_visa" not in str(comprobante)


async def test_pago_rechazado_libera_stock(api, cliente, admin):
    o = (await crear(api, cliente)).json()
    assert await stock(api, admin) == 38
    r = await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "tarjeta", "token": "tok_rechazada"}, headers=cliente)
    assert r.status_code == 402
    assert (await api.get(f"/api/orders/{o['id']}", headers=cliente)).json()["estado"] == "CANCELADO"
    assert await stock(api, admin) == 40


async def test_pago_validaciones(api, cliente):
    o = (await crear(api, cliente)).json()
    assert (await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "tarjeta"}, headers=cliente)).status_code == 400
    assert (await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "bitcoin"}, headers=cliente)).status_code == 400


async def test_cancelar_pagado_reembolsa_y_repone(api, cliente, admin):
    o = (await crear(api, cliente)).json()
    await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "transferencia"}, headers=cliente)
    r = await api.post(f"/api/orders/{o['id']}/cancel", headers=cliente)
    assert r.json()["estado"] == "CANCELADO"
    assert await stock(api, admin) == 40
    assert (await api.get(f"/api/payments/{o['id']}", headers=cliente)).json()["estado"] == "REEMBOLSADO"

    again = await api.post(f"/api/orders/{o['id']}/cancel", headers=cliente)
    assert again.status_code == 200 and await stock(api, admin) == 40


async def test_estados_de_cocina(api, cliente, admin):
    o = (await crear(api, cliente)).json()
    ruta = f"/api/orders/{o['id']}/status"

    assert (await api.patch(ruta, json={"estado": "EN_PREPARACION"}, headers=admin)).status_code == 409
    await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "transferencia"}, headers=cliente)
    assert (await api.patch(ruta, json={"estado": "LISTO"}, headers=admin)).status_code == 409

    for estado in ("EN_PREPARACION", "LISTO", "ENTREGADO"):
        r = await api.patch(ruta, json={"estado": estado}, headers=admin)
        assert r.status_code == 200 and r.json()["estado"] == estado

    assert (await api.patch(ruta, json={"estado": "PAGADO"}, headers=admin)).status_code == 409
    assert (await api.post(f"/api/orders/{o['id']}/cancel", headers=cliente)).status_code == 409
    assert (await api.patch(ruta, json={"estado": "CANCELADO"}, headers=admin)).status_code == 400
    assert (await api.patch(ruta, json={"estado": "INVENTADO"}, headers=admin)).status_code == 400


async def test_cliente_no_cambia_estados(api, cliente):
    o = (await crear(api, cliente)).json()
    r = await api.patch(f"/api/orders/{o['id']}/status", json={"estado": "ENTREGADO"}, headers=cliente)
    assert r.status_code == 403


async def test_pedidos_ajenos_no_existen(api, cliente, otro, admin):
    o = (await crear(api, cliente)).json()
    i = o["id"]
    assert (await api.get(f"/api/orders/{i}", headers=otro)).status_code == 404
    assert (await api.post(f"/api/orders/{i}/pay", json={"metodo": "transferencia"}, headers=otro)).status_code == 404
    assert (await api.post(f"/api/orders/{i}/cancel", headers=otro)).status_code == 404
    assert (await api.get(f"/api/payments/{i}", headers=otro)).status_code == 404
    assert (await api.get("/api/orders", headers=otro)).json()["orders"] == []
    assert (await api.get(f"/api/orders/{i}", headers=admin)).status_code == 200
    assert (await api.get("/api/orders/ORD-FFFFFFFF", headers=cliente)).status_code == 404


async def test_listados_y_filtros(api, cliente, otro, admin):
    await crear(api, cliente)
    o = (await crear(api, cliente)).json()
    await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "transferencia"}, headers=cliente)

    assert len((await api.get("/api/orders", headers=cliente)).json()["orders"]) == 2
    pagados = (await api.get("/api/orders", params={"estado": "PAGADO"}, headers=admin)).json()["orders"]
    assert len(pagados) == 1 and "user_id" in pagados[0]
    assert (await api.get("/api/orders", params={"estado": "X"}, headers=admin)).status_code == 400
    assert (await api.get("/api/orders", params={"limit": 1000}, headers=admin)).status_code == 400
    assert "user_id" not in (await api.get("/api/orders", headers=cliente)).json()["orders"][0]
    assert len((await api.get("/api/payments", headers=cliente)).json()["payments"]) == 1
    assert (await api.get("/api/payments", headers=otro)).json()["payments"] == []
    assert len((await api.get("/api/payments", headers=admin)).json()["payments"]) == 1


async def test_clientes_datos_personales(api, cliente, otro, admin):
    r = await api.put("/api/clients/me", json={"nombre": "Daniela J.", "telefono": "+56 9 1234 5678",
                                                "direcciones": ["Calle 1"]}, headers=cliente)
    assert r.status_code == 200
    assert (await api.put("/api/clients/me", json={"nombre": "Dani", "telefono": "abc"}, headers=cliente)).status_code == 400
    assert (await api.get("/api/clients", headers=cliente)).status_code == 403
    assert (await api.get("/api/clients/u-cliente", headers=otro)).status_code == 403
    assert (await api.get("/api/clients/u-cliente", headers=admin)).json()["telefono"] == "+56 9 1234 5678"
    assert (await api.get("/api/clients/me", headers=otro)).json()["email"] == "otro@correo.cl"


class Lento(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request):
        raise httpx.ReadTimeout("lento", request=request)


async def test_servicio_caido_da_502(api, cliente):
    outbound.TRANSPORTS.pop("inventory")
    r = await crear(api, cliente)
    assert r.status_code == 502
    assert "inventory" in r.json()["detail"] and "Traceback" not in r.text and "http://" not in r.text


async def test_servicio_lento_da_504(api, cliente):
    outbound.TRANSPORTS["inventory"] = Lento()
    assert (await crear(api, cliente)).status_code == 504


async def test_pago_con_servicio_de_pagos_caido_mantiene_pedido(api, cliente):
    o = (await crear(api, cliente)).json()
    guardado = outbound.TRANSPORTS.pop("payments")
    assert (await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "transferencia"}, headers=cliente)).status_code == 502
    assert (await api.get(f"/api/orders/{o['id']}", headers=cliente)).json()["estado"] == "PENDIENTE_PAGO"

    outbound.TRANSPORTS["payments"] = guardado
    assert (await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "transferencia"}, headers=cliente)).json()["estado"] == "PAGADO"


async def test_notas_del_pedido(api, cliente):
    o = (await crear(api, cliente, notas="  Sin picante  ")).json()
    assert o["notas"] == "Sin picante"
    assert (await crear(api, cliente, notas="x" * 501)).status_code == 400


# --- Liberación automática de reservas abandonadas (B7) ---

async def envejecer(order_id, minutos):
    from datetime import timedelta
    from services.orders import app as orders
    await orders.db().orders.update_one({"_id": order_id}, {"$set": {"creado_en": orders.ahora() - timedelta(minutes=minutos)}})


async def test_barrido_cancela_pedido_sin_pagar_y_libera_stock(api, cliente, admin):
    from services.orders import app as orders
    o = (await crear(api, cliente)).json()
    assert await stock(api, admin) == 38
    await envejecer(o["id"], 20)

    assert await orders.barrer_vencidos() == 1

    visto = (await api.get(f"/api/orders/{o['id']}", headers=cliente)).json()
    assert visto["estado"] == "CANCELADO"
    assert await stock(api, admin) == 40
    # Repetir el barrido no devuelve el stock dos veces
    assert await orders.barrer_vencidos() == 0
    assert await stock(api, admin) == 40
    # Un pedido cancelado ya no admite pago
    r = await api.post(f"/api/orders/{o['id']}/pay", json={"metodo": "tarjeta", "token": "tok_sandbox"}, headers=cliente)
    assert r.status_code == 409


async def test_barrido_respeta_pedidos_recientes_y_pagados(api, cliente, admin):
    from services.orders import app as orders
    reciente = (await crear(api, cliente, items=[{"product_id": "samosas-vegetales", "cantidad": 1}])).json()
    pagado = (await crear(api, cliente)).json()
    r = await api.post(f"/api/orders/{pagado['id']}/pay", json={"metodo": "tarjeta", "token": "tok_sandbox"}, headers=cliente)
    assert r.status_code == 200
    await envejecer(pagado["id"], 60)
    await envejecer(reciente["id"], 14)

    assert await orders.barrer_vencidos() == 0

    estados = {x["id"]: x["estado"] for x in (await api.get("/api/orders", headers=cliente)).json()["orders"]}
    assert estados[reciente["id"]] == "PENDIENTE_PAGO" and estados[pagado["id"]] == "PAGADO"


async def test_barrido_reintenta_liberaciones_pendientes(api, cliente, admin):
    from services.orders import app as orders
    o = (await crear(api, cliente)).json()
    assert await stock(api, admin) == 38
    # Simula una cancelación cuyo aviso a inventario falló
    await orders.db().orders.update_one({"_id": o["id"]}, {"$set": {"estado": "CANCELADO", "stock_pendiente_liberar": True}})

    await orders.barrer_vencidos()

    assert await stock(api, admin) == 40
    assert "stock_pendiente_liberar" not in await orders.db().orders.find_one({"_id": o["id"]})
