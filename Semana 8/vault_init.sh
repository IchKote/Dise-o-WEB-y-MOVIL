#!/usr/bin/env bash
set -euo pipefail

# Configuración
VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-root-token-masala}"

# Guardar secretos
curl -sS --fail \
  -H "X-Vault-Token: ${VAULT_TOKEN}" \
  -H "Content-Type: application/json" \
  -X POST "${VAULT_ADDR}/v1/secret/data/gateway" \
  -d '{"data": {"client_token": "student-token-123", "backend_shared_secret": "gateway-api-secret-456"}}' \
  > /dev/null

echo "Secretos guardados en secret/gateway (client_token, backend_shared_secret)"
