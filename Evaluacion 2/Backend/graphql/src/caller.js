import crypto from 'node:crypto';

import { secretos } from './secrets.js';

// Solo el API Gateway puede invocar este servicio
export function llamadorValido(headers) {
  const nombre = headers['x-caller'];
  const secreto = headers['x-caller-secret'];
  const esperado = secretos().callers?.[nombre];

  if (!esperado || typeof secreto !== 'string') return false;

  const a = Buffer.from(secreto);
  const b = Buffer.from(esperado);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Identidad ya verificada por el gateway (si la solicitud era anónima, null)
export function identidadDe(headers) {
  const rol = headers['x-user-role'];
  if (!headers['x-user-id'] || !['cliente', 'admin'].includes(rol)) return null;
  return { id: headers['x-user-id'], rol, email: headers['x-user-email'] || '' };
}
