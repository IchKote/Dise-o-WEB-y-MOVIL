# Validaciones ejecutadas contra el backend en marcha

Ejecución: 2026-11-07 14:43:10 · Gateway: http://127.0.0.1:8000

| ID | Caso | Entrada | Identidad | Resultado esperado | Lo verifica | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|---|
| V1 | Acceso anónimo al catálogo | GET /api/products | anónimo | 200, solo campos públicos (sin stock) | inventory | 200, campos: ['categoria', 'descripcion', 'disponible', 'id', 'imagen', 'nombre', 'precio'] | OK |
| V2 | Operación protegida sin sesión | POST /api/orders | anónimo | 401 | API Gateway | 401 | OK |
| V2b | Token inventado | POST /api/orders | token falso | 401 | Auth Service (vía gateway) | 401 | OK |
| V3 | Administración con rol cliente | DELETE /api/products/naan-extra | cliente | 403 | API Gateway e inventory | 403 | OK |
| V3b | Cambiar estado de cocina como cliente | PATCH /api/orders/{id}/status | cliente | 403 | API Gateway y orders | 403 | OK |
| V4 | Consulta de pedido ajeno | GET /api/orders/ORD-B421C271 | cliente B (no dueño) | 404 sin datos del pedido | orders | 404, cuerpo: Pedido no encontrado | OK |
| V4b | Consulta de pedido propio | GET /api/orders/ORD-B421C271 | cliente A (dueño) | 200 | orders | 200 | OK |
| V4c | Pagar pedido ajeno | POST /api/orders/ORD-B421C271/pay | cliente B | 404 | orders | 404 | OK |
| V5 | Acceso directo a servicios privados sin identidad autorizada | GET directo a cada servicio (sin credencial / identidad falsa) | anónimo | 403 en ambos casos | cada servicio (caller_for) | {'orders': (403, 403), 'inventory': (403, 403), 'payments': (403, 403), 'clients': (403, 403), 'auth': (403, 403)} | OK |
| V5b | Acceso directo al GraphQL Gateway | POST directo a graphql | anónimo | 403 | graphql (llamadorValido) | 403 | OK |
| V6 | Confirmar pago con datos alterados | POST /api/orders/ORD-B421C271/pay con monto=1,total=1,estado=PAGADO | cliente A | se cobra el total del servidor (9500) y el estado lo decide payments | orders + payments | 200, monto cobrado 9500, estado PAGADO | OK |
| V6b | Precio y total enviados por el navegador | POST /api/orders con precio_unitario=1,total=1 | cliente A | total = precio del servidor (2000) | orders + inventory | 2000 | OK |
| V7 | Pago duplicado | POST /api/orders/ORD-B421C271/pay (segunda vez) | cliente A | mismo comprobante, un solo cobro | orders + payments | ref igual: True, cobros: 1 | OK |
| V8 | Recuperación de stock tras pago rechazado | reserva de 3 unidades y pago con tarjeta rechazada | cliente A | stock vuelve al valor inicial | inventory (reserva/liberación) | 59 -> 56 -> 59, pago 402 | OK |
| V9 | Campo GraphQL restringido por rol | { pedidos { cliente { nombre telefono } } } | cliente | FORBIDDEN y cliente = null | graphql (por campo) | ['FORBIDDEN'], cliente null: True | OK |
| V9b | Mismo campo con rol admin | { pedidos { cliente { nombre } } } | admin | datos del cliente, sin errores | graphql | errores: 0 | OK |
| V9c | Límite de profundidad | consulta con 10 niveles | cliente | rechazada en validación | graphql (depthLimit) | '' exceeds maximum operation depth of 6 | OK |
| V9d | Límite de costo (campos) | 70 alias en una consulta | cliente | rechazada en validación | graphql (límite de campos) | La consulta pide demasiados campos (máximo 60) | OK |
| V9e | Introspección desactivada | { __schema { types { name } } } | cliente | rechazada | graphql | True | OK |
| V10 | Agregación orders + inventory + payments | { pedidos { items { producto { disponible } } pago { estado } } } | cliente A | pedido con disponibilidad actual y comprobante en una respuesta | graphql | estado PAGADO, pago APROBADO, disponible True | OK |
