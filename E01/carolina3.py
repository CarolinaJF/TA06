import glob
import os
import re  # Para usar expresiones regulares
from tqdm import tqdm  # Importamos tqdm para la barra de progreso

# Ruta personalizada para los archivos de log (puedes cambiar esta ruta)
ruta_log = 'E02/pruebas.log' # Cambia esto por la ruta deseada, por ejemplo: 'C:/mis_logs' o '/home/usuario/logs'
archivo_resultados = 'E02/pruebas.log'

# Verificar si la ruta existe, si no, crearla
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/ayuda1'

# Patrón para buscar archivos .dat
patron = '*.dat'

# Obtener la lista de archivos .dat en la carpeta
archivos = glob.glob(os.path.join(carpeta, patron))

# Inicializamos el diccionario para almacenar los resultados
datos_globales = {}

# Inicializar variables para los días con mayor y menor precipitación
dia_mas_lluvioso_pasado = {'anio': None, 'dia': None, 'precipitacion': float('-inf')}
dia_menos_lluvioso_pasado = {'anio': None, 'dia': None, 'precipitacion': float('inf')}
dia_mas_lluvioso_futuro = {'anio': None, 'dia': None, 'precipitacion': float('-inf')}
dia_menos_lluvioso_futuro = {'anio': None, 'dia': None, 'precipitacion': float('inf')}

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

                    # Buscar el día con la mayor y menor precipitación para los días pasados
                    if 2006 <= anio <= 2024:
                        for idx, precipitacion in enumerate(datos_dia):
                            if precipitacion != -999:
                                if precipitacion > dia_mas_lluvioso_pasado['precipitacion']:
                                    dia_mas_lluvioso_pasado = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                                if precipitacion < dia_menos_lluvioso_pasado['precipitacion']:
                                    dia_menos_lluvioso_pasado = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}

                    # Buscar el día con la mayor y menor precipitación para los días futuros
                    if 2025 <= anio <= 2100:
                        for idx, precipitacion in enumerate(datos_dia):
                            if precipitacion != -999:
                                if precipitacion > dia_mas_lluvioso_futuro['precipitacion']:
                                    dia_mas_lluvioso_futuro = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                                if precipitacion < dia_menos_lluvioso_futuro['precipitacion']:
                                    dia_menos_lluvioso_futuro = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}

                except ValueError:
                    continue

# Separar años pasados (2006-2024) y futuros (2025-2100)
datos_pasados = {k: v for k, v in datos_globales.items() if 2006 <= k <= 2024}
datos_futuros = {k: v for k, v in datos_globales.items() if 2025 <= k <= 2100}

# Identificar los años más lluviosos y los más secos
lluviosos_pasados = sorted(datos_pasados.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
secos_pasados = sorted(datos_pasados.items(), key=lambda x: x[1]['total'])[:10]
lluviosos_futuros = sorted(datos_futuros.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
secos_futuros = sorted(datos_futuros.items(), key=lambda x: x[1]['total'])[:10]

# Calcular promedios de precipitación por período
promedio_pasados = sum(d['total'] for d in datos_pasados.values()) / len(datos_pasados) if datos_pasados else 0
promedio_futuros = sum(d['total'] for d in datos_futuros.values()) / len(datos_futuros) if datos_futuros else 0

# Identificar mayor incremento y decremento de precipitación
mayor_incremento = {'anio': None, 'incremento': float('-inf')}
mayor_decremento = {'anio': None, 'decremento': float('inf')}  # Cambié a 'inf' en vez de '-inf'

anio_anterior = None
total_anterior = None

for anio in sorted(datos_globales):
    total_actual = datos_globales[anio]['total']
    if anio_anterior is not None and total_anterior is not None:
        diferencia = total_actual - total_anterior
        if diferencia > mayor_incremento['incremento']:
            mayor_incremento = {'anio': anio, 'incremento': diferencia}
        if diferencia < mayor_decremento['decremento']:  # Cambié a '<' en vez de '>'
            mayor_decremento = {'anio': anio, 'decremento': diferencia}
    anio_anterior = anio
    total_anterior = total_actual

# Escribir los resultados globales con formato alineado
with open(archivo_resultados, 'a') as log:
    # Tabla de años pasados más lluviosos
    log.write("Años pasados más lluviosos (2006-2024):\n")
    log.write(f"{'Año':<6}{'Total Precipitación (L/m²)':<30}\n")
    log.write("=" * 36 + "\n")
    for anio, datos in lluviosos_pasados:
        log.write(f"{anio:<6}{int(datos['total']):<30}\n")

    log.write("\n")  # Separador

    # Tabla de años pasados más secos
    log.write("Años pasados más secos (2006-2024):\n")
    log.write(f"{'Año':<6}{'Total Precipitación (L/m²)':<30}\n")
    log.write("=" * 36 + "\n")
    for anio, datos in secos_pasados:
        log.write(f"{anio:<6}{int(datos['total']):<30}\n")

    log.write("\n")  # Separador

    # Tabla de años futuros más lluviosos
    log.write("Años futuros más lluviosos (2025-2100):\n")
    log.write(f"{'Año':<6}{'Total Precipitación (L/m²)':<30}\n")
    log.write("=" * 36 + "\n")
    for anio, datos in lluviosos_futuros:
        log.write(f"{anio:<6}{int(datos['total']):<30}\n")

    log.write("\n")  # Separador

    # Tabla de años futuros más secos
    log.write("Años futuros más secos (2025-2100):\n")
    log.write(f"{'Año':<6}{'Total Precipitación (L/m²)':<30}\n")
    log.write("=" * 36 + "\n")
    for anio, datos in secos_futuros:
        log.write(f"{anio:<6}{int(datos['total']):<30}\n")

    log.write("\n" + "=" * 91 + "\n\n")  # Separador visual para las secciones

    # Añadir promedios de precipitación
    log.write("Promedios de Precipitación:\n")
    log.write(f"Promedio años pasados (2006-2024): {promedio_pasados:.2f} L/m²\n")
    log.write(f"Promedio años futuros (2025-2100): {promedio_futuros:.2f} L/m²\n")

    log.write("\n")  # Separador

    # Añadir mayor incremento y decremento
    log.write("Mayor Incremento y Decremento de Precipitación:\n")
    if mayor_incremento['anio'] is not None:
        log.write(f"Mayor incremento: Año {mayor_incremento['anio']} con {int(mayor_incremento['incremento'])} L/m²\n")  # Convirtiendo a entero
    if mayor_decremento['anio'] is not None:
        log.write(f"Mayor decremento: Año {mayor_decremento['anio']} con {int(mayor_decremento['decremento'])} L/m²\n")  # Convirtiendo a entero

    log.write("\n" + "=" * 91 + "\n\n")

    # Añadir los días con mayor y menor precipitación
    log.write("Días con más y menos precipitación:\n")
    log.write(f"Día más lluvioso en años pasados (2006-2024): Año {dia_mas_lluvioso_pasado['anio']} - Día {dia_mas_lluvioso_pasado['dia']} con {dia_mas_lluvioso_pasado['precipitacion']} L/m²\n")
    log.write(f"Día menos lluvioso en años pasados (2006-2024): Año {dia_menos_lluvioso_pasado['anio']} - Día {dia_menos_lluvioso_pasado['dia']} con {dia_menos_lluvioso_pasado['precipitacion']} L/m²\n")
    log.write(f"Día más lluvioso en años futuros (2025-2100): Año {dia_mas_lluvioso_futuro['anio']} - Día {dia_mas_lluvioso_futuro['dia']} con {dia_mas_lluvioso_futuro['precipitacion']} L/m²\n")
    log.write(f"Día menos lluvioso en años futuros (2025-2100): Año {dia_menos_lluvioso_futuro['anio']} - Día {dia_menos_lluvioso_futuro['dia']} con {dia_menos_lluvioso_futuro['precipitacion']} L/m²\n")

    log.write("\n" + "=" * 91 + "\n\n")

    # Encabezado con formato alineado para los resultados globales
    log.write(f"{'Año':<6}{'Total Precipitación (L/m²)':<30}{'Media Anual (L/m² al Año)':<30}{'Tasa de Variación (%)':<25}\n")
    log.write("=" * 91 + "\n")

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
            log.write(f"{anio:<6}{int(total_anual):<30}{media_anual:<30.2f}{tasa_variacion:<25.2f}\n")
        else:
            log.write(f"{anio:<6}{int(total_anual):<30}{media_anual:<30.2f}{'N/A':<25}\n")

        # Actualizar valores del año anterior
        anio_anterior = anio
        total_anterior = total_anual

    log.write("\n")

print(f"Resultados globales guardados en: {archivo_resultados}")
