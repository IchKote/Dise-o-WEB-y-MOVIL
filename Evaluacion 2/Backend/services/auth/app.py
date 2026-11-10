import hashlib
import hmac
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel, Field, field_validator
from pymongo.errors import DuplicateKeyError

from masala_common.app import create_app
from masala_common.db import get_db
from masala_common.outbound import Upstream
from masala_common.security import caller_for, need_identity, need_service

SERVICE = "auth"
caller = caller_for(SERVICE)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SESSION_HOURS = 8
MAX_FALLOS = 5
BLOQUEO_MIN = 5


def db():
    return get_db("masala_auth")


def ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Contraseñas: scrypt con sal (hash adaptativo, nunca reversible)
def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def check_password(password, stored):
    try:
        _, n, r, p, salt, digest = stored.split("$")
        calc = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt),
                              n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(calc.hex(), digest)
    except ValueError:
        return False


# Hash de relleno: se compara igual aunque el correo no exista
HASH_FALSO = hash_password("relleno-para-igualar-tiempos")


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class RegisterIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=120)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        if re.search(r"[<>]", v):
            raise ValueError("nombre inválido")
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, v):
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("correo inválido")
        return v


class LoginIn(BaseModel):
    email: str = Field(max_length=120)
    password: str = Field(max_length=128)


class VerifyIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)


# Datos de prueba (ficticios)
async def init():
    await db().users.create_index("email", unique=True)
    await db().sessions.create_index("exp", expireAfterSeconds=0)

    if await db().users.count_documents({}) == 0:
        demo = [
            ("u-admin", "Administrador Masala", "admin@masala.cl", "admin123", "admin"),
            ("u-cliente", "Daniela Jara", "cliente@masala.cl", "cliente123", "cliente"),
        ]
        for uid, nombre, email, password, rol in demo:
            await db().users.insert_one({
                "_id": uid, "nombre": nombre, "email": email, "rol": rol,
                "password_hash": hash_password(password), "activo": True,
                "fallos": 0, "bloqueado_hasta": None, "creado_en": ahora()
            })


app = create_app(SERVICE, "Auth Service - Masala", on_start=init)


def vista(user):
    return {"id": user["_id"], "nombre": user["nombre"], "email": user["email"], "rol": user["rol"]}


# Registro: siempre rol cliente
@app.post("/register", status_code=201)
async def register(body: RegisterIn, c=Depends(caller)):
    need_service(c, "gateway")

    user = {
        "_id": "u-" + secrets.token_hex(8), "nombre": body.nombre.strip(),
        "email": body.email, "rol": "cliente", "activo": True,
        "password_hash": hash_password(body.password),
        "fallos": 0, "bloqueado_hasta": None, "creado_en": ahora()
    }

    try:
        await db().users.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado")

    # Perfil en el servicio clients; si falla, se deshace el registro
    try:
        r = await Upstream(SERVICE, "clients").request(
            "POST", "/internal/clients",
            json={"user_id": user["_id"], "nombre": user["nombre"], "email": user["email"]}
        )
        ok = r.status_code in (200, 201)
    except HTTPException:
        ok = False

    if not ok:
        await db().users.delete_one({"_id": user["_id"]})
        raise HTTPException(status_code=502, detail="No fue posible crear el perfil del cliente")

    return vista(user)


# Login: mismo error para correo o clave incorrectos
@app.post("/login")
async def login(body: LoginIn, c=Depends(caller)):
    need_service(c, "gateway")

    user = await db().users.find_one({"email": body.email.strip().lower()})
    stored = user["password_hash"] if user else HASH_FALSO
    valid = check_password(body.password, stored)

    if user and user.get("bloqueado_hasta") and user["bloqueado_hasta"] > ahora():
        raise HTTPException(status_code=429, detail="Cuenta bloqueada temporalmente, intenta más tarde")

    if not user or not valid or not user["activo"]:
        if user:
            fallos = user.get("fallos", 0) + 1
            cambios = {"fallos": fallos}
            if fallos >= MAX_FALLOS:
                cambios = {"fallos": 0, "bloqueado_hasta": ahora() + timedelta(minutes=BLOQUEO_MIN)}
            await db().users.update_one({"_id": user["_id"]}, {"$set": cambios})
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    await db().users.update_one({"_id": user["_id"]}, {"$set": {"fallos": 0, "bloqueado_hasta": None}})

    # Token opaco: solo se guarda su hash
    token = "mst_" + secrets.token_urlsafe(32)
    exp = ahora() + timedelta(hours=SESSION_HOURS)
    await db().sessions.insert_one({"_id": token_hash(token), "user_id": user["_id"], "exp": exp})

    return {"token": token, "expira": exp.isoformat() + "Z", "usuario": vista(user)}


# Logout: revoca la sesión
@app.post("/logout", status_code=204)
async def logout(c=Depends(caller), x_session_token: str = Header(default="")):
    need_service(c, "gateway")
    await db().sessions.delete_one({"_id": token_hash(x_session_token)})


# Datos de la cuenta autenticada
@app.get("/me")
async def me(c=Depends(caller)):
    identity = need_identity(c)
    user = await db().users.find_one({"_id": identity.id})

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return vista(user)


# Valida un token para el gateway
@app.post("/internal/verify")
async def verify(body: VerifyIn, c=Depends(caller)):
    need_service(c, "gateway")

    session = await db().sessions.find_one({"_id": token_hash(body.token)})
    if not session or session["exp"] <= ahora():
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")

    user = await db().users.find_one({"_id": session["user_id"]})
    if not user or not user["activo"]:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")

    return {"user_id": user["_id"], "rol": user["rol"], "email": user["email"], "nombre": user["nombre"]}
