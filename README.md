# Masala - Curry & Naan

Masala es una interfaz web frontend responsiva y moderna diseñada para un restaurante especializado en curry y pan naan. El proyecto ofrece una experiencia de usuario fluida y con temática oscura, estructurada en múltiples páginas interconectadas mediante navegación intuitiva y persistencia local de datos.

---

## Caracteristicas Principales

* **Diseno Moderno y Coherente:** Interfaz con temática oscura basada en una paleta de colores cuidadosamente seleccionada (`#010310`, `#23A9BD`, `#8CE1EE`, `#F0F6F8`) y botones con efectos de interacción (*hover*).
* **Pagina de Inicio (`index.html`):** 
  * Cuadrícula asimétrica (*masonry-style*) responsiva en el hero con imágenes de alta calidad.
  * Sección destacada de los productos más vendidos.
* **Carta Dinamica (`carta.html`):**
  * Carrusel de promociones y códigos de descuento en la parte superior (cupones y beneficios bancarios).
  * Menú categorizado en Entradas, Platos Principales y Bebestibles.
  * Modal interactivo de personalización para platos de comida (permite agregar notas de instrucciones especiales como "sin cebolla" o sumar acompañamientos y bebidas mediante controles de cantidad).
  * Controles de cantidad interactivos independientes en la sección de bebestibles.
* **Carrito de Compras Independiente (`carrito.html`):**
  * Resumen detallado de productos con desglose de cantidades y precios totales.
  * Opciones flexibles de entrega: **Retiro en Local ($0)** o **Delivery ($2.000)** con campo dinámico de dirección.
  * Validador interactivo de códigos de descuento (`MASALA20` para un 20% de descuento).
* **Seccion de Ubicacion (`ubicacion.html`):**
  * Información detallada de las sucursales disponibles en Santiago.
* **Autenticacion Simulada (`auth.js`):**
  * Sistema de inicio de sesión y registro de usuarios persistente en el navegador con roles de cliente y administrador.
* **Persistencia de Datos (`localStorage`):**
  * Los productos agregados al carrito, la sesión activa y las cantidades se mantienen sincronizados al navegar entre las distintas páginas del sitio.

---

## Tecnologias Utilizadas

* **HTML5 / CSS3**
* **Bootstrap 5.3.3** (Sistema de grillas, componentes offcanvas, modales, carrusel y tarjetas).
* **Bootstrap Icons** (Iconografía moderna).
* **JavaScript (Vanilla)** (Gestión del carrito de compras, modales interactivos y simulación de autenticación).

---

## Estructura del Proyecto

```text
Frontend/
│
├── index.html       # Página principal con cuadrícula asimétrica y destacados
├── carta.html       # Menú interactivo, carrusel de promos y modal de personalización
├── carrito.html     # Resumen de compras, tipos de entrega y cupones de descuento
├── ubicacion.html   # Información de sucursales físicas
│
├── css/
│   └── estilos.css  # Estilos personalizados y transiciones
│
├── js/
│   ├── main.js      # Inicialización general y control de estado
│   ├── carta.js     # Lógica del modal, complementos y bebestibles
│   ├── carrito.js   # Lógica del almacenamiento local, totales y descuentos
│   └── auth.js      # Sistema de inicio de sesión y registro simulado
│
└── img/             # Directorio de recursos visuales (platos, bebidas, logos)
