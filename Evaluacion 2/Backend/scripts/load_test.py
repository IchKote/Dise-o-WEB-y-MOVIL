import argparse
import asyncio
import statistics
import time
import uuid

import httpx

try:
    import psutil
except ImportError:
    psutil = None


async def trabajador(cliente, fin, escenario, tiempos, errores):
    while time.perf_counter() < fin:
        t = time.perf_counter()
        try:
            ok = await escenario(cliente)
        except httpx.HTTPError:
            ok = False
        tiempos.append((time.perf_counter() - t) * 1000)
        if not ok:
            errores.append(1)


async def ver_catalogo(cliente):
    return (await cliente.get("/api/products")).status_code == 200


async def agregacion(cliente, cab):
    q = "{ pedidos(limit: 20) { id estado total items { nombre producto { disponible } } pago { estado } } }"
    r = await cliente.post("/api/graphql", headers=cab, json={"query": q})
    return r.status_code == 200 and "errors" not in r.json()


async def comprar(cliente, cab):
    r = await cliente.post("/api/orders", headers=cab | {"Idempotency-Key": uuid.uuid4().hex},
                           json={"items": [{"product_id": "naan-extra", "cantidad": 1}], "tipo": "retiro"})
    if r.status_code != 201:
        return False
    p = await cliente.post(f"/api/orders/{r.json()['id']}/pay", headers=cab, json={"metodo": "transferencia"})
    return p.status_code == 200


# Procesos del sistema (uvicorn y node) para medir CPU y memoria
def procesos_sistema():
    if psutil is None:
        return []
    encontrados = []
    for p in psutil.process_iter(["cmdline"]):
        cmd = p.info["cmdline"] or []
        if (len(cmd) > 2 and cmd[1:3] == ["-m", "uvicorn"]) or (len(cmd) == 2 and cmd[0].endswith("node") and cmd[1] == "src/server.js"):
            p.cpu_percent(None)
            encontrados.append(p)
    return encontrados


def recursos(procesos, segundos):
    if not procesos:
        return ""
    cpu = sum(p.cpu_percent(None) for p in procesos)
    mem = sum(p.memory_info().rss for p in procesos) / 1048576
    return f"  CPU total={cpu:5.0f}% de {psutil.cpu_count()} núcleos  RAM total={mem:5.0f} MB ({len(procesos)} procesos)"


def resumen(nombre, tiempos, errores, segundos, extra=""):
    tiempos = sorted(tiempos)
    p = lambda q: tiempos[min(len(tiempos) - 1, int(len(tiempos) * q))]
    print(f"{nombre:<26} n={len(tiempos):<6} req/s={len(tiempos) / segundos:7.1f}  p50={p(0.5):6.1f}ms  "
          f"p95={p(0.95):6.1f}ms  p99={p(0.99):6.1f}ms  errores={len(errores)}{extra}")


async def correr(url, concurrencia, segundos):
    limites = httpx.Limits(max_connections=concurrencia * 2)
    async with httpx.AsyncClient(base_url=url, timeout=30.0, limits=limites) as c:
        login = await c.post("/api/auth/login", json={"email": "cliente@masala.cl", "password": "cliente123"})
        cab = {"Authorization": "Bearer " + login.json()["token"]}

        # Stock suficiente para que cada compra de la prueba sea exitosa
        adm = await c.post("/api/auth/login", json={"email": "admin@masala.cl", "password": "admin123"})
        await c.patch("/api/products/naan-extra", json={"stock": 10000}, headers={"Authorization": "Bearer " + adm.json()["token"]})

        escenarios = (("GET /api/products", ver_catalogo),
                      ("GraphQL pedidos agregados", lambda cl: agregacion(cl, cab)),
                      ("crear + pagar pedido", lambda cl: comprar(cl, cab)))

        for nombre, escenario in escenarios:
            tiempos, errores = [], []
            procesos = procesos_sistema()
            fin = time.perf_counter() + segundos
            await asyncio.gather(*[trabajador(c, fin, escenario, tiempos, errores) for _ in range(concurrencia)])
            resumen(nombre, tiempos, errores, segundos, recursos(procesos, segundos))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--concurrencia", type=int, default=20)
    ap.add_argument("--segundos", type=int, default=10)
    a = ap.parse_args()
    asyncio.run(correr(a.url, a.concurrencia, a.segundos))
