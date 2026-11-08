from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="FastAPI 2 - Masala",
    description="Backend 2 (puerto 9100): la misma API en español. Se publica a través del API Gateway"
)

# Productos
PRODUCTOS = [
    {"id": "p01", "categoria": "platos", "nombre": "Chicken Tikka Masala", "precio": 9500, "disponible": True},
    {"id": "p02", "categoria": "entradas", "nombre": "Pan Naan al Ajo", "precio": 2500, "disponible": True},
    {"id": "p03", "categoria": "entradas", "nombre": "Samosas Vegetales", "precio": 4000, "disponible": True},
    {"id": "p04", "categoria": "bebestibles", "nombre": "Bebida Lata 350ml", "precio": 2100, "disponible": True},
    {"id": "p05", "categoria": "bebestibles", "nombre": "Limonada Menta Jengibre", "precio": 3000, "disponible": True},
    {"id": "p06", "categoria": "extras", "nombre": "Pan Naan Extra", "precio": 2000, "disponible": True}
]

# Pedidos
PEDIDOS = [
    {"id": "M-1001", "cliente": "cliente@masala.cl", "sucursal": "Sucursal Central",
     "lineas": [{"nombre": "Chicken Tikka Masala", "cantidad": 2, "precio": 9500},
                {"nombre": "Pan Naan al Ajo", "cantidad": 2, "precio": 2500}],
     "entrega": "Retiro en local", "total": 24000, "estado": "En preparación"},
    {"id": "M-1002", "cliente": "cliente@masala.cl", "sucursal": "Sucursal Ñuñoa",
     "lineas": [{"nombre": "Samosas Vegetales", "cantidad": 1, "precio": 4000},
                {"nombre": "Limonada Menta Jengibre", "cantidad": 2, "precio": 3000}],
     "entrega": "Delivery", "total": 12000, "estado": "En camino"},
    {"id": "M-1003", "cliente": "ana@correo.cl", "sucursal": "Sucursal Central",
     "lineas": [{"nombre": "Chicken Tikka Masala", "cantidad": 1, "precio": 9500},
                {"nombre": "Bebida Lata 350ml", "cantidad": 1, "precio": 2100}],
     "entrega": "Retiro en local", "total": 11600, "estado": "Entregado"}
]


# Salud
@app.get("/health")
def health():
    return {"status": "OK", "service": "FastAPI 2"}


# Listar productos (filtro opcional por categoría)
@app.get("/productos")
def productos(categoria: str | None = None):
    if categoria:
        return {"productos": [p for p in PRODUCTOS if p["categoria"] == categoria]}
    return {"productos": PRODUCTOS}


# Producto por id
@app.get("/productos/{producto_id}")
def producto(producto_id: str):
    for item in PRODUCTOS:
        if item["id"] == producto_id:
            return item

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# Listar pedidos
@app.get("/pedidos")
def pedidos():
    return {"pedidos": PEDIDOS}


# Pedido por id
@app.get("/pedidos/{pedido_id}")
def pedido(pedido_id: str):
    for item in PEDIDOS:
        if item["id"] == pedido_id:
            return item

    raise HTTPException(status_code=404, detail="Pedido no encontrado")
