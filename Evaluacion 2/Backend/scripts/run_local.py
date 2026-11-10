import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from credentials import generar  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Puertos locales de cada sistema
PUERTOS = {"gateway": 8000, "auth": 9001, "clients": 9002, "inventory": 9003, "orders": 9004, "payments": 9005}
MODULOS = {"gateway": "gateway.app:app", **{s: f"services.{s}.app:app" for s in PUERTOS if s != "gateway"}}


def main():
    datos = generar()
    urls = {f"{s.upper()}_URL": f"http://127.0.0.1:{p}" for s, p in PUERTOS.items()}
    urls["GRAPHQL_URL"] = "http://127.0.0.1:8100"
    procesos = []

    try:
        for sistema, puerto in PUERTOS.items():
            env = {**os.environ, **urls,
                   "SERVICE_SECRETS": json.dumps(datos[sistema]),
                   "MONGO_URL": os.getenv("MONGO_URL", "mongomock://"),
                   "RATE_LIMIT": os.getenv("RATE_LIMIT", "120"),
                   "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080,http://localhost,http://127.0.0.1")}
            env.pop("VAULT_ADDR", None)
            procesos.append(subprocess.Popen(
                [sys.executable, "-m", "uvicorn", MODULOS[sistema], "--host", "127.0.0.1", "--port", str(puerto), "--log-level", "warning", "--no-server-header"],
                cwd=RAIZ, env=env))

        # GraphQL (Node): solo si se instalaron sus dependencias
        if os.path.isdir(os.path.join(RAIZ, "graphql", "node_modules")):
            env = {**os.environ, **urls, "SERVICE_SECRETS": json.dumps(datos["graphql"]), "PORT": "8100", "HOST": "127.0.0.1"}
            env.pop("VAULT_ADDR", None)
            procesos.append(subprocess.Popen(["node", "src/server.js"], cwd=os.path.join(RAIZ, "graphql"), env=env))

        print("Sistemas en marcha. REST: http://127.0.0.1:8000  GraphQL: vía REST en /api/graphql  (Ctrl+C para detener)")
        while all(p.poll() is None for p in procesos):
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procesos:
            p.terminate()


if __name__ == "__main__":
    main()
