import sys
import uuid
from datetime import datetime

import httpx

# Con --docker los servicios privados no publican puertos: "sin puerto" cuenta como aislamiento correcto
DOCKER = "--docker" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
BASE = ARGS[0] if len(ARGS) > 0 else "http://127.0.0.1:8000"
SALIDA = ARGS[1] if len(ARGS) > 1 else "docs/evidencias/validaciones.md"
filas = []
PLATO = "evid-plato"
EXTRA = "evid-extra"


def registrar(id_, caso, entrada, identidad, esperado, verifica, obtenido, ok):
    filas.append((id_, caso, entrada, identidad, esperado, verifica, obtenido, "OK" if ok else "FALLA"))
    print(("OK    " if ok else "FALLA ") + f"{id_} {caso}: {obtenido}")


def entrar(c, email, password):
    r = c.post("/api/auth/login", json={"email": email, "password": password})
    return {"Authorization": "Bearer " + r.json()["token"]}


def main():
    c = httpx.Client(base_url=BASE, timeout=10.0)
    sufijo = uuid.uuid4().hex[:6]
    for n in ("a", "b"):
        c.post("/api/auth/register", json={"nombre": f"Cliente {n.upper()}", "email": f"{n}{sufijo}@correo.cl", "password": "clave12345"})
    a = entrar(c, f"a{sufijo}@correo.cl", "clave12345")
    b = entrar(c, f"b{sufijo}@correo.cl", "clave12345")
    adm = entrar(c, "admin@masala.cl", "admin123")

    # Productos propios de la prueba: no dependen del estado que haya dejado un uso anterior
    for pid, nombre, precio_p in ((PLATO, "Plato de prueba", 9500), (EXTRA, "Extra de prueba", 2000)):
        r = c.post("/api/products", json={"id": pid, "nombre": nombre, "categoria": "extras", "precio": precio_p, "stock": 100, "activo": True}, headers=adm)
        if r.status_code == 409:
            c.patch(f"/api/products/{pid}", json={"precio": precio_p, "stock": 100, "activo": True}, headers=adm)

    # V1 catálogo anónimo
    r = c.get("/api/products")
    campos = set().union(*[p.keys() for p in r.json()["products"]])
    registrar("V1", "Acceso anónimo al catálogo", "GET /api/products", "anónimo", "200, solo campos públicos (sin stock)",
              "inventory", f"{r.status_code}, campos: {sorted(campos)}", r.status_code == 200 and "stock" not in campos)

    # V2 operación protegida sin sesión
    r = c.post("/api/orders", json={"items": [{"product_id": EXTRA, "cantidad": 1}], "tipo": "retiro"})
    registrar("V2", "Operación protegida sin sesión", "POST /api/orders", "anónimo", "401", "API Gateway", str(r.status_code), r.status_code == 401)
    r = c.post("/api/orders", json={"items": []}, headers={"Authorization": "Bearer mst_inventado_inventado"})
    registrar("V2b", "Token inventado", "POST /api/orders", "token falso", "401", "Auth Service (vía gateway)", str(r.status_code), r.status_code == 401)

    # V3 administración desde rol sin permiso
    r = c.delete(f"/api/products/{EXTRA}", headers=a)
    registrar("V3", "Administración con rol cliente", f"DELETE /api/products/{EXTRA}", "cliente", "403", "API Gateway e inventory", str(r.status_code), r.status_code == 403)
    r = c.patch("/api/orders/ORD-00000000/status", json={"estado": "ENTREGADO"}, headers=a)
    registrar("V3b", "Cambiar estado de cocina como cliente", "PATCH /api/orders/{id}/status", "cliente", "403", "API Gateway y orders", str(r.status_code), r.status_code == 403)

    # Pedido del cliente A
    cuerpo = {"items": [{"product_id": PLATO, "cantidad": 1}], "tipo": "retiro"}
    resp = c.post("/api/orders", json=cuerpo, headers=a)
    pedido = resp.json()
    if "id" not in pedido:
        print(f"No se pudo crear el pedido de prueba: HTTP {resp.status_code} {resp.text}")
        sys.exit(1)
    oid = pedido["id"]

    # V4 pedido ajeno
    ajeno = c.get(f"/api/orders/{oid}", headers=b)
    propio = c.get(f"/api/orders/{oid}", headers=a)
    registrar("V4", "Consulta de pedido ajeno", f"GET /api/orders/{oid}", "cliente B (no dueño)", "404 sin datos del pedido", "orders",
              f"{ajeno.status_code}, cuerpo: {ajeno.json().get('detail')}", ajeno.status_code == 404 and "items" not in ajeno.text)
    registrar("V4b", "Consulta de pedido propio", f"GET /api/orders/{oid}", "cliente A (dueño)", "200", "orders", str(propio.status_code), propio.status_code == 200)
    r = c.post(f"/api/orders/{oid}/pay", json={"metodo": "transferencia"}, headers=b)
    registrar("V4c", "Pagar pedido ajeno", f"POST /api/orders/{oid}/pay", "cliente B", "404", "orders", str(r.status_code), r.status_code == 404)

    # V5 acceso directo al backend
    directos = {}
    for nombre, puerto, ruta in (("orders", 9004, "/"), ("inventory", 9003, "/products"), ("payments", 9005, "/"), ("clients", 9002, "/me"), ("auth", 9001, "/me")):
        try:
            sin = httpx.get(f"http://127.0.0.1:{puerto}{ruta}", timeout=3).status_code
            falsa = httpx.get(f"http://127.0.0.1:{puerto}{ruta}", timeout=3,
                              headers={"X-User-Id": "u-admin", "X-User-Role": "admin", "X-Caller": "gateway", "X-Caller-Secret": "inventado"}).status_code
            directos[nombre] = (sin, falsa)
        except httpx.HTTPError:
            directos[nombre] = ("sin puerto", "sin puerto")
    aislado = ("sin puerto", "sin puerto")
    ok5 = all(v == (403, 403) or (DOCKER and v == aislado) for v in directos.values())
    registrar("V5", "Acceso directo a servicios privados sin identidad autorizada", "GET directo a cada servicio (sin credencial / identidad falsa)",
              "anónimo", "403 en ambos casos o sin puerto publicado" if DOCKER else "403 en ambos casos", "cada servicio (caller_for)", str(directos), ok5)
    try:
        g = httpx.post("http://127.0.0.1:8100/graphql", json={"query": "{ productos { id } }"}, timeout=3).status_code
        registrar("V5b", "Acceso directo al GraphQL Gateway", "POST directo a graphql", "anónimo", "403", "graphql (llamadorValido)", str(g), g == 403)
    except httpx.HTTPError:
        registrar("V5b", "Acceso directo al GraphQL Gateway", "POST directo a graphql", "anónimo", "403 o sin puerto publicado" if DOCKER else "403", "graphql", "sin puerto", DOCKER)

    # V6 pago alterado desde el frontend
    alterado = c.post(f"/api/orders/{oid}/pay", json={"metodo": "tarjeta", "token": "tok_sandbox", "monto": 1, "total": 1, "estado": "PAGADO"}, headers=a)
    comprobante = c.get(f"/api/payments/{oid}", headers=a).json()
    registrar("V6", "Confirmar pago con datos alterados", f"POST /api/orders/{oid}/pay con monto=1,total=1,estado=PAGADO", "cliente A",
              f"se cobra el total del servidor ({pedido['total']}) y el estado lo decide payments", "orders + payments",
              f"{alterado.status_code}, monto cobrado {comprobante.get('monto')}, estado {alterado.json().get('estado')}",
              alterado.status_code == 200 and comprobante.get("monto") == pedido["total"])
    precio = c.post("/api/orders", json={"items": [{"product_id": EXTRA, "cantidad": 1, "precio_unitario": 1}], "tipo": "retiro", "total": 1}, headers=a).json()
    registrar("V6b", "Precio y total enviados por el navegador", "POST /api/orders con precio_unitario=1,total=1", "cliente A", "total = precio del servidor (2000)",
              "orders + inventory", str(precio.get("total")), precio.get("total") == 2000)

    # V7 pago duplicado
    rep = c.post(f"/api/orders/{oid}/pay", json={"metodo": "tarjeta", "token": "tok_sandbox"}, headers=a).json()
    lista = c.get("/api/payments", headers=a, params={"ids": oid}).json()["payments"]
    registrar("V7", "Pago duplicado", f"POST /api/orders/{oid}/pay (segunda vez)", "cliente A", "mismo comprobante, un solo cobro", "orders + payments",
              f"ref igual: {rep.get('pago_ref') == comprobante.get('ref')}, cobros: {len(lista)}", rep.get("pago_ref") == comprobante.get("ref") and len(lista) == 1)

    # V8 stock recuperado tras pago rechazado
    antes = c.get(f"/api/products/{EXTRA}", headers=adm).json()["stock"]
    p2 = c.post("/api/orders", json={"items": [{"product_id": EXTRA, "cantidad": 3}], "tipo": "retiro"}, headers=a).json()
    reservado = c.get(f"/api/products/{EXTRA}", headers=adm).json()["stock"]
    rech = c.post(f"/api/orders/{p2['id']}/pay", json={"metodo": "tarjeta", "token": "tok_rechazada"}, headers=a)
    despues = c.get(f"/api/products/{EXTRA}", headers=adm).json()["stock"]
    registrar("V8", "Recuperación de stock tras pago rechazado", "reserva de 3 unidades y pago con tarjeta rechazada", "cliente A",
              "stock vuelve al valor inicial", "inventory (reserva/liberación)", f"{antes} -> {reservado} -> {despues}, pago {rech.status_code}",
              reservado == antes - 3 and despues == antes and rech.status_code == 402)

    # V9 GraphQL: campo no autorizado, profundidad, costo
    def gql(q, cab):
        return c.post("/api/graphql", json={"query": q}, headers=cab).json()
    g = gql("{ pedidos { id cliente { nombre telefono } } }", a)
    codigos = {e["extensions"]["code"] for e in g.get("errors", [])}
    nulo = all(p["cliente"] is None for p in g["data"]["pedidos"])
    registrar("V9", "Campo GraphQL restringido por rol", "{ pedidos { cliente { nombre telefono } } }", "cliente", "FORBIDDEN y cliente = null", "graphql (por campo)",
              f"{sorted(codigos)}, cliente null: {nulo}", codigos == {"FORBIDDEN"} and nulo)
    ga = gql("{ pedidos { id cliente { nombre } } }", adm)
    registrar("V9b", "Mismo campo con rol admin", "{ pedidos { cliente { nombre } } }", "admin", "datos del cliente, sin errores", "graphql",
              f"errores: {len(ga.get('errors', []))}", not ga.get("errors") and ga["data"]["pedidos"][0]["cliente"] is not None)
    prof = "producto { nombre }"
    for _ in range(8):
        prof = f"producto {{ {prof} }}"
    gp = gql("{ pedidos { items { " + prof + " } } }", a)
    registrar("V9c", "Límite de profundidad", "consulta con 10 niveles", "cliente", "rechazada en validación", "graphql (depthLimit)",
              (gp.get("errors") or [{}])[0].get("message", "")[:70], bool(gp.get("errors")) and "depth" in gp["errors"][0]["message"].lower())
    campos = " ".join(f"a{i}: id" for i in range(70))
    gc = gql("{ pedidos { " + campos + " } }", a)
    registrar("V9d", "Límite de costo (campos)", "70 alias en una consulta", "cliente", "rechazada en validación", "graphql (límite de campos)",
              (gc.get("errors") or [{}])[0].get("message", "")[:70], bool(gc.get("errors")) and "campos" in gc["errors"][0]["message"])
    gi = gql("{ __schema { types { name } } }", a)
    registrar("V9e", "Introspección desactivada", "{ __schema { types { name } } }", "cliente", "rechazada", "graphql", str(bool(gi.get("errors"))), bool(gi.get("errors")))
    agg = gql("{ pedidos(limit: 5) { id estado items { nombre producto { disponible } } pago { estado ref } } }", a)
    p0 = next(p for p in agg["data"]["pedidos"] if p["id"] == oid)
    registrar("V10", "Agregación orders + inventory + payments", "{ pedidos { items { producto { disponible } } pago { estado } } }", "cliente A",
              "pedido con disponibilidad actual y comprobante en una respuesta", "graphql",
              f"estado {p0['estado']}, pago {p0['pago']['estado']}, disponible {p0['items'][0]['producto']['disponible']}",
              p0["pago"]["estado"] == "APROBADO" and p0["items"][0]["producto"] is not None)

    # Retirar de la carta los productos de prueba
    for pid in (PLATO, EXTRA):
        c.patch(f"/api/products/{pid}", json={"activo": False}, headers=adm)

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(f"# Validaciones ejecutadas contra el backend en marcha\n\nEjecución: {ahora} · Gateway: {BASE}\n\n")
        f.write("| ID | Caso | Entrada | Identidad | Resultado esperado | Lo verifica | Resultado obtenido | Estado |\n|---|---|---|---|---|---|---|---|\n")
        for fila in filas:
            f.write("| " + " | ".join(str(x).replace("|", "/") for x in fila) + " |\n")

    fallas = [x for x in filas if x[-1] != "OK"]
    print(f"\n{len(filas) - len(fallas)}/{len(filas)} validaciones OK")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
