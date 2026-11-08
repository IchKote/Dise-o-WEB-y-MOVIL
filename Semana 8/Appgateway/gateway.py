import os
import secrets

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# API Gateway
app = FastAPI(
    title="Secure API Gateway - Masala",
    description="API Gateway protegido con Bearer Token y secretos guardados en Vault"
)

# Bearer token (auto_error=False para responder 401 en vez del 403 por defecto)
security = HTTPBearer(auto_error=False)

# Configuración
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
FASTAPI1_URL = os.getenv("FASTAPI1_URL", "http://localhost:9000")
FASTAPI2_URL = os.getenv("FASTAPI2_URL", "http://localhost:9100")

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no configurado")

# Tabla de enrutamiento: primer tramo de la ruta -> backend
RUTAS = {
    "products": FASTAPI1_URL,
    "orders": FASTAPI1_URL,
    "productos": FASTAPI2_URL,
    "pedidos": FASTAPI2_URL
}

# Headers que no se reenvían (el token del cliente no llega al backend)
HEADERS_SALTADOS = {"host", "content-length", "connection", "keep-alive",
                    "transfer-encoding", "te", "trailer", "upgrade", "authorization"}
# El cliente no puede inyectar cabeceras internas
PREFIJOS_RESERVADOS = ("x-gateway-", "x-authenticated-")


# Secretos desde Vault (secret/gateway)
async def get_gateway_secrets():
    url = f"{VAULT_ADDR}/v1/secret/data/gateway"
    headers = {"X-Vault-Token": VAULT_TOKEN}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="No hay conexion con Vault")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="No fue posible leer los secretos de Vault")

    try:
        vault_secrets = response.json()["data"]["data"]
    except (KeyError, ValueError):
        raise HTTPException(status_code=500, detail="Respuesta invalida de Vault")

    for nombre in ("client_token", "backend_shared_secret"):
        if not vault_secrets.get(nombre):
            raise HTTPException(status_code=500, detail=f"Falta el secreto '{nombre}' en Vault")

    return vault_secrets


# Validar token del cliente
async def authenticate_client(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token requerido")

    vault_secrets = await get_gateway_secrets()

    valid = secrets.compare_digest(
        credentials.credentials.encode(),
        vault_secrets["client_token"].encode()
    )

    if not valid:
        raise HTTPException(status_code=401, detail="Token invalido")

    return {
        "client_id": "cliente-masala",
        "backend_secret": vault_secrets["backend_shared_secret"]
    }


# Reenvío
async def reenviar(request: Request, ruta: str, auth):
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
        and not nombre.lower().startswith(PREFIJOS_RESERVADOS)
    }
    gateway_headers = {
        "X-Gateway-Secret": auth["backend_secret"],
        "X-Authenticated-Client": auth["client_id"]
    }
    headers.update(gateway_headers)

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
async def proxy(ruta: str, request: Request, auth=Depends(authenticate_client)):
    return await reenviar(request, ruta, auth)
