import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI(
    title="FastAPI 1 protegido - Masala",
    description="Solo acepta llamadas del API Gateway (X-Gateway-Secret). Borrar exige rol admin (X-Authenticated-Role)"
)

# Secreto compartido con el Gateway (nunca va en Git: se entrega por variable de entorno)
INTERNAL_GATEWAY_SECRET = os.getenv("INTERNAL_GATEWAY_SECRET")

if not INTERNAL_GATEWAY_SECRET:
    raise RuntimeError("INTERNAL_GATEWAY_SECRET no esta configurado")


# Validar que la llamada viene del Gateway
def verify_gateway(x_gateway_secret: str = Header(default="")):
    valid = secrets.compare_digest(
        x_gateway_secret.encode(),
        INTERNAL_GATEWAY_SECRET.encode()
    )

    if not valid:
        raise HTTPException(
            status_code=403,
            detail="Acceso directo no permitido: la solicitud debe pasar por el Gateway"
        )


# Autorización por rol: el Gateway informa el rol que le dio el Auth Service
def require_admin(x_authenticated_role: str = Header(default="")):
    if x_authenticated_role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: se requiere rol admin")


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
    return {"status": "OK", "service": "FastAPI 1"}


# Listar productos (filtro opcional por categoría)
@app.get("/products", dependencies=[Depends(verify_gateway)])
def products(categoria: str | None = None):
    if categoria:
        return {"products": [p for p in PRODUCTOS if p["categoria"] == categoria]}
    return {"products": PRODUCTOS}


# Producto por id
@app.get("/products/{product_id}", dependencies=[Depends(verify_gateway)])
def product(product_id: str):
    for producto in PRODUCTOS:
        if producto["id"] == product_id:
            return producto

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# Borrar producto (solo admin)
@app.delete("/products/{product_id}", dependencies=[Depends(verify_gateway), Depends(require_admin)])
def borrar_producto(product_id: str, x_authenticated_client: str | None = Header(default=None)):
    for i, item in enumerate(PRODUCTOS):
        if item["id"] == product_id:
            PRODUCTOS.pop(i)
            return {"deleted": product_id, "by": x_authenticated_client}

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# Listar pedidos
@app.get("/orders", dependencies=[Depends(verify_gateway)])
def orders():
    return {"orders": PEDIDOS}


# Pedido por id
@app.get("/orders/{order_id}", dependencies=[Depends(verify_gateway)])
def order(order_id: str):
    for pedido in PEDIDOS:
        if pedido["id"] == order_id:
            return pedido

    raise HTTPException(status_code=404, detail="Pedido no encontrado")
