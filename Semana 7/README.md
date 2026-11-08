# PR 7 - API Gateway (solo enrutamiento)

El Gateway (puerto 8000) es el único punto de entrada: recibe `/api/...` y reenvía cada ruta
al backend que corresponde. En esta semana no hay Vault ni tokens.

| Carpeta | Archivo | Puerto | Rutas propias | Ruta en el Gateway |
|---|---|---|---|---|
| `FastAPI1` | `backend1.py` | 9000 | `/health`, `/products`, `/orders` | `/api/products`, `/api/orders` |
| `FastAPI2` | `backend2.py` | 9100 | `/health`, `/productos`, `/pedidos` (misma API en español) | `/api/productos`, `/api/pedidos` |
| `Appgateway` | `gateway.py` | 8000 | `/health`, `/api/...` | |

| Código | Cuándo |
|---|---|
| 404 | Ruta no publicada en el Gateway |
| 502 | El backend está caído |
| 504 | El backend tardó más de 10 s |

## Ejecutar

```
python -m venv .venv
.venv\Scripts\activate          (Windows)   |   source .venv/bin/activate   (Linux/Mac)
pip install -r requirements.txt
```

Una terminal por servicio (con el entorno activo):

```
cd FastAPI1   && uvicorn backend1:app --port 9000
cd FastAPI2   && uvicorn backend2:app --port 9100
cd Appgateway && uvicorn gateway:app --port 8000
```

## Probar

```
curl http://localhost:8000/api/products            # FastAPI 1
curl http://localhost:8000/api/orders/M-1002       # FastAPI 1
curl http://localhost:8000/api/productos           # FastAPI 2
curl http://localhost:8000/api/pedidos/M-1003      # FastAPI 2
curl -i http://localhost:8000/api/clientes         # 404: ruta no publicada
```

Apaga FastAPI 2: `/api/productos` responde 502 y `/api/products` sigue en 200.
