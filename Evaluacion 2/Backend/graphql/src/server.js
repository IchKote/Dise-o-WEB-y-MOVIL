import http from 'node:http';
import crypto from 'node:crypto';

import { crearServidor, manejar, MAX_BODY } from './app.js';
import { cargarSecretos } from './secrets.js';
import { llamadorValido, identidadDe } from './caller.js';

const PUERTO = Number(process.env.PORT || 8100);

function responder(res, status, objeto, extra = {}) {
  const texto = typeof objeto === 'string' ? objeto : JSON.stringify(objeto);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'X-Content-Type-Options': 'nosniff',
    'Cache-Control': 'no-store',
    ...extra,
  });
  res.end(texto);
}

async function leerCuerpo(req) {
  const partes = [];
  let total = 0;
  for await (const parte of req) {
    total += parte.length;
    if (total > MAX_BODY) throw Object.assign(new Error('grande'), { grande: true });
    partes.push(parte);
  }
  return Buffer.concat(partes).toString('utf8');
}

await cargarSecretos('graphql');
const apollo = crearServidor();
await apollo.start();

// Servicio privado: sin CORS ni puerto público; solo responde al API Gateway
const servidor = http.createServer(async (req, res) => {
  const requestId = req.headers['x-request-id'] || crypto.randomBytes(6).toString('hex');
  const base = { 'X-Request-Id': requestId };

  try {
    const ruta = new URL(req.url, 'http://x').pathname;

    if (ruta === '/health') return responder(res, 200, { status: 'OK', service: 'graphql' }, base);
    if (ruta !== '/graphql') return responder(res, 404, { detail: 'Ruta no encontrada' }, base);
    if (req.method !== 'POST') return responder(res, 405, { detail: 'Método no permitido' }, base);

    if (!llamadorValido(req.headers)) {
      return responder(res, 403, { detail: 'Llamada no autorizada: debe venir de un sistema autorizado' }, base);
    }

    let cuerpo;
    try {
      cuerpo = JSON.parse(await leerCuerpo(req));
    } catch (e) {
      const status = e.grande ? 413 : 400;
      return responder(res, status, { detail: e.grande ? 'Cuerpo demasiado grande' : 'JSON inválido' }, base);
    }

    const r = await manejar(apollo, {
      metodo: req.method, headers: req.headers, cuerpo, requestId, identity: identidadDe(req.headers),
    });
    console.log(`rid=${requestId} POST /graphql -> ${r.status} caller=${req.headers['x-caller']}`);
    responder(res, r.status, r.body, base);
  } catch (e) {
    console.error(`rid=${requestId} error:`, e?.message);
    responder(res, 500, { errors: [{ message: 'Error interno del servidor', extensions: { code: 'INTERNAL_SERVER_ERROR' } }] }, base);
  }
});

servidor.requestTimeout = 15000;
servidor.listen(PUERTO, process.env.HOST || '0.0.0.0', () => console.log(`GraphQL privado en :${PUERTO}/graphql`));

process.on('SIGTERM', () => servidor.close(() => process.exit(0)));
