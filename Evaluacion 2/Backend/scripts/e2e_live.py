import sys
import uuid

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
fallos = []


def check(nombre, condicion):
    print(("OK    " if condicion else "FALLA ") + nombre)
    if not condicion:
        fallos.append(nombre)


def main():
    c = httpx.Client(base_url=BASE, timeout=10.0)
    correo = f"e2e-{uuid.uuid4().hex[:6]}@correo.cl"

    check("catálogo público", len(c.get("/api/products").json()["products"]) >= 6)
    check("sin token -> 401", c.get("/api/orders").status_code == 401)

    r = c.post("/api/auth/register", json={"nombre": "Usuario E2E", "email": correo, "password": "clave12345"})
    check("registro -> 201", r.status_code == 201)
    token = c.post("/api/auth/login", json={"email": correo, "password": "clave12345"}).json()["token"]
    cab = {"Authorization": "Bearer " + token}

    o = c.post("/api/orders", headers=cab | {"Idempotency-Key": uuid.uuid4().hex},
               json={"items": [{"product_id": "chicken-tikka-masala", "cantidad": 2}], "tipo": "delivery",
                     "direccion": "Av. Test 1", "codigo": "MASALA20"}).json()
    check("total 15200 + envío 2000 = 17200", o.get("total") == 17200)

    p = c.post(f"/api/orders/{o['id']}/pay", headers=cab, json={"metodo": "tarjeta", "token": "tok_visa_prueba"})
    check("pago -> PAGADO", p.json().get("estado") == "PAGADO")

    adm = c.post("/api/auth/login", json={"email": "admin@masala.cl", "password": "admin123"}).json()["token"]
    cab_adm = {"Authorization": "Bearer " + adm}
    r = c.patch(f"/api/orders/{o['id']}/status", headers=cab_adm, json={"estado": "EN_PREPARACION"})
    check("admin avanza estado", r.json().get("estado") == "EN_PREPARACION")
    check("cliente no administra productos -> 403", c.post("/api/products", headers=cab, json={}).status_code == 403)

    otro = c.post("/api/auth/login", json={"email": "cliente@masala.cl", "password": "cliente123"}).json()["token"]
    check("pedido ajeno -> 404", c.get(f"/api/orders/{o['id']}", headers={"Authorization": "Bearer " + otro}).status_code == 404)

    c.post("/api/auth/logout", headers=cab)
    check("logout revoca token", c.get("/api/auth/me", headers=cab).status_code == 401)

    print(f"\n{'TODO OK' if not fallos else 'FALLAS: ' + str(len(fallos))}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
