const respuestaAPI = {
    "status": 200,
    "message": "¡Disciplinas obtenidas!",
    "data": [
        {
            "Nombre": "Football",
            "Descripcion": "Juego de equipo en el que dos equipos intentan meter un balón en el portero del equipo contrario.",
            "imagen": "img/futbol.jpeg"
        },
        {
            "Nombre": "Basketball",
            "Descripcion": "Juego de equipo en el que dos equipos intentan meter una pelota en un aro elevado.",
            "imagen": "img/basket.jpg"
        },
        {
            "Nombre": "League of Legends Esports",
            "Descripcion": "Juego de estrategia en equipo donde dos equipos compiten para destruir la base del equipo contrario.",
            "imagen": "img/lol.jpg"
        }
    ]
};

function mostrarDisciplinas() {
    let contenedor = document.getElementById("Disciplinas");
    if (!contenedor) return;

    contenedor.innerHTML = "";

    respuestaAPI.data.forEach(disciplina => {
        let col = document.createElement("div");
        col.setAttribute("class", "col-md-4 mb-4");

        let card = document.createElement("div");
        card.setAttribute("class", "card h-100 bg-dark text-white border-secondary shadow");

        let img = document.createElement("img");
        img.setAttribute("src", disciplina.imagen);
        img.setAttribute("class", "card-img-top");
        img.setAttribute("alt", disciplina.Nombre);
        img.setAttribute("style", "height: 200px; object-fit: cover;");

        let cardBody = document.createElement("div");
        cardBody.setAttribute("class", "card-body d-flex flex-column");
        
        let titulo = document.createElement("h5");
        titulo.setAttribute("class", "card-title");
        titulo.setAttribute("style", "color: #02F5A1; font-weight: bold;");
        titulo.innerText = disciplina.Nombre;

        let desc = document.createElement("p");
        desc.setAttribute("class", "card-text text-light");
        desc.innerText = disciplina.Descripcion;


        cardBody.appendChild(titulo);
        cardBody.appendChild(descripcion);

        card.appendChild(img);
        card.appendChild(cardBody);

        col.appendChild(card);

        contenedor.appendChild(col);
    });

    let botonCargar = document.getElementById("btn-cargar");
    if (botonCargar) {
        botonCargar.style.display = "none";
    }
}