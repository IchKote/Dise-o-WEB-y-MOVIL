import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

# API Gateway
app = FastAPI(
    title="Secure API Gateway con Auth Service - Masala",
    description="Login con cookie HttpOnly, introspección en cada llamada, logout seguro y secretos en Vault"
)

# Configuración
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8100")
FASTAPI1_URL = os.getenv("FASTAPI1_URL", "http://localhost:9000")
FASTAPI2_URL = os.getenv("FASTAPI2_URL", "http://localhost:9100")

# Cookie de sesión. En producción (HTTPS) COOKIE_SECURE debe ser "true".
COOKIE_NAME = "session_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# Nombre de la cabecera con el secreto hacia el Auth Service
AUTH_SECRET_HEADER = "X-Gateway-Auth-Secret"

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no configurado")

# Tabla de enrutamiento: primer tramo de la ruta -> backend
RUTAS = {
    "products": FASTAPI1_URL,
    "orders": FASTAPI1_URL,
    "productos": FASTAPI2_URL,
    "pedidos": FASTAPI2_URL
}

# Headers que no se reenvían al backend (la cookie con el token tampoco)
HEADERS_SALTADOS = {"host", "content-length", "connection", "keep-alive",
                    "transfer-encoding", "te", "trailer", "upgrade",
                    "authorization", "cookie"}
# El cliente no puede inyectar cabeceras internas
PREFIJOS_RESERVADOS = ("x-gateway-", "x-authenticated-")


class LoginRequest(BaseModel):
    username: str
    password: str


# Cliente HTTP (función aparte para poder reemplazarla en las pruebas)
def http_client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)


# Secretos desde Vault (secret/gateway)
async def get_gateway_secrets():
    url = f"{VAULT_ADDR}/v1/secret/data/gateway"
    headers = {"X-Vault-Token": VAULT_TOKEN}

    try:
        async with http_client(5.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="No hay conexion con Vault")

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="No fue posible leer los secretos de Vault")

    try:
        vault_secrets = response.json()["data"]["data"]
    except (KeyError, ValueError):
        raise HTTPException(status_code=500, detail="Respuesta invalida de Vault")

    for nombre in ("backend_shared_secret", "auth_introspection_secret"):
        if not vault_secrets.get(nombre):
            raise HTTPException(status_code=500, detail=f"Falta el secreto '{nombre}' en Vault")

    return vault_secrets


# Llamada al Auth Service
async def llamar_auth(ruta: str, payload: dict, auth_secret: str | None = None):
    headers = {AUTH_SECRET_HEADER: auth_secret} if auth_secret else {}

    try:
        async with http_client(5.0) as client:
            return await client.post(f"{AUTH_URL}{ruta}", json=payload, headers=headers)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Auth Service no disponible")


# Pregunta al Auth Service si el token de la cookie sigue vigente
async def authenticate_client(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Sesion requerida: inicia sesion en /auth/login")

    vault_secrets = await get_gateway_secrets()
    respuesta = await llamar_auth(
        "/introspect", {"token": token}, vault_secrets["auth_introspection_secret"]
    )

    if respuesta.status_code != 200:
        # El Auth Service rechazó al Gateway: problema de configuración en la frontera
        raise HTTPException(status_code=502, detail="El Auth Service rechazo al Gateway")

    datos = respuesta.json()
    if not datos.get("active"):
        raise HTTPException(status_code=401, detail="Sesion invalida o expirada")

    return {
        "client_id": datos["sub"],
        "role": datos["role"],
        "backend_secret": vault_secrets["backend_shared_secret"]
    }


# Salud
@app.get("/health")
def health():
    return {"status": "OK", "service": "API Gateway"}


# Login: el token queda en una cookie HttpOnly, nunca en el cuerpo ni en JavaScript
@app.post("/auth/login")
async def login(datos: LoginRequest, response: Response):
    respuesta = await llamar_auth("/login", datos.model_dump())

    if respuesta.status_code == 401:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    if respuesta.status_code != 200:
        raise HTTPException(status_code=502, detail="Error en el Auth Service")

    sesion = respuesta.json()
    response.set_cookie(
        key=COOKIE_NAME,
        value=sesion["access_token"],
        max_age=sesion["expires_in"],
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        path="/"
    )

    return {"message": "Sesion iniciada", "user": sesion["username"], "role": sesion["role"]}


# Quién soy (útil para el frontend: no necesita leer el token)
@app.get("/auth/me")
async def me(auth=Depends(authenticate_client)):
    return {"user": auth["client_id"], "role": auth["role"]}


# Logout seguro: revoca en el servidor y borra la cookie
@app.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    revocado = False

    if token:
        vault_secrets = await get_gateway_secrets()
        respuesta = await llamar_auth(
            "/logout", {"token": token}, vault_secrets["auth_introspection_secret"]
        )
        if respuesta.status_code != 200:
            raise HTTPException(status_code=502, detail="No se pudo revocar la sesion")
        revocado = respuesta.json().get("revoked", False)

    response.delete_cookie(
        key=COOKIE_NAME, path="/", httponly=True, secure=COOKIE_SECURE, samesite="strict"
    )
    return {"message": "Sesion cerrada", "revoked": revocado}


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
        "X-Authenticated-Client": auth["client_id"],
        "X-Authenticated-Role": auth["role"]
    }
    headers.update(gateway_headers)

    try:
        async with http_client(10.0) as client:
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


# Proxy
@app.api_route("/api/{ruta:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(ruta: str, request: Request, auth=Depends(authenticate_client)):
    return await reenviar(request, ruta, auth)
