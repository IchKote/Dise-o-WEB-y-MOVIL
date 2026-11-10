import json
import secrets
import sys

# Quién puede llamar a quién: {servicio destino: [llamadores]}
PERMITIDOS = {
    "auth": ["gateway"],
    "graphql": ["gateway"],
    "clients": ["gateway", "graphql", "auth"],
    "inventory": ["gateway", "graphql", "orders"],
    "orders": ["gateway", "graphql"],
    "payments": ["gateway", "graphql", "orders"],
}
SISTEMAS = ["gateway", *PERMITIDOS]


# Un secreto distinto por cada par llamador -> destino
def generar():
    data = {s: {"callers": {}, "outbound": {}} for s in SISTEMAS}

    for destino, llamadores in PERMITIDOS.items():
        for llamador in llamadores:
            valor = secrets.token_urlsafe(32)
            data[destino]["callers"][llamador] = valor
            data[llamador]["outbound"][destino] = valor

    data["payments"]["signing_key"] = secrets.token_urlsafe(48)
    return data


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "secrets.generated.json"
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(generar(), f, indent=2)
    print(f"Secretos de desarrollo escritos en {destino}")
