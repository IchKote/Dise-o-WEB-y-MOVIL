<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Ubicación - Masala</title>
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

        <!-- MENÚ LATERAL -->
        <div class="offcanvas offcanvas-start text-bg-dark" tabindex="-1" id="menuLateral" style="background-color: #010310 !important;">
            <div class="offcanvas-header">
                <h5 class="offcanvas-title" style="color: #23A9BD;">Menú</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body d-flex flex-column justify-content-between">
                <ul class="navbar-nav fs-5">
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="index.php">INICIO</a></li>
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="carta.php">CARTA</a></li>
                    <li class="nav-item mb-2"><a class="nav-link text-white fw-bold" href="ubicacion.php">UBICACIÓN</a></li>
                </ul>
                <div class="d-flex flex-column gap-2 border-top border-secondary pt-3">
                    <a href="ubicacion.php" class="text-light text-decoration-none"><i class="bi bi-geo-alt-fill" style="color: #23A9BD;"></i> Santiago, Chile</a>
                </div>
            </div>
        </div>

        <div style="height: 80px;"></div>

        <!-- CONTENIDO DE UBICACIÓN -->
        <div class="container my-5">
            <h2 class="mb-4 fw-bold" style="color: #8CE1EE;"><i class="bi bi-geo-alt-fill"></i> Nuestras Sucursales - Masala</h2>
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="p-4 bg-dark rounded border border-secondary shadow h-100">
                        <h4 class="fw-bold" style="color: #23A9BD;">Sucursal Central</h4>
                        <p class="text-light mt-3">Av. Providencia 1234, Santiago</p>
                        <span class="badge" style="background-color: #23A9BD; color: #010310;">Abierto ahora</span>
                    </div>
                </div>
                <div class="col-md-6">
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
    </body>
</html>