// ============================================
// CARRITO.JS - Lógica del carrito de compras
// Persistencia vía localStorage, compartida en todas las páginas
// ============================================

const CARRITO_STORAGE_KEY = "carrito_restaurante";
let descuentoAplicado = 0; // Porcentaje de descuento activo (0 a 1)

// --- Utilidades de almacenamiento ---
function obtenerCarrito() {
    return JSON.parse(localStorage.getItem(CARRITO_STORAGE_KEY)) || [];
}

function guardarCarrito(carrito) {
    localStorage.setItem(CARRITO_STORAGE_KEY, JSON.stringify(carrito));
    actualizarContadorCarrito();
}

// --- Agregar un producto al carrito ---
// item = { nombre, precio (unitario, con extras incluidos), cantidad, observaciones, extras: [{nombre, cantidad}] }
function agregarAlCarrito(item) {
    let carrito = obtenerCarrito();
    carrito.push(item);
    guardarCarrito(carrito);
}

// --- Eliminar un producto por índice ---
function eliminarItem(index) {
    let carrito = obtenerCarrito();
    carrito.splice(index, 1);
    guardarCarrito(carrito);
    cargarCarrito();
}

// --- Actualiza el badge del navbar en TODAS las páginas ---
function actualizarContadorCarrito() {
    let contador = document.getElementById("contador-carrito");
    if (!contador) return;
    let carrito = obtenerCarrito();
    let totalItems = carrito.reduce((acc, item) => acc + item.cantidad, 0);
    contador.innerText = totalItems;
}

// --- Mostrar/ocultar campo de dirección según tipo de entrega ---
function cambiarTipoEntrega() {
    let deliveryInput = document.getElementById("delivery");
    let campoDireccion = document.getElementById("campo-direccion");
    if (!deliveryInput || !campoDireccion) return;

    campoDireccion.style.display = deliveryInput.checked ? "block" : "none";
    cargarCarrito();
}

// --- Código de descuento ---
function aplicarDescuento() {
    let inputCodigo = document.getElementById("codigoDescuento").value.trim().toUpperCase();
    let msj = document.getElementById("mensajeDescuento");

    if (inputCodigo === "MASALA20") {
        descuentoAplicado = 0.20; // 20% de descuento
        msj.innerText = "¡Descuento del 20% aplicado con éxito!";
        msj.className = "text-success mt-1 d-block";
    } else {
        descuentoAplicado = 0;
        msj.innerText = "Código no válido o expirado.";
        msj.className = "text-danger mt-1 d-block";
    }
    cargarCarrito(); // Recalculamos los totales
}

// --- Pintar el carrito y calcular totales (solo aplica en carrito.html) ---
function cargarCarrito() {
    let lista = document.getElementById("lista-carrito");
    if (!lista) return;

    let carrito = obtenerCarrito();
    let subtotalElem = document.getElementById("lbl-subtotal");
    let envioElem = document.getElementById("lbl-envio");
    let totalElem = document.getElementById("lbl-total");

    lista.innerHTML = "";
    if (carrito.length === 0) {
        lista.innerHTML = '<li class="list-group-item bg-transparent text-muted border-secondary text-center">Tu carro está vacío</li>';
        subtotalElem.innerText = "$0"; envioElem.innerText = "$0"; totalElem.innerText = "$0";
        return;
    }

    let subtotalBruto = 0;

    // Pintar los productos en la lista
    carrito.forEach((item, index) => {
        let totalItem = item.precio * item.cantidad;
        subtotalBruto += totalItem;

        let detalles = "";
        if (item.extras && item.extras.length > 0) {
            let textoExtras = item.extras.map(ex => `${ex.nombre} x${ex.cantidad}`).join(", ");
            detalles += `<br><span class="text-info small">+ ${textoExtras}</span>`;
        }
        if (item.observaciones) {
            detalles += `<br><span class="text-muted small fst-italic">"${item.observaciones}"</span>`;
        }

        let imagenHtml = item.imagen
            ? `<img src="${item.imagen}" alt="${item.nombre}" class="rounded me-3" style="width: 64px; height: 64px; object-fit: cover; flex-shrink: 0;">`
            : `<div class="rounded me-3 bg-secondary bg-opacity-25 d-flex align-items-center justify-content-center" style="width: 64px; height: 64px; flex-shrink: 0;"><i class="bi bi-egg-fried fs-4 text-secondary"></i></div>`;

        let li = document.createElement("li");
        li.className = "list-group-item bg-transparent text-white border-secondary d-flex justify-content-between align-items-center px-0 py-3 flex-wrap gap-2";
        li.innerHTML = `
            <div class="d-flex align-items-center">
                ${imagenHtml}
                <div>
                    <strong>${item.nombre}</strong><br>
                    <span class="badge bg-secondary mt-1">Cantidad: x ${item.cantidad}</span>
                    ${detalles}
                </div>
            </div>
            <div class="d-flex align-items-center gap-3">
                <span class="fw-bold text-warning">$${totalItem.toLocaleString()}</span>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarItem(${index})"><i class="bi bi-trash"></i></button>
            </div>
        `;
        lista.appendChild(li);
    });

    // 1. Aplicar descuento al subtotal
    let montoDescuento = subtotalBruto * descuentoAplicado;
    let subtotalConDescuento = subtotalBruto - montoDescuento;

    // 2. Determinar el costo de envío (Delivery gratis sobre $20.000 del subtotal con descuento)
    let deliveryInput = document.getElementById("delivery");
    let esDelivery = deliveryInput ? deliveryInput.checked : false;
    let costoEnvio = 0;

    if (esDelivery) {
        costoEnvio = subtotalConDescuento > 20000 ? 0 : 2000;
    }

    // 3. Calcular Total Final
    let totalFinal = subtotalConDescuento + costoEnvio;

    // 4. Imprimir en pantalla
    let textoSubtotal = "$" + subtotalBruto.toLocaleString();
    if (descuentoAplicado > 0) {
        textoSubtotal += ` <span class="text-success small">(-$${montoDescuento.toLocaleString()})</span>`;
    }

    subtotalElem.innerHTML = textoSubtotal;

    if (esDelivery && subtotalConDescuento > 20000) {
        envioElem.innerHTML = `<span class="text-decoration-line-through text-muted me-2">$2.000</span> <span class="text-success fw-bold">¡Gratis!</span>`;
    } else {
        envioElem.innerText = "$" + costoEnvio.toLocaleString();
    }

    totalElem.innerText = "$" + totalFinal.toLocaleString();
}

// --- Confirmar y "pagar" el pedido (simulado, sin backend) ---
function finalizarCompra() {
    let carrito = obtenerCarrito();
    if (carrito.length === 0) {
        alert("Tu carrito está vacío. Agrega productos desde la carta antes de continuar.");
        return;
    }

    let deliveryInput = document.getElementById("delivery");
    if (deliveryInput && deliveryInput.checked) {
        let direccion = document.getElementById("direccion").value.trim();
        if (direccion === "") {
            alert("Por favor ingresa una dirección de entrega.");
            document.getElementById("direccion").focus();
            return;
        }
    }

    let total = document.getElementById("lbl-total").innerText;
    alert(`¡Pedido confirmado! Total a pagar: ${total}\n\nGracias por tu compra en Masala.`);

    // Vaciamos el carrito tras "pagar"
    localStorage.removeItem(CARRITO_STORAGE_KEY);
    descuentoAplicado = 0;
    cargarCarrito();
}
