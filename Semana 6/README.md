# PR 6 - API REST con FastAPI

API REST de solo lectura (puerto 9000) con la carta y los pedidos de Masala.
Es el backend que el API Gateway enruta en la Semana 7.

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/health` | Estado del servicio |
| GET | `/products` | Carta completa (filtro opcional `?categoria=bebestibles`) |
| GET | `/products/{id}` | Un producto, o 404 |
| GET | `/orders` | Todos los pedidos |
| GET | `/orders/{id}` | Un pedido, o 404 |

## Ejecutar

```
python -m venv .venv
.venv\Scripts\activate          (Windows)   |   source .venv/bin/activate   (Linux/Mac)
pip install -r requirements.txt
uvicorn api:app --port 9000 --reload
```

Documentación interactiva: http://localhost:9000/docs

## Probar

```
curl http://localhost:9000/health
curl http://localhost:9000/products
curl "http://localhost:9000/products?categoria=entradas"
curl http://localhost:9000/orders/M-1002
curl -i http://localhost:9000/products/p99        # 404
```
