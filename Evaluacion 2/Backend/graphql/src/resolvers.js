import DataLoader from 'dataloader';

import { deUpstream, error, exigirLogin, exigirRol } from './errores.js';

const ok = (res) => res.status >= 200 && res.status < 300;

// Paginación acotada
const pagina = (limit, offset) => ({
  limit: String(Math.min(Math.max(limit ?? 20, 1), 50)),
  offset: String(Math.max(offset ?? 0, 0)),
});

// Cada solicitud tiene sus propios loaders: agrupan muchas lecturas en una sola llamada
export function crearLoaders(ctx) {
  const por = (servicio, ruta, clave, campo) => async (ids) => {
    const res = await ctx.llamar(servicio, 'GET', ruta, {
      identity: ctx.identity, requestId: ctx.requestId, params: { ids: ids.join(','), limit: '100' },
    });
    if (!ok(res)) throw deUpstream(res);

    const lista = res.body[clave];
    const mapa = new Map(lista.map((x) => [x[campo], x]));
    return ids.map((id) => mapa.get(id) ?? null);
  };

  return {
    productos: new DataLoader(por('inventory', '/products', 'products', 'id'), { maxBatchSize: 50 }),
    clientes: new DataLoader(por('clients', '/', 'clients', 'id'), { maxBatchSize: 50 }),
    pagos: new DataLoader(por('payments', '/', 'payments', 'order_id'), { maxBatchSize: 50 }),
  };
}

const producto = (p) => p && ({ ...p });
const pedido = (o) => ({
  ...o,
  creadoEn: o.creado_en,
  _userId: o.user_id,
  items: o.items.map((i) => ({ ...i, productId: i.product_id, precioUnitario: i.precio_unitario })),
});
const pago = (p) => p && ({ ...p, orderId: p.order_id });
const cliente = (c) => c && ({ ...c });

async function pedir(ctx, servicio, metodo, ruta, opciones = {}) {
  const res = await ctx.llamar(servicio, metodo, ruta, {
    identity: ctx.identity, requestId: ctx.requestId, ...opciones,
  });
  if (!ok(res)) throw deUpstream(res);
  return res.body;
}

export const resolvers = {
  Query: {
    productos: async (_, { categoria, disponible }, ctx) => {
      const params = {};
      if (categoria) params.categoria = categoria;
      if (disponible !== undefined && disponible !== null) params.available = String(disponible);
      const data = await pedir(ctx, 'inventory', 'GET', '/products', { params });
      return data.products.map(producto);
    },
    producto: async (_, { id }, ctx) => {
      const res = await ctx.llamar('inventory', 'GET', `/products/${encodeURIComponent(id)}`, {
        identity: ctx.identity, requestId: ctx.requestId,
      });
      if (res.status === 404) return null;
      if (!ok(res)) throw deUpstream(res);
      return producto(res.body);
    },
    me: async (_, __, ctx) => {
      exigirLogin(ctx);
      // Nombre desde clients; el rol viene de la identidad verificada por el gateway
      const c = await pedir(ctx, 'clients', 'GET', '/me');
      return { id: ctx.identity.id, nombre: c.nombre, email: c.email, rol: ctx.identity.rol };
    },
    pedidos: async (_, { estado, limit, offset }, ctx) => {
      exigirLogin(ctx);
      const params = pagina(limit, offset);
      if (estado) params.estado = estado;
      const data = await pedir(ctx, 'orders', 'GET', '/', { params });
      return data.orders.map(pedido);
    },
    pedido: async (_, { id }, ctx) => {
      exigirLogin(ctx);
      const res = await ctx.llamar('orders', 'GET', `/${encodeURIComponent(id)}`, {
        identity: ctx.identity, requestId: ctx.requestId,
      });
      if (res.status === 404) return null;
      if (!ok(res)) throw deUpstream(res);
      return pedido(res.body);
    },
    clientes: async (_, { limit, offset }, ctx) => {
      exigirRol(ctx, 'admin');
      const data = await pedir(ctx, 'clients', 'GET', '/', { params: pagina(limit, offset) });
      return data.clients.map(cliente);
    },
  },

  Mutation: {
    crearPedido: async (_, { input, idempotencyKey }, ctx) => {
      exigirRol(ctx, 'cliente');
      const body = {
        items: input.items.map((i) => ({ product_id: i.productId, cantidad: i.cantidad })),
        tipo: input.tipo, direccion: input.direccion, codigo: input.codigo,
      };
      const headers = idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : undefined;
      return pedido(await pedir(ctx, 'orders', 'POST', '/', { body, headers }));
    },
    pagarPedido: async (_, { id, metodo, token }, ctx) => {
      exigirRol(ctx, 'cliente');
      return pedido(await pedir(ctx, 'orders', 'POST', `/${encodeURIComponent(id)}/pay`, { body: { metodo, token } }));
    },
    cancelarPedido: async (_, { id }, ctx) => {
      exigirLogin(ctx);
      return pedido(await pedir(ctx, 'orders', 'POST', `/${encodeURIComponent(id)}/cancel`));
    },
    cambiarEstadoPedido: async (_, { id, estado }, ctx) => {
      exigirRol(ctx, 'admin');
      return pedido(await pedir(ctx, 'orders', 'PATCH', `/${encodeURIComponent(id)}/status`, { body: { estado } }));
    },
  },

  Pedido: {
    cliente: async (o, _, ctx) => {
      exigirRol(ctx, 'admin');
      return cliente(await ctx.loaders.clientes.load(o._userId));
    },
    pago: async (o, _, ctx) => pago(await ctx.loaders.pagos.load(o.id)),
  },

  ItemPedido: {
    producto: async (i, _, ctx) => producto(await ctx.loaders.productos.load(i.productId)),
  },
};

export { error };
