"""
Arma todo el sistema en memoria para las pruebas: Vault falso, Auth Service,
FastAPI1, FastAPI2 y el Gateway. No hace falta levantar servidores ni Docker.
"""
import copy
import importlib.util
import os
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

BASE = Path(__file__).resolve().parent.parent

# Secretos de prueba (los mismos nombres que en Vault)
BACKEND_SECRET = "test-backend-secret"
AUTH_SECRET = "test-auth-secret"
VAULT_TOKEN = "test-vault-token"

os.environ["INTERNAL_GATEWAY_SECRET"] = BACKEND_SECRET
os.environ["AUTH_INTROSPECTION_SECRET"] = AUTH_SECRET
os.environ["VAULT_TOKEN"] = VAULT_TOKEN
os.environ["VAULT_ADDR"] = "http://vault:8200"
os.environ["AUTH_URL"] = "http://auth:8100"
os.environ["FASTAPI1_URL"] = "http://fastapi1:9000"
os.environ["FASTAPI2_URL"] = "http://fastapi2:9100"


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, BASE / ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


auth_service = cargar("auth_service", "AuthService/auth_service.py")
backend1 = cargar("backend1", "FastAPI1/backend1.py")
backend2 = cargar("backend2", "FastAPI2/backend2.py")
gateway = cargar("gateway", "Appgateway/gateway.py")

# Vault falso con secret/gateway
vault = FastAPI()


@vault.get("/v1/secret/data/gateway")
def leer_secretos(x_vault_token: str = Header(default="")):
    if x_vault_token != VAULT_TOKEN:
        raise HTTPException(status_code=403)
    return {"data": {"data": {
        "backend_shared_secret": BACKEND_SECRET,
        "auth_introspection_secret": AUTH_SECRET
    }}}


class Red(httpx.AsyncBaseTransport):
    """Enruta cada host:puerto a su app en memoria. Si un servicio está 'apagado', falla la conexión."""

    def __init__(self):
        self.servicios = {
            "vault:8200": httpx.ASGITransport(app=vault),
            "auth:8100": httpx.ASGITransport(app=auth_service.app),
            "fastapi1:9000": httpx.ASGITransport(app=backend1.app),
            "fastapi2:9100": httpx.ASGITransport(app=backend2.app),
        }
        self.apagados = set()

    async def handle_async_request(self, request):
        destino = f"{request.url.host}:{request.url.port}"
        if destino in self.apagados or destino not in self.servicios:
            raise httpx.ConnectError(f"{destino} no responde", request=request)
        return await self.servicios[destino].handle_async_request(request)


@pytest.fixture
def red(monkeypatch):
    red = Red()
    monkeypatch.setattr(
        gateway, "http_client",
        lambda timeout: httpx.AsyncClient(transport=red, timeout=timeout)
    )
    return red


@pytest.fixture(autouse=True)
def estado_limpio():
    productos1 = copy.deepcopy(backend1.PRODUCTOS)
    productos2 = copy.deepcopy(backend2.PRODUCTOS)
    auth_service.SESIONES.clear()
    yield
    backend1.PRODUCTOS[:] = productos1
    backend2.PRODUCTOS[:] = productos2
    auth_service.SESIONES.clear()


@pytest.fixture
def cliente(red):
    # Navegador: guarda la cookie HttpOnly entre llamadas, igual que un browser
    with TestClient(gateway.app) as c:
        yield c


def iniciar_sesion(cliente, usuario, password):
    return cliente.post("/auth/login", json={"username": usuario, "password": password})
