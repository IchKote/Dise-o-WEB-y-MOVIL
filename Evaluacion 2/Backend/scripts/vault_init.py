import os
import sys
import time

import httpx

sys.path.insert(0, os.path.dirname(__file__))
from credentials import SISTEMAS, generar  # noqa: E402

VAULT = os.getenv("VAULT_ADDR", "http://localhost:8200")
ROOT = os.getenv("VAULT_ROOT_TOKEN", "root-token-masala")


# Token fijo de desarrollo por sistema (en producción los emite Vault)
def token_de(sistema):
    return f"vt-{sistema}"


def main():
    cliente = httpx.Client(base_url=VAULT, headers={"X-Vault-Token": ROOT}, timeout=5.0)

    for _ in range(30):
        try:
            if cliente.get("/v1/sys/health").status_code in (200, 429, 472, 473):
                break
        except httpx.HTTPError:
            pass
        time.sleep(1)
    else:
        raise SystemExit("Vault no responde")

    datos = generar()

    for sistema in SISTEMAS:
        r = cliente.post(f"/v1/secret/data/{sistema}", json={"data": datos[sistema]})
        r.raise_for_status()

        # Política: solo lectura de su propio secreto
        regla = f'path "secret/data/{sistema}" {{ capabilities = ["read"] }}'
        cliente.put(f"/v1/sys/policies/acl/{sistema}", json={"policy": regla}).raise_for_status()

        r = cliente.post("/v1/auth/token/create", json={
            "id": token_de(sistema), "policies": [sistema], "no_parent": True, "ttl": "24h"
        })
        if r.status_code not in (200, 400):
            r.raise_for_status()

    print("Vault listo: secretos, políticas y tokens por sistema")


if __name__ == "__main__":
    main()
