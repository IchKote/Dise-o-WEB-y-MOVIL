import { secretos } from './secrets.js';
import { error } from './errores.js';

const URLS = {
  auth: process.env.AUTH_URL || 'http://auth:8000',
  clients: process.env.CLIENTS_URL || 'http://clients:8000',
  inventory: process.env.INVENTORY_URL || 'http://inventory:8000',
  orders: process.env.ORDERS_URL || 'http://orders:8000',
  payments: process.env.PAYMENTS_URL || 'http://payments:8000',
};
const TIMEOUT_MS = Number(process.env.UPSTREAM_TIMEOUT_MS || 5000);

// Llamada a un servicio interno con la credencial de graphql (y la identidad ya verificada)
export async function llamar(servicio, metodo, ruta, { identity, body, params, requestId, headers } = {}) {
  const secreto = secretos().outbound?.[servicio];
  if (!secreto) throw error('Credencial de integración no configurada', 'INTERNAL_SERVER_ERROR');

  const cab = {
    'X-Caller': 'graphql',
    'X-Caller-Secret': secreto,
    'X-Request-Id': requestId || '',
    ...(headers || {}),
  };

  if (identity) {
    cab['X-User-Id'] = identity.id;
    cab['X-User-Role'] = identity.rol;
    cab['X-User-Email'] = identity.email;
  }
  if (body !== undefined) cab['Content-Type'] = 'application/json';

  const query = params ? '?' + new URLSearchParams(params).toString() : '';

  try {
    const r = await fetch(URLS[servicio] + ruta + query, {
      method: metodo,
      headers: cab,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    const texto = await r.text();
    let json = null;
    try {
      json = texto ? JSON.parse(texto) : null;
    } catch {
      json = null;
    }
    return { status: r.status, body: json };
  } catch (e) {
    if (e.name === 'TimeoutError') throw error(`${servicio} no respondió a tiempo`, 'UPSTREAM_TIMEOUT');
    throw error(`${servicio} no disponible`, 'UPSTREAM_UNAVAILABLE');
  }
}
