# PR 9 - Auth Service: cookie HttpOnly, introspección, logout y roles

Sobre el Gateway securitizado de la Semana 8 se agrega un **Auth Service** que responde
"¿quién eres?". El Gateway ya no compara un token fijo: le pregunta al Auth Service, en cada
llamada, si la sesión sigue vigente (introspección).

| Carpeta | Archivo | Puerto | Qué hace |
|---|---|---|---|
| `AuthService` | `auth_service.py` | 8100 | `/login`, `/introspect`, `/logout` |
| `Appgateway` | `gateway.py` | 8000 | `/auth/login`, `/auth/me`, `/auth/logout`, `/api/...` |
| `FastAPI1` | `backend1.py` | 9000 | `/products`, `/orders` (borrar producto: solo admin) |
| `FastAPI2` | `backend2.py` | 9100 | `/productos`, `/pedidos` (borrar producto: solo admin) |
| Vault | `docker-compose.yml` | 8200 | `secret/gateway` |

## Cómo funciona

1. **Login**: `POST /auth/login` en el Gateway. El Auth Service valida la contraseña (hash PBKDF2) y emite un **token opaco temporal** (15 min).
2. **Cookie HttpOnly**: el Gateway guarda el token en la cookie `session_token` (`HttpOnly`, `SameSite=Strict`). El token nunca va en el cuerpo de la respuesta ni en `localStorage`, así que JavaScript no puede leerlo.
3. **Introspección**: en cada `/api/...` el Gateway llama `POST /introspect` del Auth Service. Si responde `active: false`, el Gateway devuelve 401.
4. **Solo el Gateway** puede llamar `/introspect` y `/logout`: exigen la cabecera `X-Gateway-Auth-Secret` con `auth_introspection_secret`. Sin ella responden 403.
5. **Roles**: el Gateway reenvía `X-Authenticated-Client` y `X-Authenticated-Role`. El backend permite borrar solo con rol `admin`. El cliente no puede inyectar esas cabeceras: el Gateway las descarta.
6. **Logout seguro**: `POST /auth/logout` revoca la sesión en el Auth Service y borra la cookie. Después, `/introspect` responde `active: false` y el token copiado ya no sirve.

Usuarios de prueba:

| Usuario | Contraseña | Rol | GET productos | DELETE producto |
|---|---|---|---|---|
| `ana` | `ana123` | user | 200 | 403 |
| `ernesto` | `ernesto123` | admin | 200 | 200 |

| Código | Quién | Cuándo |
|---|---|---|
| 401 | Gateway | Login incorrecto, sin cookie, o sesión revocada/expirada |
| 403 | Backend | Rol sin permiso, o acceso directo sin `X-Gateway-Secret` |
| 403 | Auth Service | `/introspect` o `/logout` sin `X-Gateway-Auth-Secret` |
| 404 | Gateway | Ruta no publicada |
| 500 | Gateway | Vault no disponible o sin los secretos |
| 502 | Gateway | Backend o Auth Service caído |

## Ejecutar (PowerShell)

```
pip install -r requirements.txt
docker compose up -d
$body = '{"data":{"backend_shared_secret":"gateway-api-secret-456","auth_introspection_secret":"auth-introspection-secret-789"}}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8200/v1/secret/data/gateway -Headers @{"X-Vault-Token"="root-token-masala"} -ContentType "application/json" -Body $body
```

En Git Bash/Linux, en vez de las dos últimas líneas: `./vault_init.sh`.

Una terminal por servicio:

```
# AuthService (8100)
$env:AUTH_INTROSPECTION_SECRET="auth-introspection-secret-789"
cd AuthService; uvicorn auth_service:app --port 8100

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

## Probar a mano

`-c` guarda la cookie y `-b` la envía, igual que un navegador:

```
curl.exe -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"ana\",\"password\":\"mala\"}"        # 401
curl.exe -i -c ana.txt -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"ana\",\"password\":\"ana123\"}"   # 200 + Set-Cookie HttpOnly
curl.exe -i -b ana.txt http://localhost:8000/api/products                  # 200
curl.exe -i -b ana.txt -X DELETE http://localhost:8000/api/products/p01    # 403 (Ana es user)

curl.exe -i -c ernesto.txt -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"ernesto\",\"password\":\"ernesto123\"}"
curl.exe -i -b ernesto.txt -X DELETE http://localhost:8000/api/products/p01   # 200 (Ernesto es admin)

curl.exe -i -b ana.txt -c ana.txt -X POST http://localhost:8000/auth/logout   # 200, revoked: true
curl.exe -i -b ana.txt http://localhost:8000/api/products                    # 401
curl.exe -i -X POST http://localhost:8100/introspect -H "Content-Type: application/json" -d "{\"token\":\"x\"}"   # 403
```

En Postman las cookies se guardan solas después del login.

## Pruebas automáticas (pytest)

```
pytest -v tests
```

Levantan todo en memoria (Vault falso incluido), sin Docker ni servidores. Cubren login
incorrecto (401), cookie HttpOnly, Ana leyendo (200) y borrando (403), Ernesto borrando (200),
logout con `active: false`, introspect sin secreto (403), acceso directo al backend (403) y
servicios caídos (500/502).
