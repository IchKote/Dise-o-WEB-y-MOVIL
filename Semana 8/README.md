# PR 8 - Vault y API Gateway securitizado

Sobre el Gateway de la Semana 7:

1. **Vault** (modo desarrollo, puerto 8200) guarda en `secret/gateway` los secretos `client_token` y `backend_shared_secret`. Ningún secreto va en el código ni en Git.
2. **Backends** (`FastAPI1` y `FastAPI2`): leen `INTERNAL_GATEWAY_SECRET` y exigen la cabecera `X-Gateway-Secret` (comparada con `compare_digest`). Si falta o no coincide, responden **403**.
3. **Gateway**: lee el Bearer token con `HTTPBearer(auto_error=False)`, lo compara con `client_token` de Vault y reenvía con `X-Gateway-Secret` y `X-Authenticated-Client`. El cliente nunca conoce el secreto interno.

| Código | Quién | Cuándo |
|---|---|---|
| 401 | Gateway | Falta el token o es inválido |
| 403 | Backend | Acceso directo sin `X-Gateway-Secret` válido |
| 404 | Gateway | Ruta no publicada |
| 500 | Gateway | Vault no disponible o sin los secretos |
| 502 | Gateway | Backend caído |

## Ejecutar (PowerShell)

```
pip install -r requirements.txt
docker compose up -d
$body = '{"data":{"client_token":"student-token-123","backend_shared_secret":"gateway-api-secret-456"}}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8200/v1/secret/data/gateway -Headers @{"X-Vault-Token"="root-token-masala"} -ContentType "application/json" -Body $body
```

En Git Bash/Linux, en vez de las dos últimas líneas: `./vault_init.sh`.

Una terminal por servicio:

```
# FastAPI1 (9000) y FastAPI2 (9100)
$env:INTERNAL_GATEWAY_SECRET="gateway-api-secret-456"
cd FastAPI1; uvicorn backend1:app --port 9000
cd FastAPI2; uvicorn backend2:app --port 9100

# Appgateway (8000)
$env:VAULT_ADDR="http://127.0.0.1:8200"
$env:VAULT_TOKEN="root-token-masala"
cd Appgateway; uvicorn gateway:app --port 8000
```

En Linux/Mac las variables van con `export NOMBRE=valor`.

## Probar

```
curl.exe -i http://localhost:8000/api/products                                                 # 401
curl.exe -i -H "Authorization: Bearer token-falso" http://localhost:8000/api/products          # 401
curl.exe -i -H "Authorization: Bearer student-token-123" http://localhost:8000/api/products    # 200
curl.exe -i -H "Authorization: Bearer student-token-123" http://localhost:8000/api/productos   # 200
curl.exe -i http://localhost:9000/products                                                     # 403
```

Apaga FastAPI 2 para ver 502 en `/api/productos`, o `docker compose stop` para ver 500.
