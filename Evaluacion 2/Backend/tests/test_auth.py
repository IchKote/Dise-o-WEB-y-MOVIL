from tests.helpers import login


async def test_registro_y_login(api):
    r = await api.post("/api/auth/register", json={"nombre": "Ana Pérez", "email": "ana@correo.cl", "password": "clave12345"})
    assert r.status_code == 201
    assert r.json()["rol"] == "cliente"
    assert "password" not in r.text and "hash" not in r.text

    cab = await login(api, "ana@correo.cl", "clave12345")
    me = await api.get("/api/auth/me", headers=cab)
    assert me.json()["email"] == "ana@correo.cl"

    perfil = await api.get("/api/clients/me", headers=cab)
    assert perfil.status_code == 200


async def test_no_se_puede_elegir_rol_admin(api):
    r = await api.post("/api/auth/register", json={"nombre": "Eva Mora", "email": "eva@correo.cl",
                                                    "password": "clave12345", "rol": "admin"})
    assert r.status_code == 201
    assert r.json()["rol"] == "cliente"


async def test_correo_duplicado(api):
    r = await api.post("/api/auth/register", json={"nombre": "Otra", "email": "CLIENTE@masala.cl", "password": "clave12345"})
    assert r.status_code == 409


async def test_validacion_registro(api):
    for body in ({"nombre": "A", "email": "x", "password": "123"}, {}, {"nombre": "Ana", "email": "a@b.cl", "password": "corta"}):
        r = await api.post("/api/auth/register", json=body)
        assert r.status_code == 400
        assert "corta" not in r.text


async def test_login_error_generico(api):
    mal_clave = await api.post("/api/auth/login", json={"email": "cliente@masala.cl", "password": "incorrecta"})
    no_existe = await api.post("/api/auth/login", json={"email": "nadie@masala.cl", "password": "incorrecta"})
    assert mal_clave.status_code == no_existe.status_code == 401
    assert mal_clave.json()["detail"] == no_existe.json()["detail"]


async def test_bloqueo_por_intentos(api, monkeypatch):
    monkeypatch.setattr("gateway.app.LIMITE_LOGIN", 100)
    for _ in range(5):
        await api.post("/api/auth/login", json={"email": "cliente@masala.cl", "password": "mala"})
    r = await api.post("/api/auth/login", json={"email": "cliente@masala.cl", "password": "cliente123"})
    assert r.status_code == 429


async def test_rate_limit_login(api):
    codigos = [(await api.post("/api/auth/login", json={"email": "a@a.cl", "password": "x"})).status_code for _ in range(12)]
    assert codigos[:10] == [401] * 10
    assert 429 in codigos[10:]


async def test_logout_revoca_token(api, cliente):
    assert (await api.get("/api/auth/me", headers=cliente)).status_code == 200
    assert (await api.post("/api/auth/logout", headers=cliente)).status_code == 204
    assert (await api.get("/api/auth/me", headers=cliente)).status_code == 401


async def test_token_invalido_o_ausente(api):
    assert (await api.get("/api/auth/me")).status_code == 401
    assert (await api.get("/api/auth/me", headers={"Authorization": "Bearer inventado"})).status_code == 401
    assert (await api.get("/api/auth/me", headers={"Authorization": "Basic abc"})).status_code == 401


async def test_nombre_con_html_rechazado(api):
    r = await api.post("/api/auth/register", json={"nombre": "<script>alert(1)</script>", "email": "xss@correo.cl", "password": "clave12345"})
    assert r.status_code == 400
