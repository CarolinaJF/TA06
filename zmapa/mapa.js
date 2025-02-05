// Inicializa el mapa
const map = L.map('map').setView([0, 0], 2); // Vista inicial centrada en (0, 0) con zoom 2

// Añade una capa de mapa base (usando OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Función para cargar y procesar el archivo CSV
function cargarCSV() {
    Papa.parse("coordenadas.csv", {
        download: true,
        header: true,
        dynamicTyping: true,
        complete: function (results) {
            const datos = results.data;
            datos.forEach((fila) => {
                const latitud = parseFloat(fila.Latitud);
                const longitud = parseFloat(fila.Longitud);

                // Añade un marcador al mapa
                if (!isNaN(latitud) && !isNaN(longitud)) {
                    L.marker([latitud, longitud]).addTo(map)
                        .bindPopup(`Latitud: ${latitud}<br>Longitud: ${longitud}`);
                }
            });

            // Ajusta el zoom y el centro del mapa para que se vean todos los puntos
            const grupoMarcadores = L.featureGroup(
                datos.map((fila) => {
                    const latitud = parseFloat(fila.Latitud);
                    const longitud = parseFloat(fila.Longitud);
                    return L.marker([latitud, longitud]);
                })
            );
            map.fitBounds(grupoMarcadores.getBounds());
        },
        error: function (error) {
            console.error("Error al cargar el CSV:", error);
        }
    });
}

// Carga el CSV cuando la página esté lista
document.addEventListener("DOMContentLoaded", cargarCSV);