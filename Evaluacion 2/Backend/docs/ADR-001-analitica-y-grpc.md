# ADR-001: No se implementan analítica ni gRPC en esta versión

Estado: aceptada · Fecha: 2026-11-07 · Alcance: módulo 9

## Contexto

Llamadas internas hoy: orders→inventory (reserva y liberación de stock), orders→payments (cobro y reembolso), auth→clients (perfil al registrarse), gateway→servicios y graphql→servicios (atender al navegador). El caso no incluye seguimiento en vivo de despacho ni reportes masivos.

## Matriz de necesidades

Los valores de carga son **proyección** (supuestos del equipo), salvo donde se indica **medición**.

| Aspecto | Valor | Origen |
|---|---|---|
| Pedidos | 200 al día; 50 en la hora punta (0,014 pedidos/s) | proyección |
| Consultas de carta | 20 por pedido en la hora punta (≈ 0,3 req/s) | proyección |
| Tamaño de mensajes internos | 0,6 KB (reserva de 10 ítems) a 6,7 KB (carta de 30 productos) | medición |
| Streaming | no hay flujo que lo necesite: el estado del pedido se consulta al abrir la pantalla | requisito del caso |
| Volumen de datos | unos 73.000 pedidos al año a la tasa proyectada; una agregación mensual lee ~6.000 documentos | proyección |
| Latencia objetivo | catálogo p95 < 300 ms; crear + pagar p95 < 1 s | objetivo del equipo |
| Retraso aceptado en reportes | consulta bajo demanda, sin retraso | decisión |

## Mediciones (reproducibles)

Entorno: máquina virtual de 2 vCPU y 8 GB (Intel Xeon 2,1 GHz), Python 3.13, Node 22, los 7 procesos del sistema y el generador de carga en la misma máquina, MongoDB **simulado en memoria** (mongomock), sistema recién iniciado con datos semilla, 15 s por escenario. Sirven para comparar órdenes de magnitud; no son cifras de producción.

| Escenario | Usuarios | req/s | p50 | p95 | p99 | Errores | CPU (de 2 núcleos) | RAM |
|---|---|---|---|---|---|---|---|---|
| `GET /api/products` | 5 | 299 | 16 ms | 25 ms | 28 ms | 0 | 122 % | 441 MB |
| `GET /api/products` | 20 | 261 | 70 ms | 139 ms | 186 ms | 0 | 132 % | 443 MB |
| GraphQL pedidos agregados | 5 | 153 | 32 ms | 46 ms | 55 ms | 0 | 142 % | 495 MB |
| GraphQL pedidos agregados | 20 | 143 | 131 ms | 226 ms | 289 ms | 0 | 148 % | 508 MB |
| crear + pagar pedido | 5 | 52 | 96 ms | 130 ms | 159 ms | 0 | 156 % | 508 MB |
| crear + pagar pedido | 20 | 60 | 328 ms | 464 ms | 551 ms | 0 | 169 % | 522 MB |

Serialización JSON (`scripts/bench_json.py`): 80 µs la carta de 30 productos (6,7 KB) y 10 µs la reserva de 10 ítems (0,6 KB), ida y vuelta.

Archivos: `docs/evidencias/carga-5-usuarios.txt`, `carga-20-usuarios.txt`, `bench-json.txt`.

## Lectura

- Con 20 usuarios simultáneos todos los escenarios cumplen los objetivos de latencia, con 0 errores. La carga proyectada de la hora punta es unas 4.000 veces menor que el flujo de compra medido (≈ 60 flujos/s frente a 0,014 pedidos/s).
- La serialización JSON representa menos del 0,5 % de la latencia de una solicitud (80 µs contra 16–70 ms). Si un protocolo binario la redujera a cero, la mejora máxima sería esa fracción: es una cota superior calculada, **no una medición de gRPC**, que no se implementó.
- Lo que sí mejoró la latencia fue reutilizar conexiones HTTP entre servicios: `GET /api/products` pasó de 46 a 235 req/s en pruebas previas en esta misma máquina. Es una mejora de REST y ya está aplicada.
- El procesamiento se concentra en CPU de Python y en la base de datos, que gRPC no cambia.

## Decisión

1. **gRPC: no se implementa.** No hay streaming, los mensajes son de menos de 7 KB y la serialización es una fracción mínima de la latencia. Se mantiene REST/JSON con conexiones persistentes, credencial por par de servicios y `X-Request-Id`.
2. **Servicio de analítica: no se implementa.** Los reportes que el caso permite (ventas por día, productos más pedidos) se resuelven con una agregación de MongoDB sobre `orders`, en el propio servicio de pedidos, y leen del orden de miles de documentos. No se justifica un subsistema separado ni procesamiento masivo.
3. **GraphQL sí está implementado** (módulo 8) para las agregaciones que necesita el frontend.

## Consecuencias

- Un solo estilo de contrato (OpenAPI de FastAPI), depurable con `curl` y logs legibles.
- No se afirma mejora de rendimiento por gRPC; tampoco se descarta si cambian los supuestos.
- La pantalla de reportes del administrador no existe en el frontend (brecha declarada en el informe).

## Cuándo reconsiderarlo

Un servicio interno supera 500 req/s sostenidos con p95 dominado por serialización o apertura de conexiones; aparece streaming (por ejemplo seguimiento en vivo del despacho hacia cocina); o el volumen de pedidos pasa de ~1 millón de documentos y las agregaciones superan el retraso aceptado. En esos casos: medir de nuevo y, si procede, crear un servicio de analítica privado que lea de réplicas, y contratos `.proto` con deadlines y TLS mutuo.

## Reproducir

```
python scripts/bench_json.py
python scripts/run_local.py
python scripts/load_test.py --concurrencia 20 --segundos 15
```
