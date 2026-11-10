import json
import timeit

producto = {"id": "chicken-tikka-masala", "nombre": "Chicken Tikka Masala", "categoria": "platos", "precio": 9500,
            "descripcion": "Pollo marinado en salsa cremosa de tomate y especias.", "imagen": "img/plato1.jpg",
            "disponible": True}
carta = {"products": [producto] * 30}
pedido = {"order_id": "ORD-1A2B3C4D", "items": [{"product_id": "chicken-tikka-masala", "cantidad": 2}] * 10}

for nombre, dato in (("carta de 30 productos", carta), ("reserva de 10 ítems", pedido)):
    n = 20000
    t = timeit.timeit(lambda: json.loads(json.dumps(dato)), number=n) / n * 1e6
    print(f"{nombre:<24} {len(json.dumps(dato)):>5} bytes   ida y vuelta JSON: {t:6.1f} us")
