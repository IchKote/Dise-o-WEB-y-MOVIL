import { ApolloServer, HeaderMap } from '@apollo/server';
import { unwrapResolverError } from '@apollo/server/errors';
import { ApolloServerPluginLandingPageDisabled } from '@apollo/server/plugin/disabled';
import depthLimit from 'graphql-depth-limit';
import { Kind } from 'graphql';
import { GraphQLError } from 'graphql';

import { typeDefs } from './schema.js';
import { resolvers, crearLoaders } from './resolvers.js';
import { llamar as llamarReal } from './upstream.js';

const MAX_BODY = 64 * 1024;
const MAX_DEPTH = 6;
const MAX_CAMPOS = 60;

// Costo: máximo de campos pedidos en un documento (los alias también cuentan)
function limiteCampos(contexto) {
  let total = 0;
  return {
    [Kind.FIELD]() {
      total += 1;
      if (total === MAX_CAMPOS + 1) {
        contexto.reportError(new GraphQLError(`La consulta pide demasiados campos (máximo ${MAX_CAMPOS})`));
      }
    },
  };
}
const CODIGOS_PUBLICOS = new Set([
  'UNAUTHENTICATED', 'FORBIDDEN', 'NOT_FOUND', 'BAD_USER_INPUT', 'CONFLICT', 'PAYMENT_REJECTED',
  'TOO_MANY_REQUESTS', 'UPSTREAM_UNAVAILABLE', 'UPSTREAM_TIMEOUT', 'GRAPHQL_VALIDATION_FAILED',
  'GRAPHQL_PARSE_FAILED', 'PERSISTED_QUERY_NOT_FOUND',
]);

// Errores inesperados se ocultan: el detalle queda solo en el log
function formatError(formatted, original) {
  const code = formatted.extensions?.code;
  if (CODIGOS_PUBLICOS.has(code)) {
    const { stacktrace, ...extensions } = formatted.extensions;
    return { ...formatted, extensions };
  }

  const interno = unwrapResolverError(original);
  console.error('error interno:', interno?.message);
  return {
    message: 'Error interno del servidor',
    path: formatted.path,
    extensions: { code: 'INTERNAL_SERVER_ERROR' },
  };
}

export function crearServidor({ introspection = process.env.GRAPHQL_INTROSPECTION === 'true' } = {}) {
  return new ApolloServer({
    typeDefs,
    resolvers,
    introspection,
    csrfPrevention: true,
    includeStacktraceInErrorResponses: false,
    validationRules: [depthLimit(MAX_DEPTH), limiteCampos],
    plugins: [ApolloServerPluginLandingPageDisabled()],
    formatError,
  });
}

// Procesa una solicitud HTTP ya leída: devuelve { status, headers, body }
export async function manejar(server, { metodo, headers, cuerpo, requestId, identity = null, llamar = llamarReal }) {
  const mapa = new HeaderMap();
  for (const [k, v] of Object.entries(headers)) mapa.set(k, String(v));

  const respuesta = await server.executeHTTPGraphQLRequest({
    httpGraphQLRequest: { method: metodo.toUpperCase(), headers: mapa, search: '', body: cuerpo },
    context: async () => {
      const ctx = { llamar, requestId, identity };
      ctx.loaders = crearLoaders(ctx);
      return ctx;
    },
  });

  const cab = Object.fromEntries(respuesta.headers);
  const cuerpoTexto = respuesta.body.kind === 'complete' ? respuesta.body.string : '';
  return { status: respuesta.status ?? 200, headers: cab, body: cuerpoTexto };
}

export { MAX_BODY, GraphQLError };
