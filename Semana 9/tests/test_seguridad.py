from fastapi.testclient import TestClient

from conftest import (AUTH_SECRET, auth_service, backend1, backend2,
                      gateway, iniciar_sesion)


# ---------- Login ----------

def test_login_incorrecto_401(cliente):
    r = iniciar_sesion(cliente, "ana", "clave-mala")
    assert r.status_code == 401


def test_usuario_inexistente_401(cliente):
    r = iniciar_sesion(cliente, "nadie", "ana123")
    assert r.status_code == 401


def test_login_entrega_cookie_httponly_y_no_el_token(cliente):
    r = iniciar_sesion(cliente, "ana", "ana123")
    assert r.status_code == 200
    assert r.json() == {"message": "Sesion iniciada", "user": "ana", "role": "user"}

    set_cookie = r.headers["set-cookie"].lower()
    assert "session_token=" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=strict" in set_cookie

    # El token no aparece en el cuerpo: JavaScript no puede leerlo
    token = cliente.cookies.get("session_token")
    assert token and token not in r.text


def test_me_devuelve_usuario_y_rol(cliente):
    iniciar_sesion(cliente, "ernesto", "ernesto123")
    r = cliente.get("/auth/me")
    assert r.status_code == 200
    assert r.json() == {"user": "ernesto", "role": "admin"}


# ---------- Gateway sin sesión ----------

def test_sin_cookie_401(cliente):
    assert cliente.get("/api/products").status_code == 401


def test_token_inventado_401(cliente):
    cliente.cookies.set("session_token", "token-inventado")
    assert cliente.get("/api/products").status_code == 401


# ---------- Roles ----------

def test_ana_lee_productos_200(cliente):
    iniciar_sesion(cliente, "ana", "ana123")
    assert cliente.get("/api/products").status_code == 200
    assert cliente.get("/api/productos").status_code == 200


def test_ana_no_puede_borrar_403(cliente):
    iniciar_sesion(cliente, "ana", "ana123")
    r = cliente.delete("/api/products/p01")
    assert r.status_code == 403
    assert any(p["id"] == "p01" for p in backend1.PRODUCTOS)


def test_ernesto_borra_200(cliente):
    iniciar_sesion(cliente, "ernesto", "ernesto123")
    r = cliente.delete("/api/products/p01")
    assert r.status_code == 200
    assert r.json() == {"deleted": "p01", "by": "ernesto"}
    assert all(p["id"] != "p01" for p in backend1.PRODUCTOS)

    r = cliente.delete("/api/productos/p02")
    assert r.status_code == 200
    assert all(p["id"] != "p02" for p in backend2.PRODUCTOS)


def test_cliente_no_puede_inyectar_rol(cliente):
    iniciar_sesion(cliente, "ana", "ana123")
    r = cliente.delete("/api/products/p01", headers={"X-Authenticated-Role": "admin"})
    assert r.status_code == 403


# ---------- Logout ----------

def test_logout_revoca_en_servidor_y_borra_cookie(cliente):
    iniciar_sesion(cliente, "ana", "ana123")
    token = cliente.cookies.get("session_token")
    assert cliente.get("/api/products").status_code == 200

    r = cliente.post("/auth/logout")
    assert r.status_code == 200
    assert r.json()["revoked"] is True
    assert cliente.cookies.get("session_token") is None

    # Después del logout, introspect responde active: false
    with TestClient(auth_service.app) as auth:
        r = auth.post("/introspect", json={"token": token},
                      headers={"X-Gateway-Auth-Secret": AUTH_SECRET})
        assert r.json() == {"active": False}

    # Aunque alguien haya copiado el token, ya no sirve
    cliente.cookies.set("session_token", token)
    assert cliente.get("/api/products").status_code == 401


def test_sesion_expirada_401(cliente):
    iniciar_sesion(cliente, "ana", "ana123")
    token = cliente.cookies.get("session_token")
    auth_service.SESIONES[token]["exp"] = 0
    assert cliente.get("/api/products").status_code == 401


# ---------- Fronteras: llamadas directas sin pasar por el Gateway ----------

def test_introspect_sin_secreto_403():
    with TestClient(auth_service.app) as auth:
        assert auth.post("/introspect", json={"token": "x"}).status_code == 403
        assert auth.post("/logout", json={"token": "x"},
                         headers={"X-Gateway-Auth-Secret": "malo"}).status_code == 403


def test_backend_directo_sin_secreto_403():
    with TestClient(backend1.app) as b1, TestClient(backend2.app) as b2:
        assert b1.get("/products").status_code == 403
        assert b2.get("/productos").status_code == 403


# ---------- Servicios caídos ----------

def test_backend_caido_502(cliente, red):
    iniciar_sesion(cliente, "ana", "ana123")
    red.apagados.add("fastapi2:9100")
    assert cliente.get("/api/productos").status_code == 502
    assert cliente.get("/api/products").status_code == 200


def test_auth_caido_502(cliente, red):
    red.apagados.add("auth:8100")
    assert iniciar_sesion(cliente, "ana", "ana123").status_code == 502


def test_vault_caido_500(cliente, red):
    iniciar_sesion(cliente, "ana", "ana123")
    red.apagados.add("vault:8200")
    assert cliente.get("/api/products").status_code == 500


def test_ruta_no_publicada_404(cliente):
    iniciar_sesion(cliente, "ana", "ana123")
    assert cliente.get("/api/clientes").status_code == 404
