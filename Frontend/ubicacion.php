<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Ubicación - Masala</title>
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
                        <li class="nav-item"><a class="nav-link text-white fw-bold" href="ubicacion.php">UBICACIÓN</a></li>
                        <li class="nav-item ms-md-3" id="navAuthItem">
                            <!-- Este contenido lo reemplaza auth.js según si hay sesión iniciada -->
                            <button type="button" class="btn btn-outline-light btn-efecto px-3 py-2" data-bs-toggle="modal" data-bs-target="#modalLogin">
                                <i class="bi bi-person-circle me-1"></i> Acceder
                            </button>
                        </li>
                        <li class="nav-item ms-md-3">
                            <a href="carrito.php" class="btn position-relative fw-bold px-3 py-2 btn-efecto shadow-sm" style="background-color: #23A9BD; color: #010310;">
                                <i class="bi bi-cart3 fs-5 me-1"></i> Carrito
                                <span id="contador-carrito" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">0</span>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div style="height: 80px;"></div>

        <!-- CONTENIDO DE UBICACIÓN -->
        <div class="container my-5">
            <h2 class="mb-4 fw-bold" style="color: #8CE1EE;"><i class="bi bi-geo-alt-fill"></i> Nuestras Sucursales - Masala</h2>
            <div class="row g-4">
                <div class="col-12 col-md-6">
                    <div class="p-4 bg-dark rounded border border-secondary shadow h-100">
                        <h4 class="fw-bold" style="color: #23A9BD;">Sucursal Central</h4>
                        <p class="text-light mt-3">Av. Providencia 1234, Santiago</p>
                        <span class="badge" style="background-color: #23A9BD; color: #010310;">Abierto ahora</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <div class="p-4 bg-dark rounded border border-secondary shadow h-100">
                        <h4 class="fw-bold" style="color: #23A9BD;">Sucursal Ñuñoa</h4>
                        <p class="text-light mt-3">Av. Irarrázaval 4567, Santiago</p>
                        <span class="badge" style="background-color: #23A9BD; color: #010310;">Abierto ahora</span>
                    </div>
                </div>
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