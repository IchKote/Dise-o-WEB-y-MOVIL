import { GraphQLError } from 'graphql';

// Código GraphQL según la respuesta HTTP del servicio interno
const CODIGOS = {
  400: 'BAD_USER_INPUT',
  401: 'UNAUTHENTICATED',
  402: 'PAYMENT_REJECTED',
  403: 'FORBIDDEN',
  404: 'NOT_FOUND',
  409: 'CONFLICT',
  429: 'TOO_MANY_REQUESTS',
};

export function error(mensaje, code, extra = {}) {
  return new GraphQLError(mensaje, { extensions: { code, ...extra } });
}

function texto(detalle) {
  if (typeof detalle === 'string') return detalle;
  if (detalle && typeof detalle === 'object' && detalle.code) return detalle.code;
  return 'Solicitud no válida';
}

// Convierte una respuesta de error de un servicio en un GraphQLError
export function deUpstream(res) {
  const code = CODIGOS[res.status];

  if (!code) return error('Servicio interno no disponible', 'UPSTREAM_UNAVAILABLE');

  const detalle = res.body?.detail;
  const extra = detalle && typeof detalle === 'object' ? { detalle } : {};
  return error(texto(detalle), code, extra);
}

export const exigirLogin = (ctx) => {
  if (!ctx.identity) throw error('Autenticación requerida', 'UNAUTHENTICATED');
  return ctx.identity;
};

export const exigirRol = (ctx, rol) => {
  const identity = exigirLogin(ctx);
  if (identity.rol !== rol) throw error('Rol sin permiso para esta operación', 'FORBIDDEN');
  return identity;
};
