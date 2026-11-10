import os
import uuid

import httpx
from fastapi import HTTPException

from . import secrets_store

# En pruebas se reemplaza por una app en memoria: {"inventory": ASGITransport(...)}
TRANSPORTS = {}

# Conexiones persistentes hacia cada servicio (evita abrir una por llamada)
_pool = {}


async def close_all():
    for client in _pool.values():
        await client.aclose()
    _pool.clear()


# Cliente para llamar a otro servicio con la credencial que le corresponde
class Upstream:
    def __init__(self, me, target, timeout=5.0):
        self.me = me
        self.target = target
        self.timeout = timeout

    def base_url(self):
        return os.getenv(f"{self.target.upper()}_URL", f"http://{self.target}:8000")

    async def request(self, method, path, *, identity=None, request_id=None,
                      json=None, params=None, extra_headers=None):
        try:
            outbound = secrets_store.get_secrets(self.me).get("outbound", {})
        except secrets_store.SecretsUnavailable:
            raise HTTPException(status_code=500, detail="Secretos no disponibles")

        secret = outbound.get(self.target)
        if not secret:
            raise HTTPException(status_code=500, detail="Credencial de integración no configurada")

        headers = {
            "X-Caller": self.me,
            "X-Caller-Secret": secret,
            "X-Request-Id": request_id or uuid.uuid4().hex[:12]
        }

        if identity is not None:
            headers["X-User-Id"] = identity.id
            headers["X-User-Role"] = identity.rol
            headers["X-User-Email"] = identity.email

        if extra_headers:
            headers.update(extra_headers)

        transport = TRANSPORTS.get(self.target)

        try:
            if transport:
                async with httpx.AsyncClient(base_url="http://" + self.target, transport=transport,
                                             timeout=self.timeout) as client:
                    return await client.request(method, path, headers=headers, json=json, params=params)

            base = self.base_url()
            client = _pool.get(base)
            if client is None:
                client = _pool[base] = httpx.AsyncClient(
                    base_url=base, timeout=self.timeout,
                    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20))
            return await client.request(method, path, headers=headers, json=json, params=params)
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail=f"{self.target} no respondió a tiempo")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail=f"{self.target} no disponible")
