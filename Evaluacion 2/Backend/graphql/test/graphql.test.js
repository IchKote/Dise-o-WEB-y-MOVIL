import test from 'node:test';
import assert from 'node:assert/strict';

import { crearServidor, manejar } from '../src/app.js';
import { fijarSecretos } from '../src/secrets.js';
import { llamadorValido, identidadDe } from '../src/caller.js';

const IDENTIDADES = {
  tok_cliente: { id: 'u-cliente', rol: 'cliente', email: 'c@x.cl' },
  tok_admin: { id: 'u-admin', rol: 'admin', email: 'a@x.cl' },
};

const PEDIDO = (id, n) => ({
  id, estado: 'PAGADO', tipo: 'retiro', direccion: null, subtotal: 100, descuento: 0, envio: 0, total: 100,
  codigo: null, creado_en: '2026-11-07T10:00:00Z', user_id: 'u-cliente',
  items: [
    { product_id: 'a', nombre: 'A', precio_unitario: 50, cantidad: 1, subtotal: 50 },
    { product_id: 'b', nombre: 'B', precio_unitario: 50, cantidad: 1, subtotal: 50 },
  ].slice(0, n),
});

// Servicios simulados: registran cada llamada para comprobar el agrupamiento
function simulados({ pagosCaido = false } = {}) {
  const llamadas = [];
  const llamar = async (servicio, metodo, ruta, op = {}) => {
    llamadas.push({ servicio, metodo, ruta, params: op.params, identity: op.identity });

    if (servicio === 'orders' && metodo === 'GET' && ruta === '/') {
      return { status: 200, body: { orders: [PEDIDO('ORD-1', 2), PEDIDO('ORD-2', 2), PEDIDO('ORD-3', 1)] } };
    }
    if (servicio === 'inventory' && ruta === '/products') {
      const ids = op.params.ids.split(',');
      return { status: 200, body: { products: ids.map((id) => ({ id, nombre: id.toUpperCase(), categoria: 'platos', precio: 50, descripcion: '', imagen: '', disponible: true })) } };
    }
    if (servicio === 'payments') {
      if (pagosCaido) return { status: 502, body: { detail: 'payments no disponible' } };
      const ids = op.params.ids.split(',');
      return { status: 200, body: { payments: ids.map((id) => ({ order_id: id, monto: 100, metodo: 'tarjeta', estado: 'APROBADO', ref: 'pay_' + id, firma: 'f' })) } };
    }
    if (servicio === 'clients' && ruta === '/me') {
      return { status: 200, body: { id: op.identity.id, nombre: 'Ana', email: op.identity.email, telefono: null, direcciones: [] } };
    }
    if (servicio === 'clients') {
      return { status: 200, body: { clients: op.params.ids.split(',').map((id) => ({ id, nombre: 'N', email: 'e@x.cl', telefono: null, direcciones: [] })) } };
    }
    if (servicio === 'orders' && metodo === 'POST') return { status: 409, body: { detail: { code: 'STOCK_INSUFICIENTE', product_id: 'a' } } };
    return { status: 404, body: { detail: 'no' } };
  };
  return { llamar, llamadas };
}

async function consulta(query, { token, llamar, variables, server = crearServidor() } = {}) {
  await server.start();
  try {
    const headers = { 'content-type': 'application/json' };
    const r = await manejar(server, { metodo: 'POST', headers, cuerpo: variables ? { query, variables } : { query }, requestId: 'test', llamar, identity: IDENTIDADES[token] || null });
    return { status: r.status, json: JSON.parse(r.body) };
  } finally {
    await server.stop();
  }
}

const LISTA = `{ pedidos { id total items { nombre producto { nombre } } pago { estado ref } } }`;

test('agrupa lecturas: 1 llamada por servicio, sin N+1', async () => {
  const s = simulados();
  const { json } = await consulta(LISTA, { token: 'tok_cliente', llamar: s.llamar });
  assert.equal(json.errors, undefined);
  assert.equal(json.data.pedidos.length, 3);
  assert.equal(json.data.pedidos[0].items[0].producto.nombre, 'A');
  assert.equal(json.data.pedidos[0].pago.ref, 'pay_ORD-1');
  assert.equal(s.llamadas.filter((l) => l.servicio === 'inventory').length, 1);
  assert.equal(s.llamadas.filter((l) => l.servicio === 'payments').length, 1);
  assert.equal(s.llamadas.find((l) => l.servicio === 'inventory').params.ids, 'a,b');
});

test('se reenvía la identidad verificada, no la que diga el cliente', async () => {
  const s = simulados();
  await consulta(LISTA, { token: 'tok_cliente', llamar: s.llamar });
  const orden = s.llamadas.find((l) => l.servicio === 'orders');
  assert.deepEqual(orden.identity, { id: 'u-cliente', rol: 'cliente', email: 'c@x.cl' });
});

test('solo el gateway puede llamar al servicio', () => {
  fijarSecretos({ callers: { gateway: 'secreto-del-gateway' } });
  assert.equal(llamadorValido({ 'x-caller': 'gateway', 'x-caller-secret': 'secreto-del-gateway' }), true);
  assert.equal(llamadorValido({ 'x-caller': 'gateway', 'x-caller-secret': 'otro' }), false);
  assert.equal(llamadorValido({ 'x-caller': 'orders', 'x-caller-secret': 'secreto-del-gateway' }), false);
  assert.equal(llamadorValido({ 'x-caller': 'gateway' }), false);
  assert.equal(llamadorValido({ 'x-caller': 'gateway', 'x-caller-secret': 'secreto-ñ' }), false);
});

test('la identidad solo se arma con rol válido', () => {
  assert.equal(identidadDe({ 'x-user-id': 'u-1', 'x-user-role': 'superadmin' }), null);
  assert.equal(identidadDe({ 'x-user-role': 'admin' }), null);
  assert.deepEqual(identidadDe({ 'x-user-id': 'u-1', 'x-user-role': 'cliente', 'x-user-email': 'a@b.cl' }), { id: 'u-1', rol: 'cliente', email: 'a@b.cl' });
});

test('sin token: pedidos exige login', async () => {
  const s = simulados();
  const { json } = await consulta(LISTA, { llamar: s.llamar });
  assert.equal(json.errors[0].extensions.code, 'UNAUTHENTICATED');
});

test('campo cliente solo para administrador (autorización por campo)', async () => {
  const q = '{ pedidos { id cliente { nombre } } }';
  const comun = await consulta(q, { token: 'tok_cliente', llamar: simulados().llamar });
  assert.equal(comun.json.errors[0].extensions.code, 'FORBIDDEN');
  assert.equal(comun.json.data.pedidos[0].cliente, null);

  const s = simulados();
  const admin = await consulta(q, { token: 'tok_admin', llamar: s.llamar });
  assert.equal(admin.json.errors, undefined);
  assert.equal(admin.json.data.pedidos[0].cliente.nombre, 'N');
  assert.equal(s.llamadas.filter((l) => l.servicio === 'clients').length, 1);
});

test('falla parcial: pagos caído devuelve pedidos con pago null y un error', async () => {
  const { json } = await consulta(LISTA, { token: 'tok_cliente', llamar: simulados({ pagosCaido: true }).llamar });
  assert.equal(json.data.pedidos.length, 3);
  assert.equal(json.data.pedidos[0].pago, null);
  assert.equal(json.data.pedidos[0].total, 100);
  assert.equal(json.errors[0].extensions.code, 'UPSTREAM_UNAVAILABLE');
});

test('mutación: error de negocio llega con código y detalle', async () => {
  const q = `mutation { crearPedido(input: { items: [{ productId: "a", cantidad: 1 }], tipo: "retiro" }) { id } }`;
  const { json } = await consulta(q, { token: 'tok_cliente', llamar: simulados().llamar });
  assert.equal(json.errors[0].extensions.code, 'CONFLICT');
  assert.equal(json.errors[0].extensions.detalle.code, 'STOCK_INSUFICIENTE');
});

test('mutaciones por rol', async () => {
  const s = simulados();
  const admin = await consulta(`mutation { crearPedido(input: { items: [{ productId: "a", cantidad: 1 }], tipo: "retiro" }) { id } }`, { token: 'tok_admin', llamar: s.llamar });
  assert.equal(admin.json.errors[0].extensions.code, 'FORBIDDEN');
  const cliente = await consulta(`mutation { cambiarEstadoPedido(id: "ORD-1", estado: "LISTO") { id } }`, { token: 'tok_cliente', llamar: s.llamar });
  assert.equal(cliente.json.errors[0].extensions.code, 'FORBIDDEN');
  assert.equal(s.llamadas.filter((l) => l.servicio === 'orders' && l.metodo !== 'GET').length, 0);
});

test('límite de profundidad', async () => {
  const normal = '{ pedidos { items { producto { nombre } } } }';
  assert.ok((await consulta(normal, { token: 'tok_cliente', llamar: simulados().llamar })).json.data);

  let abuso = 'nombre';
  for (let i = 0; i < 8; i++) abuso = `producto { ${abuso} }`;
  const r = await consulta(`{ pedidos { items { ${abuso} } } }`, { token: 'tok_cliente', llamar: simulados().llamar });
  assert.ok(r.json.errors);
  assert.match(r.json.errors[0].message, /depth|profundidad/i);
});

test('introspección desactivada por defecto', async () => {
  const { json } = await consulta('{ __schema { types { name } } }', { llamar: simulados().llamar });
  assert.equal(json.errors[0].extensions.code, 'GRAPHQL_VALIDATION_FAILED');
});

test('errores inesperados no filtran detalles', async () => {
  const roto = async (servicio, metodo, ruta) => {
    throw new Error('connection string mongodb://usuario:clave@host');
  };
  const { json } = await consulta('{ pedidos { id } }', { token: 'tok_cliente', llamar: roto });
  assert.equal(json.errors[0].message, 'Error interno del servidor');
  assert.ok(!JSON.stringify(json).includes('mongodb://'));
});

test('límite de costo: demasiados campos', async () => {
  const campos = Array.from({ length: 70 }, (_, i) => `a${i}: id`).join(' ');
  const { json } = await consulta(`{ pedidos { ${campos} } }`, { token: 'tok_cliente', llamar: simulados().llamar });
  assert.match(json.errors[0].message, /demasiados campos/);
});

test('paginación acotada a 50', async () => {
  const s = simulados();
  await consulta('{ pedidos(limit: 5000) { id } }', { token: 'tok_cliente', llamar: s.llamar });
  assert.equal(s.llamadas.find((l) => l.servicio === 'orders').params.limit, '50');
});

test('me responde con la identidad del gateway y sin llamar a auth', async () => {
  const sim = simulados();
  const { json } = await consulta('{ me { id nombre email rol } }', { token: 'tok_cliente', llamar: sim.llamar });
  assert.equal(json.errors, undefined);
  assert.deepEqual(json.data.me, { id: 'u-cliente', nombre: 'Ana', email: 'c@x.cl', rol: 'cliente' });
  assert.ok(sim.llamadas.every((l) => l.servicio === 'clients'));
});
