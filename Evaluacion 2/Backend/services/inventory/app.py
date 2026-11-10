from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from masala_common.app import create_app
from masala_common.db import get_db
from masala_common.security import caller_for, need_role, need_service

SERVICE = "inventory"
caller = caller_for(SERVICE)

CATEGORIAS = ("entradas", "platos", "bebestibles", "extras")
Categoria = Literal["entradas", "platos", "bebestibles", "extras"]


def db():
    return get_db("masala_inventory")


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProductReplace(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    categoria: Categoria
    precio: int = Field(ge=0, le=1_000_000)
    descripcion: str = Field(default="", max_length=300)
    imagen: str = Field(default="", max_length=120)
    stock: int = Field(ge=0, le=10_000)
    activo: bool = True


class ProductIn(ProductReplace):
    id: str = Field(pattern=r"^[a-z0-9-]{3,40}$")


class ProductPatch(BaseModel):
    precio: int | None = Field(default=None, ge=0, le=1_000_000)
    stock: int | None = Field(default=None, ge=0, le=10_000)
    activo: bool | None = None
    descripcion: str | None = Field(default=None, max_length=300)


class ReservaItem(BaseModel):
    product_id: str = Field(min_length=1, max_length=40)
    cantidad: int = Field(ge=1, le=200)


class ReservaIn(BaseModel):
    order_id: str = Field(min_length=3, max_length=20)
    items: list[ReservaItem] = Field(min_length=1, max_length=60)


# Carta inicial (la del frontend)
SEMILLA = [
    ("samosas-vegetales", "Samosas Vegetales", "entradas", 4000, "Empanadillas crujientes rellenas de verduras especiadas.", "img/pollito.jpg", 40),
    ("chicken-tikka-masala", "Chicken Tikka Masala", "platos", 9500, "Pollo marinado en salsa cremosa de tomate y especias.", "img/plato1.jpg", 40),
    ("pan-naan-ajo", "Pan Naan al Ajo", "platos", 2500, "Pan horneado al tandoor con mantequilla de ajo.", "img/naan.jpg", 60),
    ("limonada-menta-jengibre", "Limonada Menta Jengibre", "bebestibles", 3000, "Limonada natural con menta y jengibre.", "img/limona3.jpg", 50),
    ("bebida-lata-350", "Bebida Lata 350ml", "bebestibles", 2100, "Bebida en lata de 350 ml.", "img/lata.jpg", 100),
    ("naan-extra", "Pan Naan Extra", "extras", 2000, "Porción adicional de pan naan.", "img/naan.jpg", 60),
]


async def init():
    await db().reservations.create_index("estado")

    if await db().products.count_documents({}) == 0:
        await db().products.insert_many([
            {"_id": i, "nombre": n, "categoria": c, "precio": p, "descripcion": d,
             "imagen": img, "stock": s, "activo": True, "creado_en": ahora()}
            for i, n, c, p, d, img, s in SEMILLA
        ])


app = create_app(SERVICE, "Inventory - Masala", on_start=init)


# El público no ve el stock exacto, solo si hay disponibilidad
def vista(p, admin=False):
    data = {"id": p["_id"], "nombre": p["nombre"], "categoria": p["categoria"],
            "precio": p["precio"], "descripcion": p.get("descripcion", ""),
            "imagen": p.get("imagen", ""), "disponible": bool(p["activo"] and p["stock"] > 0)}

    if admin:
        data["stock"] = p["stock"]
        data["activo"] = p["activo"]

    return data


def es_admin(c):
    return c.identity is not None and c.identity.rol == "admin"


# Catálogo con filtros (categoria, available, ids)
@app.get("/products")
async def list_products(c=Depends(caller), categoria: str | None = Query(default=None, max_length=20),
                        available: str | None = Query(default=None, max_length=5),
                        ids: str | None = Query(default=None, max_length=1000)):
    if categoria and categoria not in CATEGORIAS:
        raise HTTPException(status_code=400, detail="Categoría inválida")
    if available not in (None, "true", "false"):
        raise HTTPException(status_code=400, detail="available debe ser true o false")

    admin = es_admin(c)
    filtro = {}
    if not admin:
        filtro["activo"] = True
    if categoria:
        filtro["categoria"] = categoria
    if ids:
        filtro["_id"] = {"$in": [i for i in ids.split(",") if i][:50]}

    docs = await db().products.find(filtro).sort([("categoria", 1), ("nombre", 1)]).to_list(length=200)
    data = [vista(p, admin) for p in docs]

    if available == "true":
        data = [p for p in data if p["disponible"]]
    elif available == "false":
        data = [p for p in data if not p["disponible"]]

    return {"products": data}


# Un producto
@app.get("/products/{product_id}")
async def get_product(product_id: str, c=Depends(caller)):
    p = await db().products.find_one({"_id": product_id})
    admin = es_admin(c)

    if not p or (not p["activo"] and not admin):
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return vista(p, admin)


# Crear (administrador)
@app.post("/products", status_code=201)
async def create_product(body: ProductIn, c=Depends(caller)):
    need_role(c, "admin")
    doc = body.model_dump(exclude={"id"})
    doc.update({"_id": body.id, "creado_en": ahora()})

    try:
        await db().products.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Ya existe un producto con ese id")

    return vista(doc, True)


# Reemplazar (administrador)
@app.put("/products/{product_id}")
async def replace_product(product_id: str, body: ProductReplace, c=Depends(caller)):
    need_role(c, "admin")
    result = await db().products.update_one({"_id": product_id}, {"$set": body.model_dump()})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return vista(await db().products.find_one({"_id": product_id}), True)


# Cambio parcial: precio, stock o activo (administrador)
@app.patch("/products/{product_id}")
async def patch_product(product_id: str, body: ProductPatch, c=Depends(caller)):
    need_role(c, "admin")
    cambios = body.model_dump(exclude_none=True)

    if not cambios:
        raise HTTPException(status_code=400, detail="Sin cambios")

    result = await db().products.update_one({"_id": product_id}, {"$set": cambios})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return vista(await db().products.find_one({"_id": product_id}), True)


# Retirar de la carta: no se borra, queda inactivo para conservar el historial
@app.delete("/products/{product_id}")
async def delete_product(product_id: str, c=Depends(caller)):
    need_role(c, "admin")
    result = await db().products.update_one({"_id": product_id}, {"$set": {"activo": False}})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"id": product_id, "activo": False}


# Reserva de stock para un pedido (idempotente por order_id)
@app.post("/internal/reservations", status_code=201)
async def reserve(body: ReservaIn, c=Depends(caller)):
    need_service(c, "orders")

    existente = await db().reservations.find_one({"_id": body.order_id})
    if existente:
        if existente["estado"] != "RESERVADA":
            raise HTTPException(status_code=409, detail="La reserva ya fue liberada")
        return {"productos": existente["productos"]}

    # Cantidad total por producto
    necesarios = {}
    for item in body.items:
        necesarios[item.product_id] = necesarios.get(item.product_id, 0) + item.cantidad

    productos = {}
    for pid in necesarios:
        p = await db().products.find_one({"_id": pid})
        if not p or not p["activo"]:
            raise HTTPException(status_code=404, detail={"code": "PRODUCTO_NO_DISPONIBLE", "product_id": pid})
        productos[pid] = p

    # Descuento atómico: solo si alcanza el stock
    reservados = []
    for pid, cantidad in necesarios.items():
        result = await db().products.update_one(
            {"_id": pid, "activo": True, "stock": {"$gte": cantidad}},
            {"$inc": {"stock": -cantidad}}
        )

        if result.modified_count == 0:
            for rid, rcant in reservados:
                await db().products.update_one({"_id": rid}, {"$inc": {"stock": rcant}})
            raise HTTPException(status_code=409, detail={"code": "STOCK_INSUFICIENTE", "product_id": pid})

        reservados.append((pid, cantidad))

    snapshot = [{"product_id": pid, "nombre": p["nombre"], "categoria": p["categoria"], "precio": p["precio"]}
                for pid, p in productos.items()]

    await db().reservations.insert_one({
        "_id": body.order_id, "estado": "RESERVADA", "items": necesarios,
        "productos": snapshot, "creado_en": ahora()
    })

    return {"productos": snapshot}


# Libera el stock (pago fallido o pedido anulado); repetirlo no devuelve stock dos veces
@app.post("/internal/reservations/{order_id}/release")
async def release(order_id: str, c=Depends(caller)):
    need_service(c, "orders")

    reserva = await db().reservations.find_one_and_update(
        {"_id": order_id, "estado": "RESERVADA"}, {"$set": {"estado": "LIBERADA"}}
    )

    if reserva:
        for pid, cantidad in reserva["items"].items():
            await db().products.update_one({"_id": pid}, {"$inc": {"stock": cantidad}})
        return {"estado": "LIBERADA"}

    existente = await db().reservations.find_one({"_id": order_id})
    if not existente:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    return {"estado": existente["estado"]}
