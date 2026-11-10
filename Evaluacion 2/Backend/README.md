# Backend Masala

Servicios FastAPI + MongoDB detrás de un API Gateway, con un gateway GraphQL (Node/Apollo). Secretos en Vault.

```
Cliente → gateway :8000 → auth · clients · inventory · orders · payments → MongoDB
                          └→ graphql (privado) → clients · inventory · orders · payments
```

## Sin Docker (rápido)

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
cd graphql
npm install
cd ..
.venv\Scripts\python.exe scripts\run_local.py
```

Usa MongoDB en memoria y secretos generados al arrancar. Todo entra por `http://127.0.0.1:8000/api` (REST y `POST /api/graphql`); GraphQL no se expone al exterior.

## Con Docker (Vault + MongoDB reales)

```powershell
docker compose up --build
```

Levanta el backend: Vault, MongoDB, los cinco servicios, GraphQL y el gateway en `http://localhost:8000/api`.

## Pruebas

```powershell
.venv\Scripts\python.exe -m pytest
cd graphql
npm test
cd ..
.venv\Scripts\python.exe scripts\e2e_live.py
```

## Pedidos sin pagar

Un pedido que no se paga en 15 minutos se cancela solo (con 1 minuto de gracia) y su stock vuelve al inventario. Lo hace una tarea periódica del servicio `orders` que corre cada 60 segundos; el intervalo se cambia con la variable `BARRIDO_SEGUNDOS` (0 la desactiva). El mismo barrido reintenta las liberaciones de stock que hayan fallado.

## Cuentas de prueba

- `admin@masala.cl` / `admin123`
- `cliente@masala.cl` / `cliente123`
- Pago rechazado de prueba: token `tok_rechazada`.

## Rutas

| Ruta | Acceso |
|---|---|
| `POST /api/auth/register`, `/login` | público |
| `GET /api/products[/{id}]` | público |
| `POST/PUT/PATCH/DELETE /api/products` | admin |
| `POST /api/orders`, `/{id}/pay` | cliente |
| `GET /api/orders[/{id}]`, `POST /{id}/cancel` | dueño o admin |
| `PATCH /api/orders/{id}/status` | admin |
| `GET /api/payments[/{id}]` | dueño o admin |
| `GET/PUT /api/clients/me` · `GET /api/clients` | usuario · admin |

Decisión sobre analítica y gRPC: `docs/ADR-001-analitica-y-grpc.md`.
