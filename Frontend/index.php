<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Inicio - Masala</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
        <style>
            .btn-efecto {
                transition: all 0.3s ease-in-out;
            }
            .btn-efecto:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(35, 169, 189, 0.4) !important;
                background-color: #8CE1EE !important;
                color: #010310 !important;
            }
            .grid-hero-item {
                position: relative;
                background-size: cover;
                background-position: center;
                background-color: #010310;
            }
            .grid-hero-item::before {
                content: "";
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(1, 3, 16, 0.55);
                z-index: 1;
            }
            .grid-hero-content {
                position: relative;
                z-index: 2;
            }
            .box-alta { min-height: 420px; }
            .box-mediana { min-height: 340px; }
            .box-baja { min-height: 260px; }
            @media (min-width: 768px) {
                .row-desigual { display: flex; align-items: stretch; }
            }
        </style>
    </head>
    <body style="background-color: #010310; color: #ffffff;">

        <!-- NAVBAR -->
        <nav class="navbar navbar-dark bg-dark px-3 position-fixed w-100" style="z-index: 1050;">
            <div class="container-fluid d-flex justify-content-between align-items-center">
                <button class="btn text-white px-3 py-2 btn-efecto" type="button" data-bs-toggle="offcanvas" data-bs-target="#menuLateral" style="background-color: #23A9BD; color: #010310 !important;">
                    <i class="bi bi-list fs-4"></i>
                </button>
                <a class="navbar-brand fw-bold fs-3 mx-0" href="index.php" style="color: #8CE1EE;">Masala</a>
                <div style="width: 45px;" class="d-block d-md-none"></div>
            </div>
        </nav>

        <!-- MENÚ LATERAL (OFFCANVAS) -->
        <div class="offcanvas offcanvas-start text-bg-dark" tabindex="-1" id="menuLateral" style="background-color: #010310 !important;">
            <div class="offcanvas-header">
                <h5 class="offcanvas-title" style="color: #23A9BD;">Menú</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body d-flex flex-column justify-content-between">
                <ul class="navbar-nav fs-5">
                    <li class="nav-item mb-2"><a class="nav-link text-white fw-bold" href="index.php">INICIO</a></li>
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="carta.php">CARTA</a></li>
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="ubicacion.php">UBICACIÓN</a></li>
                </ul>
                <div class="d-flex flex-column gap-2 border-top border-secondary pt-3">
                    <a href="ubicacion.php" class="text-light text-decoration-none"><i class="bi bi-geo-alt-fill" style="color: #23A9BD;"></i> Santiago, Chile</a>
                </div>
            </div>
        </div>

        <div style="height: 70px;"></div>

        <!-- CUADRÍCULA ASIMÉTRICA -->
        <div class="container-fluid p-0">
            <div class="row g-0 row-desigual">
                <div class="col-md-4 d-flex flex-column">
                    <div class="grid-hero-item box-baja d-flex align-items-center justify-content-center text-center p-4 border-bottom border-end border-secondary" style="background-image: url('img/plato1.jpg');"></div>
                    <div class="grid-hero-item box-alta d-flex align-items-center justify-content-center text-center p-4 border-end border-secondary" style="background-image: url('img/pollito.jpg');"></div>
                </div>
                <div class="col-md-4 d-flex flex-column">
                    <div class="grid-hero-item box-alta d-flex flex-column align-items-center justify-content-center text-center p-4 border-bottom border-end border-secondary" style="background-image: url('img/bebestible.jpg');">
                        <div class="grid-hero-content">
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
                <div class="col-md-4 d-flex flex-column">
                    <div class="grid-hero-item box-mediana d-flex align-items-center justify-content-center text-center p-4 border-bottom border-secondary" style="background-image: url('img/pollito.jpg');"></div>
                    <div class="grid-hero-item box-mediana d-flex align-items-center justify-content-center text-center p-4" style="background-image: url('img/bebestible.jpg');"></div>
                </div>
            </div>
        </div>

        <!-- PRODUCTOS MÁS VENDIDOS -->
        <div class="container my-5">
            <h2 class="text-center mb-4 fw-bold" style="color: #8CE1EE;">Lo más vendido</h2>
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card bg-dark text-white border-secondary h-100 shadow-sm">
                        <img src="img/pollito.jpg" class="card-img-top" alt="Plato 1" style="height: 220px; object-fit: cover;">
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
                <div class="col-md-4">
                    <div class="card bg-dark text-white border-secondary h-100 shadow-sm">
                        <img src="img/plato1.jpg" class="card-img-top" alt="Plato 2" style="height: 220px; object-fit: cover;">
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
                <div class="col-md-4">
                    <div class="card bg-dark text-white border-secondary h-100 shadow-sm">
                        <img src="img/bebestible.jpg" class="card-img-top" alt="Bebestible" style="height: 220px; object-fit: cover;">
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
        <div class="container-fluid bg-dark py-3">
            <div class="row text-center"><div class="col-12" style="color: #23A9BD;"><strong>Jose-Tomas Guzman y Daniela Jara</strong></div></div>
        </div>
    </body>
</html>