import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager

from masala_common import outbound, secrets_store
from masala_common.app import log
from masala_common.outbound import Upstream
from masala_common.security import Identity

SERVICE = "gateway"
MAX_BODY = 64 * 1024
PUBLICA, OPCIONAL, REQUERIDA = "publica", "opcional", "requerida"

# Tabla de rutas expuestas: (método, patrón, servicio, ruta interna, acceso, roles permitidos)
RUTAS = [
    ("POST", r"auth/register", "auth", "/register", PUBLICA, None),
    ("POST", r"auth/login", "auth", "/login", PUBLICA, None),
    ("POST", r"auth/logout", "auth", "/logout", REQUERIDA, None),
    ("GET", r"auth/me", "auth", "/me", REQUERIDA, None),

    ("GET", r"clients/me", "clients", "/me", REQUERIDA, None),
    ("PUT", r"clients/me", "clients", "/me", REQUERIDA, None),
    ("GET", r"clients", "clients", "/", REQUERIDA, {"admin"}),
    ("GET", r"clients/(?P<id>[A-Za-z0-9-]{3,40})", "clients", "/{id}", REQUERIDA, {"admin"}),

    ("GET", r"products", "inventory", "/products", OPCIONAL, None),
    ("GET", r"products/(?P<id>[a-z0-9-]{3,40})", "inventory", "/products/{id}", OPCIONAL, None),
    ("POST", r"products", "inventory", "/products", REQUERIDA, {"admin"}),
    ("PUT", r"products/(?P<id>[a-z0-9-]{3,40})", "inventory", "/products/{id}", REQUERIDA, {"admin"}),
    ("PATCH", r"products/(?P<id>[a-z0-9-]{3,40})", "inventory", "/products/{id}", REQUERIDA, {"admin"}),
    ("DELETE", r"products/(?P<id>[a-z0-9-]{3,40})", "inventory", "/products/{id}", REQUERIDA, {"admin"}),

    ("POST", r"orders", "orders", "/", REQUERIDA, {"cliente"}),
    ("GET", r"orders", "orders", "/", REQUERIDA, None),
    ("GET", r"orders/(?P<id>ORD-[A-F0-9]{8})", "orders", "/{id}", REQUERIDA, None),
    ("POST", r"orders/(?P<id>ORD-[A-F0-9]{8})/pay", "orders", "/{id}/pay", REQUERIDA, {"cliente"}),
    ("POST", r"orders/(?P<id>ORD-[A-F0-9]{8})/cancel", "orders", "/{id}/cancel", REQUERIDA, None),
    ("PATCH", r"orders/(?P<id>ORD-[A-F0-9]{8})/status", "orders", "/{id}/status", REQUERIDA, {"admin"}),

    ("GET", r"payments", "payments", "/", REQUERIDA, None),

    # Agregaciones: el GraphQL Gateway es privado, solo se llega por aquí
    ("POST", r"graphql", "graphql", "/graphql", OPCIONAL, None),
    ("GET", r"payments/(?P<id>ORD-[A-F0-9]{8})", "payments", "/{id}", REQUERIDA, None),
]
COMPILADAS = [(m, re.compile(p + r"$"), s, i, a, r) for m, p, s, i, a, r in RUTAS]

# Límites por IP (ventana de 60 s)
LIMITE_GENERAL = int(os.getenv("RATE_LIMIT", "120"))
LIMITE_LOGIN = int(os.getenv("RATE_LIMIT_LOGIN", "10"))
_hits = defaultdict(deque)


@asynccontextmanager
async def lifespan(app):
    await secrets_store.load_secrets(SERVICE)
    yield
    await outbound.close_all()


app = FastAPI(title="API Gateway - Masala", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# CORS: solo orígenes del frontend
origenes = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080,http://localhost,http://127.0.0.1").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware, allow_origins=origenes, allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    expose_headers=["X-Request-Id"], max_age=600
)


def limitado(clave, limite):
    ahora = time.time()
    cola = _hits[clave]

    while cola and cola[0] < ahora - 60:
        cola.popleft()

    if len(cola) >= limite:
        return True

    cola.append(ahora)
    return False


def respuesta(status, detail, rid, extra=None):
    body = {"detail": detail, "request_id": rid}
    body.update(extra or {})
    return JSONResponse(status_code=status, content=body, headers={"X-Request-Id": rid})


# Cabeceras de seguridad y correlación en todas las respuestas
@app.middleware("http")
async def contexto(request: Request, call_next):
    rid = uuid.uuid4().hex[:12]
    request.state.rid = rid
    inicio = time.time()

    ip = request.client.host if request.client else "?"
    if request.method != "OPTIONS" and limitado(f"all:{ip}", LIMITE_GENERAL):
        return respuesta(429, "Demasiadas solicitudes", rid)

    response = await call_next(request)
    response.headers["X-Request-Id"] = rid
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    log.info("rid=%s %s %s -> %s %.0fms", rid, request.method, request.url.path,
             response.status_code, (time.time() - inicio) * 1000)
    return response


# Estado de salud
@app.get("/health")
async def health():
    return {"status": "OK", "service": SERVICE}


def buscar(method, path):
    permitido = []
    for m, patron, servicio, interna, acceso, roles in COMPILADAS:
        encontrado = patron.match(path)
        if encontrado:
            if m == method:
                return servicio, interna.format(**encontrado.groupdict()), acceso, roles
            permitido.append(m)

    if permitido:
        raise HTTPException(status_code=405, detail="Método no permitido")

    raise HTTPException(status_code=404, detail="Ruta no encontrada")


# Verifica el token con el servicio auth
async def autenticar(request, rid):
    cabecera = request.headers.get("authorization", "")

    if not cabecera:
        return None, None

    partes = cabecera.split(" ", 1)
    if len(partes) != 2 or partes[0].lower() != "bearer" or not partes[1].strip():
        raise HTTPException(status_code=401, detail="Token inválido")

    token = partes[1].strip()
    r = await Upstream(SERVICE, "auth").request("POST", "/internal/verify", request_id=rid, json={"token": token})

    if r.status_code in (400, 401):
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Servicio de autenticación no disponible")

    datos = r.json()
    return Identity(datos["user_id"], datos["rol"], datos["email"]), token


@app.api_route("/api/{ruta:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(ruta: str, request: Request):
    rid = request.state.rid

    try:
        # Se rechaza ".." y rutas fuera de la tabla
        if ".." in ruta or "//" in ruta:
            raise HTTPException(status_code=404, detail="Ruta no encontrada")

        servicio, interna, acceso, roles = buscar(request.method, ruta.strip("/"))

        if ruta.strip("/") == "auth/login":
            ip = request.client.host if request.client else "?"
            if limitado(f"login:{ip}", LIMITE_LOGIN):
                return respuesta(429, "Demasiados intentos de inicio de sesión", rid)

        identity, token = None, None
        if acceso != PUBLICA:
            identity, token = await autenticar(request, rid)

            if acceso == REQUERIDA and identity is None:
                raise HTTPException(status_code=401, detail="Autenticación requerida")
            if roles and identity.rol not in roles:
                raise HTTPException(status_code=403, detail="Rol sin permiso para esta operación")

        # Cuerpo JSON con tamaño máximo
        cuerpo = None
        crudo = await request.body()
        if len(crudo) > MAX_BODY:
            raise HTTPException(status_code=413, detail="Cuerpo demasiado grande")
        if crudo:
            try:
                cuerpo = json.loads(crudo)
            except ValueError:
                raise HTTPException(status_code=400, detail="JSON inválido")

        params = dict(request.query_params)
        if len(request.url.query) > 500:
            raise HTTPException(status_code=414, detail="Consulta demasiado larga")

        # Solo estas cabeceras pasan hacia adentro
        extra = {}
        if request.headers.get("idempotency-key"):
            extra["Idempotency-Key"] = request.headers["idempotency-key"]
        if servicio == "graphql" and not isinstance(cuerpo, dict):
            raise HTTPException(status_code=400, detail="Consulta GraphQL inválida")
        if servicio == "auth" and token and interna == "/logout":
            extra["X-Session-Token"] = token

        r = await Upstream(SERVICE, servicio).request(
            request.method, interna, identity=identity, request_id=rid,
            json=cuerpo, params=params or None, extra_headers=extra
        )
    except HTTPException as error:
        return respuesta(error.status_code, error.detail, rid)

    # Caída o lentitud de otro servicio: se conserva el código (502/504)
    if r.status_code in (502, 504):
        detalle = r.json().get("detail") if r.content else None
        return respuesta(r.status_code, detalle if isinstance(detalle, str) else "Servicio interno no disponible", rid)

    # Errores internos: mensaje genérico, el detalle queda en los logs del servicio
    if r.status_code >= 500:
        log.error("rid=%s %s respondió %s", rid, servicio, r.status_code)
        return respuesta(502, "Error en el servicio interno", rid)

    if r.status_code == 204 or not r.content:
        return Response(status_code=r.status_code, headers={"X-Request-Id": rid})

    try:
        datos = r.json()
    except ValueError:
        return respuesta(502, "Respuesta inválida del servicio interno", rid)

    if r.status_code >= 400 and isinstance(datos, dict):
        datos.setdefault("request_id", rid)

    return JSONResponse(status_code=r.status_code, content=datos, headers={"X-Request-Id": rid})
