export const typeDefs = `#graphql
  type Usuario {
    id: ID!
    nombre: String!
    email: String!
    rol: String!
  }

  type Cliente {
    id: ID!
    nombre: String!
    email: String!
    telefono: String
    direcciones: [String!]!
  }

  type Producto {
    id: ID!
    nombre: String!
    categoria: String!
    precio: Int!
    descripcion: String!
    imagen: String!
    disponible: Boolean!
    "Solo administrador"
    stock: Int
  }

  type Pago {
    orderId: ID!
    monto: Int!
    metodo: String!
    estado: String!
    ref: String!
    firma: String!
  }

  type ItemPedido {
    productId: ID!
    nombre: String!
    precioUnitario: Int!
    cantidad: Int!
    subtotal: Int!
    "Datos actuales del producto (puede ser null si se retiró de la carta)"
    producto: Producto
  }

  type Pedido {
    id: ID!
    estado: String!
    tipo: String!
    direccion: String
    items: [ItemPedido!]!
    subtotal: Int!
    descuento: Int!
    envio: Int!
    total: Int!
    codigo: String
    notas: String
    creadoEn: String!
    "Solo administrador"
    cliente: Cliente
    "Comprobante; si el servicio de pagos falla, llega null junto con el error"
    pago: Pago
  }

  input ItemInput {
    productId: ID!
    cantidad: Int!
  }

  input CrearPedidoInput {
    items: [ItemInput!]!
    tipo: String!
    direccion: String
    codigo: String
  }

  type Query {
    productos(categoria: String, disponible: Boolean): [Producto!]!
    producto(id: ID!): Producto
    me: Usuario
    pedidos(estado: String, limit: Int = 20, offset: Int = 0): [Pedido!]!
    pedido(id: ID!): Pedido
    clientes(limit: Int = 20, offset: Int = 0): [Cliente!]!
  }

  type Mutation {
    crearPedido(input: CrearPedidoInput!, idempotencyKey: String): Pedido!
    pagarPedido(id: ID!, metodo: String!, token: String): Pedido!
    cancelarPedido(id: ID!): Pedido!
    cambiarEstadoPedido(id: ID!, estado: String!): Pedido!
  }
`;
