const respuestaAPI = {
    "status": 200,
    "mesagge": "¡Disciplinas obtenidas!",
    "data": [
        {
            "Nombre": "Basketball",
            "Descripcion": "",
            "imagen": "img/futbol.jpeg"
        },
        {
            "Nombre": "Football",
            "Descripcion": "",
            "imagen": "img/basket.jpg"
        },
        {
            "Nombre": "League of Legends Esports",
            "Descripcion": "",
            "imagen": "img/lol.jpg"
        }
    ]
};

function mostrarDisciplinas() {
    let contenedor = document.getElementById("Disciplinas")
    contenedor.innerHTML = "";
    respuestaAPI.data.forEach(disciplina => {
        let col = document.createElement("div");
        col.setAttribute("class", "col-md-4 mb-4");
    });
}