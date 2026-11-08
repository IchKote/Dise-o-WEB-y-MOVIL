import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response

# API Gateway
app = FastAPI(
    title="API Gateway - Masala",
    description="Único punto de entrada público: reenvía /api/... al backend que corresponde"
)

# Backends
FASTAPI1_URL = os.getenv("FASTAPI1_URL", "http://localhost:9000")
FASTAPI2_URL = os.getenv("FASTAPI2_URL", "http://localhost:9100")

# Tabla de enrutamiento: primer tramo de la ruta -> backend
RUTAS = {
    "products": FASTAPI1_URL,
    "orders": FASTAPI1_URL,
    "productos": FASTAPI2_URL,
    "pedidos": FASTAPI2_URL
}

# Headers que no se reenvían
HEADERS_SALTADOS = {"host", "content-length", "connection", "keep-alive",
                    "transfer-encoding", "te", "trailer", "upgrade"}


# Reenvío
async def reenviar(request: Request, ruta: str):
    tramos = ruta.split("/")
    servicio = tramos[0]

    # Ruta publicada
    if servicio not in RUTAS or ".." in tramos:
        raise HTTPException(status_code=404, detail="Ruta no publicada en el Gateway")

    destino = f"{RUTAS[servicio]}/{ruta}"
    if request.url.query:
        destino += "?" + request.url.query

    headers = {
        nombre: valor for nombre, valor in request.headers.items()
        if nombre.lower() not in HEADERS_SALTADOS
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            respuesta = await client.request(
                request.method, destino,
                headers=headers, content=await request.body()
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="El backend tardó demasiado")
    except httpx.RequestError:
        # Backend caído
        raise HTTPException(status_code=502, detail="Backend no disponible")

    return Response(
        content=respuesta.content,
        status_code=respuesta.status_code,
        media_type=respuesta.headers.get("content-type")
    )


# Salud
@app.get("/health")
def health():
    return {"status": "OK", "service": "API Gateway"}


# Proxy
@app.api_route("/api/{ruta:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(ruta: str, request: Request):
    return await reenviar(request, ruta)
