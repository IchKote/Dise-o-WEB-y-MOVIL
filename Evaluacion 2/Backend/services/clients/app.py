import re
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field

from masala_common.app import create_app
from masala_common.db import get_db
from masala_common.security import caller_for, need_identity, need_role, need_service

SERVICE = "clients"
caller = caller_for(SERVICE)

TEL_RE = re.compile(r"^\+?[0-9 ]{8,15}$")


def db():
    return get_db("masala_clients")


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class InternalClientIn(BaseModel):
    user_id: str = Field(min_length=3, max_length=40)
    nombre: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=120)


class ProfileIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    telefono: str | None = Field(default=None, max_length=20)
    direcciones: list[str] = Field(default=[], max_length=5)


# Datos de prueba (los mismos usuarios de auth)
async def init():
    if await db().clients.count_documents({}) == 0:
        await db().clients.insert_many([
            {"_id": "u-admin", "nombre": "Administrador Masala", "email": "admin@masala.cl",
             "telefono": None, "direcciones": [], "creado_en": ahora()},
            {"_id": "u-cliente", "nombre": "Daniela Jara", "email": "cliente@masala.cl",
             "telefono": "+56 9 1111 2222", "direcciones": ["Av. Providencia 123"], "creado_en": ahora()},
        ])


app = create_app(SERVICE, "Clients - Masala", on_start=init)


# Teléfono y direcciones son datos personales: solo dueño o administrador
def vista(c):
    return {"id": c["_id"], "nombre": c["nombre"], "email": c["email"],
            "telefono": c.get("telefono"), "direcciones": c.get("direcciones", [])}


# Perfil inicial creado por auth (idempotente)
@app.post("/internal/clients", status_code=201)
async def create_client(body: InternalClientIn, c=Depends(caller)):
    need_service(c, "auth")

    await db().clients.update_one(
        {"_id": body.user_id},
        {"$setOnInsert": {"nombre": body.nombre, "email": body.email, "telefono": None,
                          "direcciones": [], "creado_en": ahora()}},
        upsert=True
    )
    return {"id": body.user_id}


# Mi perfil
@app.get("/me")
async def my_profile(c=Depends(caller)):
    identity = need_identity(c)
    client = await db().clients.find_one({"_id": identity.id})

    if not client:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    return vista(client)


# Reemplaza los datos editables de mi perfil
@app.put("/me")
async def update_profile(body: ProfileIn, c=Depends(caller)):
    identity = need_identity(c)

    if re.search(r"[<>]", body.nombre) or any(re.search(r"[<>]", d) for d in body.direcciones):
        raise HTTPException(status_code=400, detail="Caracteres no permitidos")

    if body.telefono and not TEL_RE.match(body.telefono):
        raise HTTPException(status_code=400, detail="Teléfono inválido")

    if any(not d.strip() or len(d) > 200 for d in body.direcciones):
        raise HTTPException(status_code=400, detail="Dirección inválida")

    result = await db().clients.update_one(
        {"_id": identity.id},
        {"$set": {"nombre": body.nombre.strip(), "telefono": body.telefono,
                  "direcciones": [d.strip() for d in body.direcciones]}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    return vista(await db().clients.find_one({"_id": identity.id}))


# Listado (administrador); ids permite consultar varios a la vez
@app.get("/")
async def list_clients(c=Depends(caller), limit: int = Query(20, ge=1, le=100),
                       offset: int = Query(0, ge=0), ids: str | None = Query(default=None, max_length=1000)):
    need_role(c, "admin")

    filtro = {}
    if ids:
        lista = [i for i in ids.split(",") if i][:50]
        filtro = {"_id": {"$in": lista}}

    docs = await db().clients.find(filtro).sort("nombre", 1).skip(offset).limit(limit).to_list(length=limit)
    return {"clients": [vista(d) for d in docs]}


# Un cliente (administrador)
@app.get("/{user_id}")
async def get_client(user_id: str, c=Depends(caller)):
    need_role(c, "admin")
    client = await db().clients.find_one({"_id": user_id})

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return vista(client)
