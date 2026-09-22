// ============================================
// MAIN.JS - Inicialización general del sitio
// Se carga en todas las páginas, al final
// ============================================

document.addEventListener("DOMContentLoaded", () => {
    // Actualiza el número del carrito en el navbar (todas las páginas)
    actualizarContadorCarrito();

    // Pinta el botón "Acceder" o el menú de usuario según haya sesión iniciada
    renderNavbarAuth();

    // Si estamos en carrito.html, pintamos la lista y los totales
    if (document.getElementById("lista-carrito")) {
        cargarCarrito();
    }
});
