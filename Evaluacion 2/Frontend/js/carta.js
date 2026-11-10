// ============================================
// CARTA.JS - Lógica del modal de personalización de platos
// Depende de: carrito.js (usa agregarAlCarrito)
// ============================================

let productoActual = null; // { nombre, precioBase, img }

let extrasDisponibles = {
    bebidaLata: { nombre: "Bebida Lata 350ml", precio: 2100, cantidad: 0 },
    naanExtra: { nombre: "Pan Naan Extra", precio: 2000, cantidad: 0 }
};

// --- Cantidades de las tarjetas de bebestibles (sección "Bebestibles") ---
// Son independientes del modal de personalización: se agregan directo al carrito.
let cantidadesCarta = {
    limonada: 1,
    bebidaLata: 1
};

// --- Sumar/restar cantidad en una tarjeta de bebestible ---
function cambiarCantCarta(id, delta) {
    let actual = cantidadesCarta[id] || 1;
    let nueva = Math.max(1, actual + delta);
    cantidadesCarta[id] = nueva;

    let span = document.getElementById(`carta-cant-${id}`);
    if (span) span.innerText = nueva;
}

// --- Agregar una bebida directamente al carrito, sin pasar por el modal ---
function agregarBebidaCarta(nombre, precio, id, imagen) {
    let cantidad = cantidadesCarta[id] || 1;

    agregarAlCarrito({
        nombre: nombre,
        precio: precio,
        cantidad: cantidad,
        observaciones: "",
        extras: [],
        imagen: imagen || ""
    });

    // Reiniciamos el contador visual de la tarjeta a 1
    cantidadesCarta[id] = 1;
    let span = document.getElementById(`carta-cant-${id}`);
    if (span) span.innerText = 1;

    alert(`"${nombre}" (x${cantidad}) se agregó al carrito.`);
}

// --- Abrir el modal con los datos del plato seleccionado ---
function abrirPersonalizador(nombre, precio, img) {
    productoActual = { nombre, precioBase: precio, img };

    // Reiniciamos extras y observaciones cada vez que se abre el modal
    for (let key in extrasDisponibles) {
        extrasDisponibles[key].cantidad = 0;
        document.getElementById(`cant-modal-${key}`).innerText = "0";
    }
    document.getElementById("observaciones").value = "";

    document.getElementById("modal-titulo").innerText = nombre;
    document.getElementById("modal-img").src = img;
    document.getElementById("modal-img").alt = nombre;
    document.getElementById("modal-precio").innerText = "$" + precio.toLocaleString();

    actualizarTotalModal();

    let modal = new bootstrap.Modal(document.getElementById("modalPersonalizar"));
    modal.show();
}

// --- Sumar/restar cantidad de un extra (bebida, pan, etc.) ---
function cambiarCantidadModal(idExtra, delta) {
    let extra = extrasDisponibles[idExtra];
    if (!extra) return;

    let nuevaCantidad = Math.max(0, extra.cantidad + delta);
    extra.cantidad = nuevaCantidad;

    document.getElementById(`cant-modal-${idExtra}`).innerText = nuevaCantidad;
    actualizarTotalModal();
}

// --- Recalcular el total mostrado en el footer del modal ---
function actualizarTotalModal() {
    if (!productoActual) return;

    let total = productoActual.precioBase;
    for (let key in extrasDisponibles) {
        let extra = extrasDisponibles[key];
        total += extra.precio * extra.cantidad;
    }
    document.getElementById("modal-total-calc").innerText = "Total: $" + total.toLocaleString();
}

// --- Confirmar y añadir el plato personalizado al carrito ---
function agregarAlCarroPersonalizado() {
    if (!productoActual) return;

    let observaciones = document.getElementById("observaciones").value.trim();
    let extrasSeleccionados = Object.values(extrasDisponibles).filter(e => e.cantidad > 0);

    // El precio unitario del ítem incluye el plato base + sus extras
    let precioUnitario = productoActual.precioBase;
    extrasSeleccionados.forEach(extra => {
        precioUnitario += extra.precio * extra.cantidad;
    });

    let item = {
        nombre: productoActual.nombre,
        precio: precioUnitario,
        cantidad: 1,
        observaciones: observaciones,
        extras: extrasSeleccionados.map(e => ({ nombre: e.nombre, cantidad: e.cantidad })),
        imagen: productoActual.img || ""
    };

    agregarAlCarrito(item);

    let modal = bootstrap.Modal.getInstance(document.getElementById("modalPersonalizar"));
    if (modal) modal.hide();

    alert(`"${productoActual.nombre}" se agregó al carrito.`);
    productoActual = null;
}