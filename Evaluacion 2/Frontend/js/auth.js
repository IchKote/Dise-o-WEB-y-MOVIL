// ============================================
// AUTH.JS - Login / Registro (simulado en frontend)
// No hay backend: las credenciales están hardcodeadas
// y la sesión se guarda en localStorage.
// ============================================

// --- Cuentas de prueba hardcodeadas ---
// (Los registros nuevos se agregan aquí en memoria, se pierden al recargar)
const USUARIOS_DEMO = [
    { nombre: "Administrador Masala", email: "admin@masala.cl",   password: "admin123",   rol: "admin" },
    { nombre: "Daniela Jara",         email: "cliente@masala.cl", password: "cliente123", rol: "cliente" }
];

const SESION_STORAGE_KEY = "usuario_sesion";

let modoRegistro = false;

// --- Sesión actual ---
function obtenerSesion() {
    return JSON.parse(localStorage.getItem(SESION_STORAGE_KEY)) || null;
}

function guardarSesion(usuario) {
    localStorage.setItem(SESION_STORAGE_KEY, JSON.stringify(usuario));
    renderNavbarAuth();
}

function cerrarSesion() {
    localStorage.removeItem(SESION_STORAGE_KEY);
    renderNavbarAuth();
}

// --- Alternar entre modo Login y modo Registro dentro del modal ---
function alternarAuth() {
    modoRegistro = !modoRegistro;
    document.getElementById("campoNombre").style.display = modoRegistro ? "block" : "none";
    document.getElementById("tituloModalAuth").innerText = modoRegistro ? "Crear Cuenta" : "Iniciar Sesión";
    document.getElementById("btnAuthSubmit").innerText = modoRegistro ? "Registrarse" : "Entrar";
    document.getElementById("textoAuthSwitch").innerText = modoRegistro ? "¿Ya tienes cuenta?" : "¿No tienes cuenta?";
    document.getElementById("authNombre").required = modoRegistro;
}

// --- Procesar el envío del formulario (login o registro) ---
function procesarAuth(e) {
    e.preventDefault();

    let email = document.getElementById("authEmail").value.trim().toLowerCase();
    let password = document.getElementById("authPass").value;

    if (modoRegistro) {
        let nombre = document.getElementById("authNombre").value.trim();

        if (USUARIOS_DEMO.some(u => u.email === email)) {
            alert("Ese correo ya está registrado. Intenta iniciar sesión.");
            return;
        }

        let nuevoUsuario = { nombre: nombre || email, email, password, rol: "cliente" };
        USUARIOS_DEMO.push(nuevoUsuario); // Solo en memoria, se pierde al recargar (no hay backend)

        alert(`¡Cuenta creada exitosamente para ${nuevoUsuario.nombre}!`);
        guardarSesion({ nombre: nuevoUsuario.nombre, email: nuevoUsuario.email, rol: nuevoUsuario.rol });

    } else {
        let usuario = USUARIOS_DEMO.find(u => u.email === email && u.password === password);

        if (!usuario) {
            alert("Correo o contraseña incorrectos.\n\nCuentas de prueba:\n- admin@masala.cl / admin123\n- cliente@masala.cl / cliente123");
            return;
        }

        alert(`¡Bienvenido de vuelta, ${usuario.nombre}!`);
        guardarSesion({ nombre: usuario.nombre, email: usuario.email, rol: usuario.rol });
    }

    let modalEl = document.getElementById('modalLogin');
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
    document.getElementById('formAuth').reset();
}

// --- Pintar el navbar según si hay o no sesión iniciada ---
function renderNavbarAuth() {
    let contenedor = document.getElementById("navAuthItem");
    if (!contenedor) return;

    let usuario = obtenerSesion();

    if (!usuario) {
        contenedor.innerHTML = `
            <button type="button" class="btn btn-outline-light btn-efecto px-3 py-2" data-bs-toggle="modal" data-bs-target="#modalLogin">
                <i class="bi bi-person-circle me-1"></i> Acceder
            </button>
        `;
        return;
    }

    let badgeAdmin = usuario.rol === "admin"
        ? '<span class="badge bg-warning text-dark ms-1">Admin</span>'
        : '';

    contenedor.innerHTML = `
        <div class="dropdown">
            <button class="btn btn-outline-light btn-efecto px-3 py-2 dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi bi-person-circle me-1"></i> ${usuario.nombre}${badgeAdmin}
            </button>
            <ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark">
                <li><span class="dropdown-item-text small text-muted">${usuario.email}</span></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" onclick="cerrarSesion(); return false;"><i class="bi bi-box-arrow-right me-1"></i> Cerrar sesión</a></li>
            </ul>
        </div>
    `;
}
