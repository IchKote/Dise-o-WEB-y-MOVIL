<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Tu Carrito - Masala</title>
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
                <a href="carta.php" class="btn btn-outline-light btn-efecto" style="border-color: #23A9BD; color: #8CE1EE;">
                    <i class="bi bi-arrow-left"></i> Volver a la Carta
                </a>
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
                    <li class="nav-item mb-2"><a class="nav-link text-white" href="ubicacion.php">UBICACIÓN</a></li>
                </ul>
                <div class="d-flex flex-column gap-2 border-top border-secondary pt-3">
                    <a href="ubicacion.php" class="text-light text-decoration-none"><i class="bi bi-geo-alt-fill" style="color: #23A9BD;"></i> Santiago, Chile</a>
                </div>
            </div>
        </div>

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
                    <div class="d-flex gap-4">
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
        <div class="container-fluid bg-dark py-3">
            <div class="row text-center"><div class="col-12" style="color: #23A9BD;"><strong>Jose-Tomas Guzman y Daniela Jara</strong></div></div>
        </div>

        <script>
            function cargarCarrito() {
                let carrito = JSON.parse(localStorage.getItem("carrito_restaurante")) || [];
                let lista = document.getElementById("lista-carrito");
                let subtotalElem = document.getElementById("lbl-subtotal");
                let envioElem = document.getElementById("lbl-envio");
                let totalElem = document.getElementById("lbl-total");
                
                lista.innerHTML = "";
                if (carrito.length === 0) {
                    lista.innerHTML = '<li class="list-group-item bg-transparent text-muted border-secondary text-center">Tu carro está vacío</li>';
                    subtotalElem.innerText = "$0"; envioElem.innerText = "$0"; totalElem.innerText = "$0";
                    return;
                }

                let subtotal = 0;
                carrito.forEach((item, index) => {
                    let totalItem = item.precio * item.cantidad;
                    subtotal += totalItem;
                    let li = document.createElement("li");
                    li.className = "list-group-item bg-transparent text-white border-secondary d-flex justify-content-between align-items-center px-0 py-3";
                    li.innerHTML = `
                        <div class="d-flex align-items-center">
                            <div>
                                <strong>${item.nombre}</strong><br>
                                <span class="badge bg-secondary mt-1">Cantidad: x ${item.cantidad}</span>
                            </div>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <span class="fw-bold text-warning">$${totalItem.toLocaleString()}</span>
                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="eliminarItem(${index})"><i class="bi bi-trash"></i></button>
                        </div>
                    `;
                    lista.appendChild(li);
                });

                let esDelivery = document.getElementById("delivery").checked;
                let costoEnvio = esDelivery ? 2000 : 0;
                subtotalElem.innerText = "$" + subtotal.toLocaleString();
                envioElem.innerText = "$" + costoEnvio.toLocaleString();
                totalElem.innerText = "$" + (subtotal + costoEnvio).toLocaleString();
            }

            function cambiarTipoEntrega() {
                let esDelivery = document.getElementById("delivery").checked;
                document.getElementById("campo-direccion").style.display = esDelivery ? "block" : "none";
                cargarCarrito();
            }

            function eliminarItem(index) {
                let carrito = JSON.parse(localStorage.getItem("carrito_restaurante")) || [];
                carrito.splice(index, 1);
                localStorage.setItem("carrito_restaurante", JSON.stringify(carrito));
                cargarCarrito();
            }

            function finalizarCompra() {
                let carrito = JSON.parse(localStorage.getItem("carrito_restaurante")) || [];
                if (carrito.length === 0) { alert("Tu carrito está vacío."); return; }
                if (document.getElementById("delivery").checked && !document.getElementById("direccion").value) {
                    alert("Por favor ingresa la dirección de entrega."); return;
                }
                alert("¡Pedido confirmado con éxito!");
                localStorage.removeItem("carrito_restaurante");
                window.location.href = "carta.php";
            }
            cargarCarrito();
        </script>
    </body>
</html>