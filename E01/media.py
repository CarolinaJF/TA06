import glob
import os
import re  # Para usar expresiones regulares
from tqdm import tqdm  # Importamos tqdm para la barra de progreso

# Ruta personalizada para los archivos de log (puedes cambiar esta ruta)
ruta_log = 'E02'  # Cambia esto por la ruta deseada, por ejemplo: 'C:/mis_logs' o '/home/usuario/logs'

# Verificar si la ruta existe, si no, crearla
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/ayuda1'

# Patrón para buscar archivos .dat
patron = '*.dat'

# Obtener la lista de archivos .dat en la carpeta
archivos = glob.glob(os.path.join(carpeta, patron))

# Crear un archivo de log para guardar los resultados (modo 'a' para no sobrescribir)
archivo_resultados = os.path.join(ruta_log, 'resultados_globales.log')

# Inicializamos el diccionario para almacenar los resultados
datos_globales = {}

# Procesar los archivos
for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
    with open(archivo, 'r') as f:
        contenido = f.read()

        # Dividir el contenido en líneas, eliminando líneas vacías al final del archivo
        lines = contenido.strip().split('\n')

        # Verificar que haya suficientes líneas para evitar errores de índice
        if len(lines) > 2:  # Empezamos desde la tercera línea
            for linea in lines[2:]:  # Procesar las líneas desde la tercera
                if not linea.strip():  # Si la línea está vacía o solo contiene espacios en blanco
                    continue

                # Dividir las columnas usando re.split para manejar espacios múltiples
                columnas = re.split(r'\s+', linea.strip())

                if len(columnas) < 4:
                    continue

                # Extraer los datos
                try:
                    anio = int(columnas[1])  # Columna 2: año
                    datos_dia = list(map(float, columnas[3:]))  # A partir de la columna 4: datos diarios

                    if anio not in datos_globales:
                        datos_globales[anio] = {'total': 0, 'dias': 0}

                    # Actualizar el total y el conteo de días válidos para el año
                    datos_globales[anio]['total'] += sum(d for d in datos_dia if d != -999)
                    datos_globales[anio]['dias'] += sum(1 for d in datos_dia if d != -999)
                except ValueError:
                    continue

# Escribir los resultados globales con formato alineado
with open(archivo_resultados, 'w') as log:
    # Encabezado con formato alineado
    log.write(f"{'Año':<6}{'Total Precipitación (L/m²)':<30}{'Media Anual (L/m² al Año)':<30}{'Tasa de Variación (%)':<25}\n")
    log.write("=" * 91 + "\n")  # Separador visual
    
    anio_anterior = None
    total_anterior = None
    
    for anio, datos in sorted(datos_globales.items()):
        total_anual = datos['total']
        media_anual = (total_anual / datos['dias'] * 365) if datos['dias'] > 0 else 0
        
        # Calcular la tasa de variación sobre el total anual
        if anio_anterior is not None and total_anterior > 0:
            tasa_variacion = ((total_anual - total_anterior) / total_anterior) * 100
        else:
            tasa_variacion = None
        
        # Escribir resultados al log con formato
        if tasa_variacion is not None:
            log.write(f"{anio:<6}{total_anual:<30.2f}{media_anual:<30.2f}{tasa_variacion:<25.2f}\n")
        else:
            log.write(f"{anio:<6}{total_anual:<30.2f}{media_anual:<30.2f}{'N/A':<25}\n")
        
        # Actualizar valores del año anterior
        anio_anterior = anio
        total_anterior = total_anual

    log.write("\n")

print(f"Resultados globales guardados en: {archivo_resultados}")
