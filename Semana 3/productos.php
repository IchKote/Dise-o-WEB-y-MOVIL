<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Nuestros Productos</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body style="background-color: #010310; color: #ffffff;">
        <!-- navbar -->
        <nav class="navbar navbar-expand-sm bg-dark navbar-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="index.php">
                    <img src="img/logo.png" style="height: 40px;">
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#collapsibleNavbar">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="collapsibleNavbar">
                    <ul class="navbar-nav">
                        <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">Empresa</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="empresa.php">Quienes somos</a></li>
                            <li><a class="dropdown-item" href="#">Nuestro equipo</a></li>
                            <li><a class="dropdown-item" href="#">Mision</a></li>
                        </ul>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link " href="productos.php">Productos</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="servicios.php">Servicios</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="contacto.php">Contacto</a>
                        </li>
                    </ul>
                </div>
                <button type="button" class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#myModal"style="background-color: #23A9BD; color: #010310">Acceder</button>
            </div>
        </nav>
        <!-- container -->
        
        <div class="container-fluid" style="background-color: #010310; color: #ffffff;">
            <!-- Carousel -->
            <div id="demo" class="carousel slide" data-bs-ride="carousel">
                <!-- Indicators/dots -->
                <div class="carousel-indicators">
                    <button type="button" data-bs-target="#demo" data-bs-slide-to="0" class="active"></button>
                    <button type="button" data-bs-target="#demo" data-bs-slide-to="1"></button>
                    <button type="button" data-bs-target="#demo" data-bs-slide-to="2"></button>
                </div>
                <!-- The slideshow/carousel -->
                <div class="carousel-inner">
                    <div class="carousel-item active">
                    <img src="img/basket.jpg" alt="Basket" class="d-block w-100">
                    </div>
                    <div class="carousel-item">
                    <img src="img/futbol.jpeg" alt="Football" class="d-block w-100">
                    </div>
                    <div class="carousel-item">
                    <img src="img/lol.jpg" alt="League of Legends" class="d-block w-100">
                    </div>
                </div>
                    <!-- Left and right controls/icons -->
                    <button class="carousel-control-prev" type="button" data-bs-target="#demo" data-bs-slide="prev">
                        <span class="carousel-control-prev-icon"></span>
                    </button>
                    <button class="carousel-control-next" type="button" data-bs-target="#demo" data-bs-slide="next">
                        <span class="carousel-control-next-icon"></span>
                    </button>
            </div>
        </div>
        <!-- Contenedor donde app.js cargará las tarjetas -->
        <div class="container my-5">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 style="color: #23A9BD;">Nuestras Disciplinas</h2>
                <button id="btn-cargar" class="btn" style="background-color: #23A9BD; color: #010310; font-weight: bold;" onclick="mostrarDisciplinas()">
                    Cargar Disciplinas
                </button>
            </div>
            
            <!-- Aquí JS insertará las columnas con id="Disciplinas" -->
            <div class="row" id="Disciplinas"></div>
        </div>
        <!-- footer -->
        <div class="container-fluid bg-dark">
            <div class="row">
                <div class="col-4"></div>
                <div class="col-4" style="color: #23A9BD"><strong>Jose-Tomas Guzman y Daniela Jara</strong></div>
                <div class="col-4"></div>
            </div>
        </div>

        <!-- modal -->
        <div class="modal fade" id="myModal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h4 class="modal-title">Autenticacion</h4>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <!-- Modal body -->
                    <div class="modal-body">
                        <form action="empresa.php">
                            <div class="mb-3 mt-3">
                                <label for="email" class="form-label">Email:</label>
                                <input type="email" class="form-control" id="email" placeholder="Enter email" name="email">
                            </div>
                            <div class="mb-3">
                                <label for="pwd" class="form-label">Password:</label>
                                <input type="password" class="form-control" id="pwd" placeholder="Enter password" name="pswd">
                            </div>
                            <div class="form-check mb-3">
                                <label class="form-check-label">
                                    <input class="form-check-input" type="checkbox" name="remember"> Remember me
                                </label>
                            </div>
                            <button type="submit" class="btn btn-primary">Login</button>
                        </form>
                    </div>
                    <!-- Modal footer -->
                    <div class="modal-footer">
                        <button type="button" class="btn btn-danger" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        <script src="app.js"></script>
    </body>
</html>