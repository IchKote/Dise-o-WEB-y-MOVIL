async def test_catalogo_publico_sin_stock_exacto(api):
    r = await api.get("/api/products")
    assert r.status_code == 200
    productos = r.json()["products"]
    assert len(productos) == 6
    assert all("stock" not in p and p["disponible"] for p in productos)


async def test_admin_ve_stock(api, admin):
    r = await api.get("/api/products/chicken-tikka-masala", headers=admin)
    assert r.json()["stock"] == 40


async def test_filtros(api):
    r = await api.get("/api/products", params={"categoria": "bebestibles"})
    assert {p["id"] for p in r.json()["products"]} == {"limonada-menta-jengibre", "bebida-lata-350"}
    assert (await api.get("/api/products", params={"categoria": "otra"})).status_code == 400
    assert (await api.get("/api/products", params={"available": "quizas"})).status_code == 400


async def test_producto_inexistente(api):
    assert (await api.get("/api/products/no-existe")).status_code == 404


NUEVO = {"id": "postre-gulab", "nombre": "Gulab Jamun", "categoria": "extras", "precio": 3500, "stock": 10}


async def test_crud_admin(api, admin):
    assert (await api.post("/api/products", json=NUEVO, headers=admin)).status_code == 201
    assert (await api.post("/api/products", json=NUEVO, headers=admin)).status_code == 409

    r = await api.patch("/api/products/postre-gulab", json={"precio": 3900}, headers=admin)
    assert r.json()["precio"] == 3900

    cambio = {k: v for k, v in NUEVO.items() if k != "id"} | {"nombre": "Gulab Jamun x2"}
    assert (await api.put("/api/products/postre-gulab", json=cambio, headers=admin)).json()["nombre"] == "Gulab Jamun x2"

    assert (await api.delete("/api/products/postre-gulab", headers=admin)).status_code == 200
    assert (await api.get("/api/products/postre-gulab")).status_code == 404
    assert (await api.get("/api/products/postre-gulab", headers=admin)).status_code == 200


async def test_solo_admin_modifica(api, cliente):
    assert (await api.post("/api/products", json=NUEVO, headers=cliente)).status_code == 403
    assert (await api.patch("/api/products/pan-naan-ajo", json={"precio": 1}, headers=cliente)).status_code == 403
    assert (await api.delete("/api/products/pan-naan-ajo", headers=cliente)).status_code == 403
    assert (await api.post("/api/products", json=NUEVO)).status_code == 401


async def test_validacion_producto(api, admin):
    for cambio in ({"precio": -5}, {"categoria": "otra"}, {"id": "ID con espacios"}, {"stock": "muchos"}, {"nombre": ""}):
        r = await api.post("/api/products", json=NUEVO | cambio, headers=admin)
        assert r.status_code == 400, cambio
    assert (await api.patch("/api/products/pan-naan-ajo", json={}, headers=admin)).status_code == 400
