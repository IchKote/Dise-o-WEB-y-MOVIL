import httpx
from fastapi import FastAPI, Request
import pytest
from httpx import ASGITransport
from mongomock_motor import AsyncMongoMockClient

import gateway.app as gw
from credentials import SISTEMAS, generar
from tests.helpers import login
from masala_common import db, outbound, secrets_store
from services.auth import app as auth
from services.clients import app as clients
from services.inventory import app as inventory
from services.orders import app as orders
from services.payments import app as payments

# GraphQL (Node) simulado: devuelve lo que recibió para comprobar qué atraviesa el gateway
fake_graphql = FastAPI()


@fake_graphql.post("/graphql")
async def eco(request: Request):
    h = request.headers
    return {"caller": h.get("x-caller"), "secreto_ok": h.get("x-caller-secret") == fake_graphql.state.secreto,
            "user_id": h.get("x-user-id"), "rol": h.get("x-user-role"), "authorization": h.get("authorization"),
            "cuerpo": await request.json()}


SERVICIOS = {"auth": auth, "clients": clients, "inventory": inventory,
             "orders": orders, "payments": payments}


# Entorno completo en memoria: servicios, gateway y base de datos simulada
@pytest.fixture
async def entorno():
    db.set_client(AsyncMongoMockClient())
    datos = generar()
    for sistema in SISTEMAS:
        secrets_store.set_secrets(sistema, datos[sistema])

    outbound.TRANSPORTS.clear()
    for nombre, modulo in SERVICIOS.items():
        outbound.TRANSPORTS[nombre] = ASGITransport(app=modulo.app)
        await modulo.init()

    fake_graphql.state.secreto = datos["gateway"]["outbound"]["graphql"]
    outbound.TRANSPORTS["graphql"] = ASGITransport(app=fake_graphql)

    gw._hits.clear()
    yield datos
    outbound.TRANSPORTS.clear()


# Cliente HTTP contra el gateway (lo que ve el frontend)
@pytest.fixture
async def api(entorno):
    async with httpx.AsyncClient(transport=ASGITransport(app=gw.app), base_url="http://gateway") as c:
        yield c


@pytest.fixture
async def cliente(api):
    return await login(api, "cliente@masala.cl", "cliente123")


@pytest.fixture
async def admin(api):
    return await login(api, "admin@masala.cl", "admin123")


# Llamada directa a un servicio con las credenciales de otro sistema
@pytest.fixture
def directo(entorno):
    def hacer(servicio, llamador, secreto=None, identidad=None):
        valor = secreto or entorno[llamador]["outbound"].get(servicio, "x")
        cab = {"X-Caller": llamador, "X-Caller-Secret": valor.encode()}
        if identidad:
            cab.update({"X-User-Id": identidad[0], "X-User-Role": identidad[1], "X-User-Email": "x@x.cl"})
        return httpx.AsyncClient(transport=ASGITransport(app=SERVICIOS[servicio].app),
                                 base_url="http://svc", headers=cab)
    return hacer
