<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Tu Carrito - Masala</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <link rel="stylesheet" href="css/estilos.css">
    </head>
    <body>

        <!-- NAVBAR RESPONSIVO -->
        <nav class="navbar navbar-dark bg-dark navbar-expand-md px-3 position-fixed w-100" style="z-index: 1050;">
            <div class="container-fluid d-flex justify-content-between align-items-center">
                <a class="navbar-brand d-flex align-items-center mx-0" href="index.php">
                    <img src="img/logo.webp" alt="Masala" style="height: 44px; width: 44px; object-fit: cover; border-radius: 10px;">
                </a>
                
                <button class="navbar-toggler btn-efecto border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation" style="background-color: #23A9BD;">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                    <ul class="navbar-nav fs-5 align-items-md-center gap-md-3">
                        <li class="nav-item"><a class="nav-link text-white" href="index.php">INICIO</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="carta.php">CARTA</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="ubicacion.php">UBICACIÓN</a></li>
                        <li class="nav-item ms-md-3" id="navAuthItem">
                            <!-- Este contenido lo reemplaza auth.js según si hay sesión iniciada -->
                            <button type="button" class="btn btn-outline-light btn-efecto px-3 py-2" data-bs-toggle="modal" data-bs-target="#modalLogin">
                                <i class="bi bi-person-circle me-1"></i> Acceder
                            </button>
                        </li>
                        <li class="nav-item ms-md-3">
                            <a href="carta.php" class="btn btn-outline-light btn-efecto" style="border-color: #23A9BD; color: #8CE1EE;">
                                <i class="bi bi-arrow-left"></i> Volver a la Carta
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div style="height: 80px;"></div>

        <!-- CONTENIDO DEL CARRITO -->
        <div class="container my-5" style="max-width: 800px;">
            <h2 class="mb-4 fw-bold" style="color: #8CE1EE;"><i class="bi bi-cart3"></i> Tu Carrito de Compras</h2>

            <div class="card bg-dark text-white border-secondary p-4 shadow">
                <ul id="lista-carrito" class="list-group list-group-flush bg-transparent mb-3 text-white">
                    <li class="list-group-item bg-transparent text-muted border-secondary text-center">Tu carro está vacío</li>
                </ul>

                <div class="mb-3 border-top border-secondary pt-3">
                    <label class="form-label fw-bold" style="color: #23A9BD;">Tipo de Entrega:</label>
                    <div class="d-flex gap-4 flex-wrap">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="tipoEntrega" id="retiro" value="retiro" checked onclick="cambiarTipoEntrega()">
                            <label class="form-check-label" for="retiro">Retiro en Local ($0)</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="tipoEntrega" id="delivery" value="delivery" onclick="cambiarTipoEntrega()">
                            <label class="form-check-label" for="delivery">Delivery ($2.000)</label>
                        </div>
                    </div>
                </div>

                <div id="campo-direccion" class="mb-3" style="display: none;">
                    <label for="direccion" class="form-label small">Dirección de Entrega</label>
                    <input type="text" class="form-control bg-dark text-white border-secondary" id="direccion" placeholder="Ej. Av. Providencia 123">
                </div>

                <!-- CÓDIGO DE DESCUENTO -->
                <div class="mb-3 border-top border-secondary pt-3">
                    <label for="codigoDescuento" class="form-label fw-bold" style="color: #23A9BD;">¿Tienes un código de descuento?</label>
                    <div class="input-group">
                        <input type="text" class="form-control bg-dark text-white border-secondary" id="codigoDescuento" placeholder="Ej. MASALA20">
                        <button class="btn btn-outline-warning fw-bold" type="button" onclick="aplicarDescuento()">Aplicar</button>
                    </div>
                    <small id="mensajeDescuento" class="text-success mt-1 d-none">¡Descuento del 20% aplicado con éxito!</small>
                </div>

                <div class="border-top border-secondary pt-3 mb-4">
                    <div class="d-flex justify-content-between mb-2"><span>Subtotal:</span><span id="lbl-subtotal">$0</span></div>
                    <div class="d-flex justify-content-between mb-2"><span>Costo Envío:</span><span id="lbl-envio">$0</span></div>
                    <div class="d-flex justify-content-between fw-bold fs-4" style="color: #8CE1EE;"><span>Total:</span><span id="lbl-total">$0</span></div>
                </div>

                <button type="button" class="btn w-100 fw-bold py-2 shadow-sm btn-efecto" style="background-color: #23A9BD; color: #010310;" onclick="finalizarCompra()">
                    Confirmar y Pagar <i class="bi bi-check-circle-fill ms-1"></i>
                </button>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="container-fluid bg-dark py-3 mt-5">
            <div class="row text-center"><div class="col-12" style="color: #23A9BD;"><strong>Jose-Tomas Guzman y Daniela Jara</strong></div></div>
        </div>

        <!-- MODAL DE LOGIN / REGISTRO (Va aquí, oculto por defecto) -->
        <div class="modal fade" id="modalLogin" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark text-white border-secondary">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title fw-bold" id="tituloModalAuth" style="color: #8CE1EE;">Iniciar Sesión</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-4">
                        <form id="formAuth" onsubmit="procesarAuth(event)">
                            <div id="campoNombre" class="mb-3" style="display: none;">
                                <label for="authNombre" class="form-label">Nombre Completo</label>
                                <input type="text" class="form-control bg-dark text-white border-secondary" id="authNombre" placeholder="Ej. Juan Pérez">
                            </div>
                            <div class="mb-3">
                                <label for="authEmail" class="form-label">Correo Electrónico</label>
                                <input type="email" class="form-control bg-dark text-white border-secondary" id="authEmail" placeholder="correo@ejemplo.com" required>
                            </div>
                            <div class="mb-4">
                                <label for="authPass" class="form-label">Contraseña</label>
                                <input type="password" class="form-control bg-dark text-white border-secondary" id="authPass" required>
                            </div>
                            <button type="submit" class="btn w-100 fw-bold btn-efecto mb-3" style="background-color: #23A9BD; color: #010310;" id="btnAuthSubmit">
                                Entrar
                            </button>
                            <div class="text-center">
                                <small class="text-light">
                                    <span id="textoAuthSwitch">¿No tienes cuenta?</span> 
                                    <a href="#" class="fw-bold text-warning text-decoration-none" onclick="alternarAuth()">¡Regístrate aquí!</a>
                                </small>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- SCRIPTS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="js/carrito.js"></script>
        <script src="js/auth.js"></script>
        <script src="js/main.js"></script>
    </body>
</html>