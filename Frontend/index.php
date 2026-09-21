<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Inicio - Masala</title>
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
                <a class="navbar-brand fw-bold fs-3 mx-0" href="index.php" style="color: #8CE1EE;">Masala</a>
                
                <button class="navbar-toggler btn-efecto border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation" style="background-color: #23A9BD;">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                    <ul class="navbar-nav fs-5 align-items-md-center gap-md-3">
                        <li class="nav-item"><a class="nav-link text-white fw-bold" href="index.php">INICIO</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="carta.php">CARTA</a></li>
                        <li class="nav-item"><a class="nav-link text-white" href="ubicacion.php">UBICACIÓN</a></li>
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

        <div style="height: 70px;"></div>

        <!-- CUADRÍCULA ASIMÉTRICA RESPONSIVA -->
        <div class="container-fluid p-0">
            <div class="row g-0 row-desigual">
                <div class="col-12 col-md-4 d-flex flex-column">
                    <div class="grid-hero-item box-baja d-flex align-items-center justify-content-center text-center p-4 border-bottom border-end border-secondary" style="background-image: url('img/plato1.jpg');"></div>
                    <div class="grid-hero-item box-alta d-flex align-items-center justify-content-center text-center p-4 border-end border-secondary" style="background-image: url('img/pollito.jpg');"></div>
                </div>
                <div class="col-12 col-md-4 d-flex flex-column">
                    <div class="grid-hero-item box-alta d-flex flex-column align-items-center justify-content-center text-center p-4 border-bottom border-end border-secondary" style="background-image: url('img/bebestible.jpg');">
                        <div class="grid-hero-content px-2">
                            <span class="text-uppercase small text-light opacity-75" style="letter-spacing: 2px;">BIENVENIDOS</span>
                            <h1 class="display-4 fw-bold text-white mt-1 mb-0" style="letter-spacing: 1px;">Masala</h1>
                        </div>
                    </div>
                    <div class="grid-hero-item box-baja d-flex flex-column align-items-center justify-content-center text-center p-4 border-end border-secondary" style="background-image: url('img/plato1.jpg');">
                        <div class="grid-hero-content">
                            <p class="text-light mb-2 small fw-bold">Curry & Naan</p>
                            <a href="carta.php" class="btn btn-light fw-bold px-4 py-2 shadow text-dark rounded-0 btn-efecto" style="background-color: #ffffff; border: none;">
                                Ver Carta
                            </a>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-4 d-flex flex-column">
                    <div class="grid-hero-item box-mediana d-flex align-items-center justify-content-center text-center p-4 border-bottom border-secondary" style="background-image: url('img/pollito.jpg');"></div>
                    <div class="grid-hero-item box-mediana d-flex align-items-center justify-content-center text-center p-4" style="background-image: url('img/bebestible.jpg');"></div>
                </div>
            </div>
        </div>

        <!-- PRODUCTOS MÁS VENDIDOS -->
        <div class="container my-5">
            <h2 class="text-center mb-4 fw-bold" style="color: #8CE1EE;">Lo más vendido</h2>
            <div class="row g-4">
                <div class="col-12 col-md-4">
                    <div class="card bg-dark text-white border-secondary h-100 shadow-sm">
                        <img src="img/plato1.jpg" class="card-img-top w-100" alt="Chicken Tikka Masala" style="height: 220px; object-fit: cover;">
                        <div class="card-body d-flex flex-column justify-content-between">
                            <div>
                                <h5 class="card-title fw-bold" style="color: #23A9BD;">Chicken Tikka Masala</h5>
                                <p class="card-text text-light small">Trocitos de pollo marinados en especias hindúes con salsa cremosa.</p>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <span class="fs-5 fw-bold text-warning">$9.500</span>
                                <a href="carta.php" class="btn btn-sm fw-bold px-3 btn-efecto" style="background-color: #23A9BD; color: #010310;">Pedir</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <div class="card bg-dark text-white border-secondary h-100 shadow-sm">
                        <img src="img/naan.jpg" class="card-img-top w-100" alt="Pan Naan al Ajo" style="height: 220px; object-fit: cover;">
                        <div class="card-body d-flex flex-column justify-content-between">
                            <div>
                                <h5 class="card-title fw-bold" style="color: #23A9BD;">Pan Naan al Ajo</h5>
                                <p class="card-text text-light small">Pan plano tradicional horneado en tandoor con mantequilla y ajo.</p>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <span class="fs-5 fw-bold text-warning">$2.500</span>
                                <a href="carta.php" class="btn btn-sm fw-bold px-3 btn-efecto" style="background-color: #23A9BD; color: #010310;">Pedir</a>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <div class="card bg-dark text-white border-secondary h-100 shadow-sm">
                        <img src="img/bebestible.jpg" class="card-img-top w-100" alt="Limonada Menta Jengibre" style="height: 220px; object-fit: cover;">
                        <div class="card-body d-flex flex-column justify-content-between">
                            <div>
                                <h5 class="card-title fw-bold" style="color: #23A9BD;">Limonada Menta Jengibre</h5>
                                <p class="card-text text-light small">Refrescante bebida natural de la casa (500ml).</p>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <span class="fs-5 fw-bold text-warning">$3.000</span>
                                <a href="carta.php" class="btn btn-sm fw-bold px-3 btn-efecto" style="background-color: #23A9BD; color: #010310;">Pedir</a>
                            </div>
                        </div>
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