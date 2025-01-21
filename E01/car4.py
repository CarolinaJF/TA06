import glob
import os
import re  # Para usar expresiones regulares
from tqdm import tqdm  # Importamos tqdm para la barra de progreso

# Ruta personalizada para los archivos de log (puedes cambiar esta ruta)
ruta_log = 'E01'  # Cambia esto por la ruta deseada, por ejemplo: 'C:/mis_logs' o '/home/usuario/logs'

# Verificar si la ruta existe, si no, crearla
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'

# Patrón para buscar archivos .dat
patron = '*.dat'

# Obtener la lista de archivos .dat en la carpeta
archivos = glob.glob(os.path.join(carpeta, patron))

# Crear un archivo de log para guardar los errores (modo 'a' para no sobrescribir)
archivo_log = os.path.join(ruta_log, 'pruebas.log')

# Diccionario para acumular precipitaciones y días por año
lluvia_por_anio = {}
dias_por_anio = {}

# Inicializamos contadores globales
total_archivos = 0
total_lineas = 0
total_faltantes = 0

# Parámetros esperados para la primera fila
parametros_primera_fila = ['precip', 'MIROC5', 'RCP60', 'REGRESION', 'decimas', '1']

# Inicializamos la barra de progreso con tqdm
with open(archivo_log, 'a') as log:
    # Usamos tqdm para la barra de progreso en los archivos
    for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
        with open(archivo, 'r') as f:
            contenido = f.read()

            # Dividir el contenido en líneas, eliminando líneas vacías al final del archivo
            lines = contenido.strip().split('\n')

            # Verificar que haya suficientes líneas para evitar errores de índice
            if len(lines) > 2:  # Empezamos desde la segunda línea
                total_archivos += 1  # Contamos el archivo procesado

                # Procesar las líneas desde la tercera
                for i, linea in enumerate(lines[2:], start=3):  # Empezamos desde la tercera línea
                    if not linea.strip():  # Si la línea está vacía o solo contiene espacios en blanco
                        log.write(f"ERROR: Línea vacía detectada en el archivo {archivo}, línea {i}\n")
                        continue

                    # Dividir las columnas usando re.split para manejar espacios múltiples
                    columnas = re.split(r'\s+', linea.strip())

                    # Validar la columna 2 (años) y obtener precipitaciones
                    if len(columnas) > 1:
                        try:
                            anio = int(columnas[1])  # Columna 2: Año
                            valores_diarios = list(map(float, columnas[2:]))  # Datos de lluvia desde la columna 3

                            # Inicializar acumuladores para el año si no existen
                            if anio not in lluvia_por_anio:
                                lluvia_por_anio[anio] = 0.0
                                dias_por_anio[anio] = 0

                            for valor in valores_diarios:
                                if valor != -999:  # Excluir valores faltantes
                                    lluvia_por_anio[anio] += valor
                                    dias_por_anio[anio] += 1
                                else:
                                    total_faltantes += 1
                        except ValueError:
                            log.write(f"ERROR: Datos inválidos en el archivo {archivo}, línea {i}: {linea}\n")
                            continue

# Calcular los promedios por año
promedios_por_anio = {anio: lluvia_por_anio[anio] / dias_por_anio[anio] for anio in lluvia_por_anio if dias_por_anio[anio] > 0}

# Guardar los resultados en el log
with open(archivo_log, 'a') as log:
    log.write("\nPromedios de lluvia por año (litros por metro cuadrado):\n")
    for anio, promedio in sorted(promedios_por_anio.items()):
        log.write(f"Año {anio}: {promedio:.2f} litros/m²\n")

    # Escribir resumen final
    log.write("\nResumen Final:\n")
    log.write(f"Total de archivos procesados: {total_archivos}\n")
    log.write(f"Total de líneas procesadas: {total_lineas}\n")
    log.write(f"Total de valores faltantes (-999): {total_faltantes}\n")
    log.write('\n')
