// Secretos del sistema graphql: Vault, o SERVICE_SECRETS (JSON) si no hay Vault
let datos = null;

export function fijarSecretos(valor) {
  datos = valor;
}

export function secretos() {
  if (!datos) throw new Error('Secretos no cargados');
  return datos;
}

export async function cargarSecretos(servicio = 'graphql') {
  const addr = process.env.VAULT_ADDR;
  const token = process.env.VAULT_TOKEN;

  if (addr && token) {
    const r = await fetch(`${addr}/v1/secret/data/${servicio}`, {
      headers: { 'X-Vault-Token': token },
      signal: AbortSignal.timeout(5000),
    });
    if (!r.ok) throw new Error('No fue posible leer Vault');
    datos = (await r.json()).data.data;
  } else if (process.env.SERVICE_SECRETS) {
    datos = JSON.parse(process.env.SERVICE_SECRETS);
  } else {
    throw new Error('Sin Vault ni SERVICE_SECRETS');
  }

  return datos;
}
