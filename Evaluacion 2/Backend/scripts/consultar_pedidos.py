import sys

import httpx

# Lista los pedidos como administrador (sirve para comprobar persistencia tras reiniciar)
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
c = httpx.Client(base_url=BASE, timeout=10.0)
r = c.post("/api/auth/login", json={"email": "admin@masala.cl", "password": "admin123"})
r.raise_for_status()
lista = c.get("/api/orders", headers={"Authorization": "Bearer " + r.json()["token"]})
lista.raise_for_status()
pedidos = lista.json()["orders"]
print(f"{len(pedidos)} pedidos en {BASE}")
for p in pedidos[:15]:
    print(p["id"], p["estado"], p.get("total"))
