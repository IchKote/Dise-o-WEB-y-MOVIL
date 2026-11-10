import json
import os
import time

import httpx


class SecretsUnavailable(Exception):
    pass


_data = {}
_loaded_at = {}


def set_secrets(service, data):
    _data[service] = data
    _loaded_at[service] = time.time()


def get_secrets(service):
    if service not in _data:
        raise SecretsUnavailable(f"Secretos de {service} no cargados")

    return _data[service]


# Lee los secretos del servicio: Vault, o SERVICE_SECRETS (JSON) si no hay Vault
async def load_secrets(service):
    addr = os.getenv("VAULT_ADDR")
    token = os.getenv("VAULT_TOKEN")

    if addr and token:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{addr}/v1/secret/data/{service}",
                    headers={"X-Vault-Token": token}
                )
            response.raise_for_status()
            data = response.json()["data"]["data"]
        except (httpx.HTTPError, KeyError, ValueError) as error:
            raise SecretsUnavailable("No fue posible leer Vault") from error
    else:
        raw = os.getenv("SERVICE_SECRETS")
        if not raw:
            raise SecretsUnavailable("Sin Vault ni SERVICE_SECRETS")
        data = json.loads(raw)

    set_secrets(service, data)
    return data


# Usa el valor en memoria y lo renueva cada ttl segundos; si Vault cae, conserva el último
async def refresh_secrets(service, ttl=60):
    if service in _data and time.time() - _loaded_at.get(service, 0) < ttl:
        return _data[service]

    try:
        return await load_secrets(service)
    except SecretsUnavailable:
        if service in _data:
            return _data[service]
        raise
