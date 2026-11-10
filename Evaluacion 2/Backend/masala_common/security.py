import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException

from . import secrets_store

# Solo estos sistemas pueden informar la identidad de un usuario
IDENTITY_CALLERS = {"gateway", "graphql"}


@dataclass
class Identity:
    id: str
    rol: str
    email: str


@dataclass
class Caller:
    name: str
    identity: Identity | None


# Dependencia que valida quién llama al servicio (si no, 403)
def caller_for(service):
    def dependency(
        x_caller: str = Header(default=""),
        x_caller_secret: str = Header(default=""),
        x_user_id: str = Header(default=""),
        x_user_role: str = Header(default=""),
        x_user_email: str = Header(default="")
    ):
        try:
            callers = secrets_store.get_secrets(service).get("callers", {})
        except secrets_store.SecretsUnavailable:
            raise HTTPException(status_code=500, detail="Secretos no disponibles")

        expected = callers.get(x_caller)

        # Se compara en bytes para que un secreto con tildes dé 403 y no 500
        if not expected or not secrets.compare_digest(
            x_caller_secret.encode(), expected.encode()
        ):
            raise HTTPException(
                status_code=403,
                detail="Llamada no autorizada: debe venir de un sistema autorizado"
            )

        # La identidad solo se acepta de gateway o graphql
        identity = None
        if x_caller in IDENTITY_CALLERS and x_user_id and x_user_role in ("cliente", "admin"):
            identity = Identity(x_user_id, x_user_role, x_user_email)

        return Caller(x_caller, identity)

    return dependency


# Exige un usuario identificado
def need_identity(caller):
    if caller.identity is None:
        raise HTTPException(status_code=401, detail="Autenticación requerida")

    return caller.identity


# Exige un rol concreto
def need_role(caller, rol):
    identity = need_identity(caller)

    if identity.rol != rol:
        raise HTTPException(status_code=403, detail="Rol sin permiso para esta operación")

    return identity


# Exige que llame un servicio concreto (rutas /internal)
def need_service(caller, *names):
    if caller.name not in names:
        raise HTTPException(status_code=403, detail="Sistema sin permiso para esta operación")
