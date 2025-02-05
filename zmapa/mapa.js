// Inicializa el mapa
const map = L.map('map').setView([0, 0], 2); // Vista inicial centrada en (0, 0) con zoom 2

// Añade una capa de mapa base (usando OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Variable para almacenar los marcadores
let marcadores = [];

// Función para cargar y procesar el archivo CSV
function cargarCSV() {
    Papa.parse("zmapa/coordenadas.csv", {
        download: true,
        header: true,
        dynamicTyping: true,
        complete: function (results) {
            const datos = results.data;
            datos.forEach((fila) => {
                const id = fila.ID;
                const latitud = parseFloat(fila.Latitud);
                const longitud = parseFloat(fila.Longitud);

                // Añade un marcador al mapa
                if (!isNaN(latitud) && !isNaN(longitud)) {
                    const marcador = L.marker([latitud, longitud]).addTo(map)
                        .bindPopup(`ID: ${id}<br>Latitud: ${latitud}<br>Longitud: ${longitud}`);
                    marcadores.push({ id, marcador });
                }
            });

            // Ajusta el zoom y el centro del mapa para que se vean todos los puntos
            const grupoMarcadores = L.featureGroup(marcadores.map(m => m.marcador));
            map.fitBounds(grupoMarcadores.getBounds());
        },
        error: function (error) {
            console.error("Error al cargar el CSV:", error);
        }
    });
}

// Función para buscar un pluviómetro por ID
function buscarPluviometro() {
    const idBuscado = document.getElementById('searchInput').value.trim();
    if (!idBuscado) return;

    const marcadorEncontrado = marcadores.find(m => m.id === idBuscado);
    if (marcadorEncontrado) {
        map.setView(marcadorEncontrado.marcador.getLatLng(), 10); // Centra el mapa en el marcador
        marcadorEncontrado.marcador.openPopup(); // Abre el popup del marcador
    } else {
        alert(`No se encontró un pluviómetro con el ID: ${idBuscado}`);
    }
}

// Carga el CSV cuando la página esté lista
document.addEventListener("DOMContentLoaded", cargarCSV);

// Asigna la función de búsqueda al botón
document.getElementById('searchButton').addEventListener('click', buscarPluviometro);
