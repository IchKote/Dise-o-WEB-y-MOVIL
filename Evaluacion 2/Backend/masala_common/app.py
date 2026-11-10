import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import outbound, secrets_store

log = logging.getLogger("masala")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# Crea la app de un servicio con arranque seguro, errores controlados y logs sin secretos
def create_app(service, title, on_start=None, on_stop=None):
    @asynccontextmanager
    async def lifespan(app):
        # Sin secretos el servicio no arranca
        await secrets_store.load_secrets(service)

        if on_start:
            await on_start()

        yield

        if on_stop:
            await on_stop()

        await outbound.close_all()

    app = FastAPI(title=title, lifespan=lifespan)

    # Identificador de correlación
    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        log.info("rid=%s %s %s -> %s caller=%s", rid, request.method, request.url.path,
                 response.status_code, request.headers.get("x-caller", "-"))
        return response

    # Validación: 400 sin devolver los valores recibidos
    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        errores = [
            {"campo": ".".join(str(p) for p in e["loc"][1:]), "mensaje": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(status_code=400, content={"detail": "Datos inválidos", "errores": errores})

    # Estado de salud (abierto, sin datos sensibles)
    @app.get("/health")
    async def health():
        return {"status": "OK", "service": service}

    return app
