import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from masala_common import secrets_store
from masala_common.app import create_app
from masala_common.db import get_db
from masala_common.security import caller_for, need_identity, need_service

SERVICE = "payments"
caller = caller_for(SERVICE)

# Tarjeta de prueba que el sandbox rechaza
TOKEN_RECHAZADO = "tok_rechazada"


def db():
    return get_db("masala_payments")


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ChargeIn(BaseModel):
    order_id: str = Field(min_length=3, max_length=20)
    user_id: str = Field(min_length=3, max_length=40)
    monto: int = Field(gt=0, le=5_000_000)
    metodo: Literal["tarjeta", "transferencia"]
    token: str | None = Field(default=None, max_length=60)


async def init():
    await db().payments.create_index("user_id")


app = create_app(SERVICE, "Payments - Masala", on_start=init)


# Comprobante firmado con la clave guardada en el gestor de secretos
def firmar(order_id, monto, estado, ref):
    key = secrets_store.get_secrets(SERVICE).get("signing_key", "")
    msg = f"{order_id}|{monto}|{estado}|{ref}".encode()
    return hmac.new(key.encode(), msg, hashlib.sha256).hexdigest()


# Nunca se guarda ni se devuelve el token de tarjeta
def vista(p):
    return {"order_id": p["_id"], "monto": p["monto"], "metodo": p["metodo"],
            "estado": p["estado"], "ref": p["ref"], "firma": p["firma"],
            "creado_en": p["creado_en"].isoformat() + "Z"}


# Cobro en sandbox (idempotente por order_id)
@app.post("/internal/charges", status_code=201)
async def charge(body: ChargeIn, c=Depends(caller)):
    need_service(c, "orders")

    existente = await db().payments.find_one({"_id": body.order_id})
    if existente:
        if existente["monto"] != body.monto or existente["user_id"] != body.user_id:
            raise HTTPException(status_code=409, detail="Ya existe un cobro distinto para este pedido")
        return vista(existente)

    if body.metodo == "tarjeta" and not body.token:
        raise HTTPException(status_code=400, detail="Falta el token de la tarjeta")

    estado = "RECHAZADO" if body.token == TOKEN_RECHAZADO else "APROBADO"
    ref = "pay_" + secrets.token_hex(6)

    pago = {"_id": body.order_id, "user_id": body.user_id, "monto": body.monto,
            "metodo": body.metodo, "estado": estado, "ref": ref,
            "firma": firmar(body.order_id, body.monto, estado, ref), "creado_en": ahora()}

    try:
        await db().payments.insert_one(pago)
    except DuplicateKeyError:
        pago = await db().payments.find_one({"_id": body.order_id})

    return vista(pago)


# Reembolso (idempotente)
@app.post("/internal/charges/{order_id}/refund")
async def refund(order_id: str, c=Depends(caller)):
    need_service(c, "orders")

    pago = await db().payments.find_one({"_id": order_id})
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    if pago["estado"] == "APROBADO":
        firma = firmar(order_id, pago["monto"], "REEMBOLSADO", pago["ref"])
        await db().payments.update_one(
            {"_id": order_id, "estado": "APROBADO"},
            {"$set": {"estado": "REEMBOLSADO", "firma": firma}}
        )
        pago = await db().payments.find_one({"_id": order_id})

    if pago["estado"] != "REEMBOLSADO":
        raise HTTPException(status_code=409, detail="El pago no se puede reembolsar")

    return vista(pago)


# Comprobante de un pedido: dueño o administrador
@app.get("/{order_id}")
async def get_payment(order_id: str, c=Depends(caller)):
    identity = need_identity(c)
    pago = await db().payments.find_one({"_id": order_id})

    if not pago or (identity.rol != "admin" and pago["user_id"] != identity.id):
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    return vista(pago)


# Listado: el cliente solo ve sus pagos, el administrador todos; ids filtra por pedido
@app.get("/")
async def list_payments(c=Depends(caller), limit: int = Query(20, ge=1, le=100),
                        offset: int = Query(0, ge=0), ids: str | None = Query(default=None, max_length=1000)):
    identity = need_identity(c)

    filtro = {}
    if identity.rol != "admin":
        filtro["user_id"] = identity.id
    if ids:
        filtro["_id"] = {"$in": [i for i in ids.split(",") if i][:50]}

    docs = await db().payments.find(filtro).sort("creado_en", -1).skip(offset).limit(limit).to_list(length=limit)
    return {"payments": [vista(p) for p in docs]}
