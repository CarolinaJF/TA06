import glob
import os
import re
from tqdm import tqdm

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/ayuda1'
# Patrón para buscar archivos .dat
patron = '*.dat'
# Obtener la lista de archivos .dat en la carpeta
archivos = glob.glob(os.path.join(carpeta, patron))

# Ruta personalizada para guardar el resultado
ruta_resultados = 'E02'
if not os.path.exists(ruta_resultados):
    os.makedirs(ruta_resultados)

# Archivo donde guardar los resultados
archivo_resultados = os.path.join(ruta_resultados, 'resultados_lluvias_agrupados.log')

# Inicializar el log de resultados
with open(archivo_resultados, 'w') as log:
    log.write("Resultados Globales de Precipitación Total y Media Anual\n\n")

# Inicializar diccionario global para almacenar totales y conteos por año
datos_globales = {}

# Procesar cada archivo
for archivo in tqdm(archivos, desc="Calculando medias y totales", unit="archivo"):
    try:
        with open(archivo, 'r') as f:
            contenido = f.read()

        # Dividir el contenido en líneas y omitir líneas vacías al final
        lines = contenido.strip().split('\n')

        # Verificar que hay suficientes líneas para evitar errores
        if len(lines) < 3:
            with open(archivo_resultados, 'a') as log:
                log.write(f"Archivo {archivo}: No tiene suficientes datos para procesar.\n\n")
            continue

        # Procesar líneas a partir de la tercera
        for linea in lines[2:]:
            columnas = re.split(r'\s+', linea.strip())

            # Validar que haya suficientes columnas (mínimo año, mes y un dato de precipitación)
            if len(columnas) < 4:
                continue

            try:
                # Extraer año y datos de precipitación
                anio = int(columnas[1])  # Columna 2 es el año
                precipitaciones = [float(valor) for valor in columnas[3:] if float(valor) != -999]

                # Sumar precipitaciones totales y contar días
                if anio not in datos_globales:
                    datos_globales[anio] = {'total': 0, 'dias': 0}

                datos_globales[anio]['total'] += sum(precipitaciones)
                datos_globales[anio]['dias'] += len(precipitaciones)

            except ValueError:
                continue  # Ignorar líneas con datos inválidos

    except Exception as e:
        with open(archivo_resultados, 'a') as log:
            log.write(f"Error procesando archivo {archivo}: {str(e)}\n\n")

# Escribir los resultados globales
with open(archivo_resultados, 'a') as log:
    log.write("Resultados Globales Agrupados:\n")
    log.write("Año\tTotal Precipitación (L/m²)\tMedia Anual (L/m²)\n")
    for anio, datos in sorted(datos_globales.items()):
        total_anual = datos['total']
        media_anual = total_anual / datos['dias'] if datos['dias'] > 0 else 0
        log.write(f"{anio}\t{total_anual:.2f}\t{media_anual:.2f}\n")
    log.write("\n")
