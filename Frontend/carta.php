<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Carta y Menú - Masala</title>
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
            .card-producto {
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            .card-producto:hover {
                transform: scale(1.02);
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
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="index.php">INICIO</a></li>
                    <li class="nav-item mb-2"><a class="nav-link text-white fw-bold" href="carta.php">CARTA</a></li>
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="ubicacion.php">UBICACIÓN</a></li>
                </ul>
                <div class="d-flex flex-column gap-2 border-top border-secondary pt-3">
                    <a href="ubicacion.php" class="text-light text-decoration-none"><i class="bi bi-geo-alt-fill" style="color: #23A9BD;"></i> Santiago, Chile</a>
                </div>
            </div>
        </div>

        <div style="height: 80px;"></div>

        <!-- CARTA CON SLIDER DE PROMOCIONES ARRIBA -->
        <div class="container my-5">
            
            <!-- SLIDER / CARRUSEL DE PROMOCIONES -->
            <div id="sliderPromos" class="carousel slide mb-5 shadow rounded border border-secondary overflow-hidden" data-bs-ride="carousel">
                <div class="carousel-indicators">
                    <button type="button" data-bs-target="#sliderPromos" data-bs-slide-to="0" class="active" aria-current="true"></button>
                    <button type="button" data-bs-target="#sliderPromos" data-bs-slide-to="1"></button>
                    <button type="button" data-bs-target="#sliderPromos" data-bs-slide-to="2"></button>
                </div>
                <div class="carousel-inner">
                    <!-- Promo 1 -->
                    <div class="carousel-item active p-5 text-center bg-dark text-white" style="min-height: 200px;">
                        <span class="badge bg-danger mb-2 px-3 py-2 fs-6">¡CÓDIGO DE DESCUENTO!</span>
                        <h3 class="fw-bold text-warning">Usa el código: <span class="text-white">MASALA20</span></h3>
                        <p class="text-light mb-0">Obtén un 20% de descuento en tu primer pedido online superior a $15.000.</p>
                    </div>
                    <!-- Promo 2 -->
                    <div class="carousel-item p-5 text-center bg-dark text-white" style="min-height: 200px;">
                        <span class="badge bg-info text-dark mb-2 px-3 py-2 fs-6">BENEFICIO BANCARIO</span>
                        <h3 class="fw-bold" style="color: #8CE1EE;">30% de Descuento con BancoEstado</h3>
                        <p class="text-light mb-0">Pagando con tus tarjetas de débito o crédito los días martes y miércoles.</p>
                    </div>
                    <!-- Promo 3 -->
                    <div class="carousel-item p-5 text-center bg-dark text-white" style="min-height: 200px;">
                        <span class="badge bg-success mb-2 px-3 py-2 fs-6">DELIVERY GRATIS</span>
                        <h3 class="fw-bold text-warning">Envío Gratis en Santiago</h3>
                        <p class="text-light mb-0">En compras sobre $20.000 aplican costos de envío preferenciales.</p>
                    </div>
                </div>
                <button class="carousel-control-prev" type="button" data-bs-target="#sliderPromos" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Anterior</span>
                </button>
                <button class="carousel-control-next" type="button" data-bs-target="#sliderPromos" data-bs-slide="next">
                    <span class="carousel-control-next-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Siguiente</span>
                </button>
            </div>

            <!-- CABECERA DE CARTA Y BOTÓN CARRITO -->
            <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom border-secondary">
                <h2 class="fw-bold m-0" style="color: #8CE1EE;">Nuestra Carta - Curry & Naan</h2>
                
                <a href="carrito.php" class="btn position-relative fw-bold px-3 py-2 btn-efecto shadow-sm" style="background-color: #23A9BD; color: #010310;">
                    <i class="bi bi-cart3 fs-5 me-1"></i> Ir al Carrito
                    <span id="contador-carrito" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">0</span>
                </a>
            </div>

            <!-- Categoría: Entradas -->
            <h4 class="text-warning mt-4 mb-3">Entradas</h4>
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card bg-dark text-white border-secondary p-3 h-100 card-producto" onclick="abrirPersonalizador('Samosas Vegetales', 4000, 'img/pollito.jpg')">
                        <div class="row g-0 align-items-center">
                            <div class="col-4">
                                <img src="img/pollito.jpg" alt="Samosas" class="img-fluid rounded" style="height: 100px; width: 100%; object-fit: cover;">
                            </div>
                            <div class="col-8 ps-3">
                                <h5 class="fw-bold mb-1" style="color: #23A9BD;">Samosas Vegetales</h5>
                                <p class="text-light small mb-2">Empanaditas crujientes rellenas de papa y especias aromáticas.</p>
                                <span class="fw-bold text-warning">$4.000</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Categoría: Platos Principales -->
            <h4 class="text-warning mt-4 mb-3">Platos Principales</h4>
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card bg-dark text-white border-secondary p-3 h-100 card-producto" onclick="abrirPersonalizador('Chicken Tikka Masala', 9500, 'img/plato1.jpg')">
                        <div class="row g-0 align-items-center">
                            <div class="col-4">
                                <img src="img/plato1.jpg" alt="Curry" class="img-fluid rounded" style="height: 100px; width: 100%; object-fit: cover;">
                            </div>
                            <div class="col-8 ps-3">
                                <h5 class="fw-bold mb-1" style="color: #23A9BD;">Chicken Tikka Masala</h5>
                                <p class="text-light small mb-2">Pollo marinado con salsa cremosa de tomate y especias hindúes.</p>
                                <span class="fw-bold text-warning">$9.500</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-dark text-white border-secondary p-3 h-100 card-producto" onclick="abrirPersonalizador('Pan Naan al Ajo', 2500, 'img/bebestible.jpg')">
                        <div class="row g-0 align-items-center">
                            <div class="col-4">
                                <img src="img/bebestible.jpg" alt="Naan" class="img-fluid rounded" style="height: 100px; width: 100%; object-fit: cover;">
                            </div>
                            <div class="col-8 ps-3">
                                <h5 class="fw-bold mb-1" style="color: #23A9BD;">Pan Naan al Ajo</h5>
                                <p class="text-light small mb-2">Pan plano tradicional horneado en tandoor con mantequilla y ajo.</p>
                                <span class="fw-bold text-warning">$2.500</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Categoría: Bebestibles -->
            <h4 class="text-warning mt-4 mb-3">Bebestibles</h4>
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <div class="card bg-dark text-white border-secondary p-3 h-100">
                        <div class="row g-0 align-items-center">
                            <div class="col-4">
                                <img src="img/bebestible.jpg" alt="Limonada" class="img-fluid rounded" style="height: 100px; width: 100%; object-fit: cover;">
                            </div>
                            <div class="col-8 ps-3">
                                <h5 class="fw-bold mb-1" style="color: #23A9BD;">Limonada Menta Jengibre</h5>
                                <p class="text-light small mb-1">Refrescante bebida natural (500ml).</p>
                                <span class="fw-bold text-warning d-block mb-2">$3.000</span>
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="d-flex align-items-center gap-2">
                                        <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 28px; height: 28px; padding:0;" onclick="cambiarCantCarta('limonada', -1)">-</button>
                                        <span id="carta-cant-limonada" class="fw-bold fs-6">1</span>
                                        <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 28px; height: 28px; padding:0;" onclick="cambiarCantCarta('limonada', 1)">+</button>
                                    </div>
                                    <button class="btn btn-sm fw-bold px-3 btn-efecto" style="background-color: #23A9BD; color: #010310;" onclick="agregarBebidaCarta('Limonada Menta Jengibre', 3000, 'limonada')">Agregar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-dark text-white border-secondary p-3 h-100">
                        <div class="row g-0 align-items-center">
                            <div class="col-4">
                                <img src="img/bebestible.jpg" alt="Bebida Lata" class="img-fluid rounded" style="height: 100px; width: 100%; object-fit: cover;">
                            </div>
                            <div class="col-8 ps-3">
                                <h5 class="fw-bold mb-1" style="color: #23A9BD;">Bebida Lata 350ml</h5>
                                <p class="text-light small mb-1">Elige entre Coca Cola, Fanta o Sprite.</p>
                                <span class="fw-bold text-warning d-block mb-2">$2.100</span>
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="d-flex align-items-center gap-2">
                                        <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 28px; height: 28px; padding:0;" onclick="cambiarCantCarta('bebidaLata', -1)">-</button>
                                        <span id="carta-cant-bebidaLata" class="fw-bold fs-6">1</span>
                                        <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 28px; height: 28px; padding:0;" onclick="cambiarCantCarta('bebidaLata', 1)">+</button>
                                    </div>
                                    <button class="btn btn-sm fw-bold px-3 btn-efecto" style="background-color: #23A9BD; color: #010310;" onclick="agregarBebidaCarta('Bebida Lata 350ml', 2100, 'bebidaLata')">Agregar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MODAL DE PERSONALIZACIÓN -->
        <div class="modal fade" id="modalPersonalizar" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content bg-dark text-white border-secondary">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title" id="modal-titulo" style="color: #8CE1EE;">Personalizar Plato</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-5 text-center mb-3">
                                <img id="modal-img" src="" alt="Plato" class="rounded img-fluid mb-2" style="height: 160px; width: 100%; object-fit: cover;">
                                <p id="modal-precio" class="fw-bold text-warning fs-5"></p>
                            </div>
                            <div class="col-md-7">
                                <div class="mb-3">
                                    <label for="observaciones" class="form-label small fw-bold" style="color: #23A9BD;">Instrucciones especiales (agregar / quitar):</label>
                                    <textarea class="form-control bg-dark text-white border-secondary" id="observaciones" rows="2" placeholder="Ej. Sin cebolla, extra picante..."></textarea>
                                </div>
                            </div>
                        </div>

                        <div class="border-top border-secondary pt-3 mt-2">
                            <h6 class="fw-bold mb-3" style="color: #8CE1EE;"><i class="bi bi-cup-straw"></i> Desea agregar bebestible o acompañamiento:</h6>
                            
                            <div class="d-flex justify-content-between align-items-center bg-black bg-opacity-25 p-2 rounded mb-2 border border-secondary">
                                <div>
                                    <span class="fw-bold">Bebida Lata 350ml</span><br>
                                    <small class="text-danger">+$2.100</small>
                                </div>
                                <div class="d-flex align-items-center gap-2">
                                    <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 32px; height: 32px;" onclick="cambiarCantidadModal('bebidaLata', -1)">-</button>
                                    <span id="cant-modal-bebidaLata" class="fw-bold fs-5 px-2">0</span>
                                    <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 32px; height: 32px;" onclick="cambiarCantidadModal('bebidaLata', 1)">+</button>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center bg-black bg-opacity-25 p-2 rounded mb-2 border border-secondary">
                                <div>
                                    <span class="fw-bold">Pan Naan Extra</span><br>
                                    <small class="text-danger">+$2.000</small>
                                </div>
                                <div class="d-flex align-items-center gap-2">
                                    <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 32px; height: 32px;" onclick="cambiarCantidadModal('naanExtra', -1)">-</button>
                                    <span id="cant-modal-naanExtra" class="fw-bold fs-5 px-2">0</span>
                                    <button type="button" class="btn btn-outline-light btn-sm rounded-circle" style="width: 32px; height: 32px;" onclick="cambiarCantidadModal('naanExtra', 1)">+</button>
                                </div>
                            </div>
                        </div>

                    </div>
                    <div class="modal-footer border-secondary justify-content-between align-items-center">
                        <span class="fs-5 fw-bold text-white" id="modal-total-calc">Total: $0</span>
                        <div>
                            <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn fw-bold btn-efecto px-4" style="background-color: #23A9BD; color: #010310;" onclick="agregarAlCarroPersonalizado()">Añadir al Carrito</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="container-fluid bg-dark py-3">
            <div class="row text-center"><div class="col-12" style="color: #23A9BD;"><strong>Jose-Tomas Guzman y Daniela Jara</strong></div></div>
        </div>

        <script>
            let cantBebidasCarta = { limonada: 1, bebidaLata: 1 };

            function cambiarCantCarta(tipo, cambio) {
                cantBebidasCarta[tipo] += cambio;
                if (cantBebidasCarta[tipo] < 1) cantBebidasCarta[tipo] = 1;
                document.getElementById("carta-cant-" + tipo).innerText = cantBebidasCarta[tipo];
            }

            function agregarBebidaCarta(nombre, precio, tipo) {
                let cantidad = cantBebidasCarta[tipo];
                agregarItemLocalStorage(nombre, precio, cantidad);
                cantBebidasCarta[tipo] = 1;
                document.getElementById("carta-cant-" + tipo).innerText = "1";
            }

            let productoSeleccionado = {};
            let cantidadesModal = { bebidaLata: 0, naanExtra: 0 };
            const preciosComplementos = { bebidaLata: 2100, naanExtra: 2000 };

            function abrirPersonalizador(nombre, precio, imagen) {
                productoSeleccionado = { nombre, precio };
                cantidadesModal = { bebidaLata: 0, naanExtra: 0 };
                
                document.getElementById("modal-titulo").innerText = nombre;
                document.getElementById("modal-precio").innerText = "$" + precio.toLocaleString();
                document.getElementById("modal-img").src = imagen;
                document.getElementById("observaciones").value = "";
                document.getElementById("cant-modal-bebidaLata").innerText = "0";
                document.getElementById("cant-modal-naanExtra").innerText = "0";
                
                actualizarTotalModal();
                let modal = new bootstrap.Modal(document.getElementById('modalPersonalizar'));
                modal.show();
            }

            function cambiarCantidadModal(tipo, cambio) {
                cantidadesModal[tipo] += cambio;
                if (cantidadesModal[tipo] < 0) cantidadesModal[tipo] = 0;
                document.getElementById("cant-modal-" + tipo).innerText = cantidadesModal[tipo];
                actualizarTotalModal();
            }

            function actualizarTotalModal() {
                let total = productoSeleccionado.precio;
                for (let tipo in cantidadesModal) {
                    total += cantidadesModal[tipo] * preciosComplementos[tipo];
                }
                document.getElementById("modal-total-calc").innerText = "Total: $" + total.toLocaleString();
            }

            function agregarAlCarroPersonalizado() {
                let obs = document.getElementById("observaciones").value.trim();
                let nombreFinal = productoSeleccionado.nombre;
                let precioFinal = productoSeleccionado.precio;

                if (obs) nombreFinal += ` (${obs})`;

                agregarItemLocalStorage(nombreFinal, precioFinal, 1);

                if (cantidadesModal.bebidaLata > 0) {
                    agregarItemLocalStorage("Bebida Lata 350ml", preciosComplementos.bebidaLata, cantidadesModal.bebidaLata);
                }
                if (cantidadesModal.naanExtra > 0) {
                    agregarItemLocalStorage("Pan Naan Extra", preciosComplementos.naanExtra, cantidadesModal.naanExtra);
                }

                let modalEl = document.getElementById('modalPersonalizar');
                let modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();
            }

            function agregarItemLocalStorage(nombre, precio, cantidad) {
                let carrito = JSON.parse(localStorage.getItem("carrito_restaurante")) || [];
                let item = carrito.find(i => i.nombre === nombre);
                if (item) { 
                    item.cantidad += cantidad; 
                } else { 
                    carrito.push({ nombre: nombre, precio: precio, cantidad: cantidad }); 
                }
                localStorage.setItem("carrito_restaurante", JSON.stringify(carrito));
                actualizarContador();
            }

            function actualizarContador() {
                let carrito = JSON.parse(localStorage.getItem("carrito_restaurante")) || [];
                let totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
                document.getElementById("contador-carrito").innerText = totalItems;
            }
            actualizarContador();
        </script>
    </body>
</html>