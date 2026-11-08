import hashlib
import os
import secrets
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

# Auth Service: responde "¿quién eres?"
app = FastAPI(
    title="Auth Service - Masala",
    description="Valida credenciales, emite tokens opacos temporales y responde introspección y logout"
)

# Secreto que solo conoce el Gateway (se entrega por variable de entorno, nunca en Git)
AUTH_INTROSPECTION_SECRET = os.getenv("AUTH_INTROSPECTION_SECRET")
# Vida del token en segundos (15 minutos por defecto)
TOKEN_TTL = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "900"))

if not AUTH_INTROSPECTION_SECRET:
    raise RuntimeError("AUTH_INTROSPECTION_SECRET no esta configurado")

# Usuarios de prueba. Solo se guarda el hash PBKDF2 de la contraseña, nunca la contraseña.
#   ana     / ana123      -> rol user
#   ernesto / ernesto123  -> rol admin
ITERACIONES = 200_000
USUARIOS = {
    "ana": {
        "role": "user",
        "salt": "a1e706ecc8687549bb0afaf34b137a6a",
        "hash": "a24d7f6eb4597a39ec05cf448058d10c381fca16eef50b6b2d7a44c9f0030d4a"
    },
    "ernesto": {
        "role": "admin",
        "salt": "072f5567fb1df0780ef86ab6d8fa22d1",
        "hash": "b7c0028f3b26da0687198010d6e99348c40cdfd7c251a91812ce7acafc475608"
    }
}

# Sesiones vivas: token opaco -> {sub, role, exp}
SESIONES: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    token: str


# Hash de contraseña
def hash_password(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), ITERACIONES
    ).hex()


# Solo el Gateway puede llamar /introspect y /logout
def verify_gateway(x_gateway_auth_secret: str = Header(default="")):
    valid = secrets.compare_digest(
        x_gateway_auth_secret.encode(),
        AUTH_INTROSPECTION_SECRET.encode()
    )

    if not valid:
        raise HTTPException(status_code=403, detail="Introspect no lo puede llamar cualquiera")


# Sesión vigente o None (las vencidas se borran)
def sesion_vigente(token: str):
    sesion = SESIONES.get(token)
    if sesion is None:
        return None

    if sesion["exp"] <= time.time():
        SESIONES.pop(token, None)
        return None

    return sesion


# Salud
@app.get("/health")
def health():
    return {"status": "OK", "service": "Auth Service"}


# Login: valida credenciales y emite un token opaco temporal
@app.post("/login")
def login(datos: LoginRequest):
    usuario = USUARIOS.get(datos.username)

    # Se calcula el hash aunque el usuario no exista, para no delatar qué usuarios existen
    salt = usuario["salt"] if usuario else "00" * 16
    esperado = usuario["hash"] if usuario else "00" * 32
    valid = secrets.compare_digest(hash_password(datos.password, salt), esperado)

    if not usuario or not valid:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    token = secrets.token_urlsafe(32)
    SESIONES[token] = {
        "sub": datos.username,
        "role": usuario["role"],
        "exp": time.time() + TOKEN_TTL
    }

    return {
        "access_token": token,
        "token_type": "opaque",
        "expires_in": TOKEN_TTL,
        "username": datos.username,
        "role": usuario["role"]
    }


# Introspección: el Gateway pregunta si el token sigue vigente
@app.post("/introspect", dependencies=[Depends(verify_gateway)])
def introspect(datos: TokenRequest):
    sesion = sesion_vigente(datos.token)

    if sesion is None:
        return {"active": False}

    return {
        "active": True,
        "sub": sesion["sub"],
        "role": sesion["role"],
        "exp": int(sesion["exp"])
    }


# Logout: revoca la sesión del lado del servidor
@app.post("/logout", dependencies=[Depends(verify_gateway)])
def logout(datos: TokenRequest):
    revocado = SESIONES.pop(datos.token, None) is not None
    return {"revoked": revocado}
