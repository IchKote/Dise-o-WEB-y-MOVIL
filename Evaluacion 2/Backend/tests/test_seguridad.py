from tests.helpers import login


async def test_servicios_exigen_credencial(directo):
    for servicio, ruta in (("orders", "/"), ("inventory", "/products"), ("clients", "/me"), ("auth", "/me"), ("payments", "/")):
        async with directo(servicio, "gateway", secreto="inventado") as c:
            assert (await c.get(ruta)).status_code == 403, servicio
        async with directo(servicio, "desconocido", secreto="x") as c:
            assert (await c.get(ruta)).status_code == 403, servicio


async def test_secreto_con_tildes_no_rompe(directo):
    async with directo("orders", "gateway", secreto="clavé-ñ") as c:
        assert (await c.get("/")).status_code == 403


async def test_rutas_internas_solo_para_su_llamador(directo):
    async with directo("inventory", "gateway", identidad=("u-admin", "admin")) as c:
        r = await c.post("/internal/reservations", json={"order_id": "ORD-1", "items": [{"product_id": "naan-extra", "cantidad": 1}]})
        assert r.status_code == 403
    async with directo("payments", "gateway", identidad=("u-admin", "admin")) as c:
        r = await c.post("/internal/charges", json={"order_id": "ORD-1", "user_id": "u-1", "monto": 10, "metodo": "transferencia"})
        assert r.status_code == 403
    async with directo("clients", "gateway") as c:
        assert (await c.post("/internal/clients", json={"user_id": "u-xx", "nombre": "Xx", "email": "x@x.cl"})).status_code == 403
    async with directo("auth", "graphql") as c:
        assert (await c.post("/internal/verify", json={"token": "a" * 20})).status_code == 403
        assert (await c.post("/login", json={"email": "a@a.cl", "password": "x"})).status_code == 403


async def test_identidad_solo_de_gateway_o_graphql(directo):
    # orders no puede declararse admin: la identidad se ignora
    async with directo("inventory", "orders", identidad=("u-admin", "admin")) as c:
        assert (await c.post("/products", json={"id": "hack-1", "nombre": "Hack", "categoria": "extras", "precio": 1, "stock": 1})).status_code == 401
    async with directo("clients", "auth", identidad=("u-admin", "admin")) as c:
        assert (await c.get("/")).status_code == 401


async def test_cabeceras_falsas_no_elevan_privilegios(api, cliente):
    falsas = cliente | {"X-User-Role": "admin", "X-User-Id": "u-admin", "X-Caller": "gateway"}
    assert (await api.get("/api/clients", headers=falsas)).status_code == 403
    assert (await api.get("/api/payments", headers=falsas)).json()["payments"] == []
    r = await api.get("/api/auth/me", headers=falsas)
    assert r.json()["email"] == "cliente@masala.cl"
    assert (await api.get("/api/orders", headers={"X-User-Id": "u-admin", "X-User-Role": "admin"})).status_code == 401


async def test_gateway_rutas_y_cuerpos(api, cliente):
    assert (await api.get("/api/internal/verify")).status_code == 404
    assert (await api.get("/api/../etc/passwd")).status_code in (404,)
    assert (await api.get("/api/products/%2e%2e/x")).status_code == 404
    assert (await api.delete("/api/orders", headers=cliente)).status_code == 405
    assert (await api.post("/api/orders", content=b"{no json", headers=cliente | {"Content-Type": "application/json"})).status_code == 400
    assert (await api.post("/api/orders", content=b"x" * 70000, headers=cliente)).status_code == 413
    r = await api.get("/api/orders/ORD-1", headers=cliente)
    assert r.status_code == 404


async def test_respuestas_con_correlacion_y_cabeceras(api):
    r = await api.get("/api/products")
    assert len(r.headers["x-request-id"]) == 12
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "no-store"
    mala = await api.get("/api/nada")
    assert mala.json()["request_id"] == mala.headers["x-request-id"]


async def test_cors_solo_origen_permitido(api):
    ok = await api.options("/api/products", headers={"Origin": "http://localhost:8080", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:8080"
    mal = await api.options("/api/products", headers={"Origin": "http://malo.cl", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in mal.headers


async def test_rate_limit_general(api, monkeypatch):
    monkeypatch.setattr("gateway.app.LIMITE_GENERAL", 5)
    codigos = [(await api.get("/api/products")).status_code for _ in range(8)]
    assert codigos[:5] == [200] * 5 and codigos[5:] == [429] * 3


async def test_sesion_de_otro_usuario_distinta(api, cliente, admin):
    assert (await api.get("/api/auth/me", headers=admin)).json()["rol"] == "admin"
    assert (await api.get("/api/auth/me", headers=cliente)).json()["rol"] == "cliente"


async def test_graphql_solo_por_el_gateway(api, cliente):
    q = {"query": "{ pedidos { id } }"}

    r = await api.post("/api/graphql", json=q, headers=cliente | {"X-User-Role": "admin", "X-User-Id": "u-admin"})
    data = r.json()
    assert r.status_code == 200
    assert data["caller"] == "gateway" and data["secreto_ok"] is True
    assert data["rol"] == "cliente" and data["user_id"] == "u-cliente"
    assert data["authorization"] is None
    assert data["cuerpo"] == q

    anonimo = (await api.post("/api/graphql", json=q)).json()
    assert anonimo["user_id"] is None and anonimo["rol"] is None

    assert (await api.post("/api/graphql", json=q, headers={"Authorization": "Bearer inventado"})).status_code == 401
    assert (await api.get("/api/graphql")).status_code == 405
    assert (await api.post("/api/graphql", content=b"[1,2]", headers={"Content-Type": "application/json"})).status_code == 400
