import glob
import os
import re
from tqdm import tqdm

# Ruta personalizada para los archivos de log (puedes cambiar esta ruta)
ruta_log = 'E02'  # Cambia esto por la ruta deseada
archivo_resultados = 'E02/pruebas.log'

# Verificar si la ruta existe, si no, crearla
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'

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

# Inicializamos el diccionario para almacenar las medias anuales
medias_anuales_totales = {}

# Procesar los archivos
for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
    with open(archivo, 'r') as f:
        # Saltar las dos primeras líneas de cabecera
        f.readline()
        f.readline()

        for linea in f:
            # Convertir la línea en una lista de valores
            partes = re.split(r'\s+', linea.strip())
            if len(partes) < 4:
                continue

            identificador = partes[0]  # Mantener el identificador como cadena
            anio = int(partes[1])
            mes = int(partes[2])
            precipitaciones = list(map(float, partes[3:]))  # Convertir los datos de precipitación a flotantes

            # Filtrar las precipitaciones válidas (no -999)
            precipitaciones_validas = [p for p in precipitaciones if p != -999]

            if not precipitaciones_validas:  # Si no hay precipitaciones válidas, no lo consideramos
                continue

            suma_precipitaciones = sum(precipitaciones_validas)

            # Acumular la suma de precipitaciones para este pluviómetro y año
            if (identificador, anio) not in medias_anuales_totales:
                medias_anuales_totales[(identificador, anio)] = {'suma': 0, 'contador': 0}

            medias_anuales_totales[(identificador, anio)]['suma'] += suma_precipitaciones
            medias_anuales_totales[(identificador, anio)]['contador'] += 1

            # Actualizar el total y el conteo de días válidos para el año
            if anio not in datos_globales:
                datos_globales[anio] = {'total': 0, 'dias': 0}

            datos_globales[anio]['total'] += sum(precipitaciones_validas)
            datos_globales[anio]['dias'] += len(precipitaciones_validas)

            # Buscar el día con la mayor y menor precipitación para los días pasados
            if 2006 <= anio <= 2024:
                for idx, precipitacion in enumerate(precipitaciones):
                    if precipitacion != -999:
                        if precipitacion > dia_mas_lluvioso_pasado['precipitacion']:
                            dia_mas_lluvioso_pasado = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                        if precipitacion < dia_menos_lluvioso_pasado['precipitacion']:
                            dia_menos_lluvioso_pasado = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}

            # Buscar el día con la mayor y menor precipitación para los días futuros
            if 2025 <= anio <= 2100:
                for idx, precipitacion in enumerate(precipitaciones):
                    if precipitacion != -999:
                        if precipitacion > dia_mas_lluvioso_futuro['precipitacion']:
                            dia_mas_lluvioso_futuro = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                        if precipitacion < dia_menos_lluvioso_futuro['precipitacion']:
                            dia_menos_lluvioso_futuro = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}

# Calcular la media anual final por pluviómetro
medias_anuales = {}
for (identificador, anio), datos_pluviometro in medias_anuales_totales.items():
    if datos_pluviometro['contador'] > 0:
        media_anual = datos_pluviometro['suma'] / 12  # Dividir la suma de precipitaciones entre 12 meses
        medias_anuales[(identificador, anio)] = media_anual

# Calcular la suma de medias anuales para cada año
suma_medias_por_anio = {}
for (identificador, anio), media_anual in medias_anuales.items():
    if anio not in suma_medias_por_anio:
        suma_medias_por_anio[anio] = 0
    suma_medias_por_anio[anio] += media_anual

# Calcular el número de pluviómetros por año
num_pluviometros_por_anio = {}
for (identificador, anio) in medias_anuales.keys():
    if anio not in num_pluviometros_por_anio:
        num_pluviometros_por_anio[anio] = 0
    num_pluviometros_por_anio[anio] += 1

# Calcular la media anual de precipitación por año en L/m² al año
medias_anuales_por_anio = {}
for anio in suma_medias_por_anio:
    if num_pluviometros_por_anio[anio] > 0:
        medias_anuales_por_anio[anio] = suma_medias_por_anio[anio] / num_pluviometros_por_anio[anio]

# Separar años pasados (2006-2024) y futuros (2025-2100)
datos_pasados = {k: v for k, v in datos_globales.items() if 2006 <= k <= 2024}
datos_futuros = {k: v for k, v in datos_globales.items() if 2025 <= k <= 2100}

# Identificar los años más lluviosos y los más secos
lluviosos_pasados = sorted(datos_pasados.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
secos_pasados = sorted(datos_pasados.items(), key=lambda x: x[1]['total'])[:10]
lluviosos_futuros = sorted(datos_futuros.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
secos_futuros = sorted(datos_futuros.items(), key=lambda x: x[1]['total'])[:10]

# Calcular promedios de precipitación por período (basados en la media anual)
promedio_pasados = sum(medias_anuales_por_anio.get(anio, 0) for anio in range(2006, 2025)) / len(range(2006, 2025)) if datos_pasados else 0
promedio_futuros = sum(medias_anuales_por_anio.get(anio, 0) for anio in range(2025, 2101)) / len(range(2025, 2101)) if datos_futuros else 0

# Identificar mayor incremento y decremento de precipitación (basados en la media anual)
mayor_incremento = {'anio': None, 'incremento': float('-inf')}
mayor_decremento = {'anio': None, 'decremento': float('inf')}

anio_anterior = None
media_anterior = None

for anio in sorted(medias_anuales_por_anio):
    media_actual = medias_anuales_por_anio[anio]
    if anio_anterior is not None and media_anterior is not None:
        diferencia = media_actual - media_anterior
        if diferencia > mayor_incremento['incremento']:
            mayor_incremento = {'anio': anio, 'incremento': diferencia}
        if diferencia < mayor_decremento['decremento']:
            mayor_decremento = {'anio': anio, 'decremento': diferencia}
    anio_anterior = anio
    media_anterior = media_actual

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

    # Añadir promedios de precipitación (basados en la media anual)
    log.write("Promedios de Precipitación (basados en la media anual):\n")
    log.write(f"Promedio años pasados (2006-2024): {promedio_pasados:.2f} L/m² al año\n")
    log.write(f"Promedio años futuros (2025-2100): {promedio_futuros:.2f} L/m² al año\n")

    log.write("\n")  # Separador

    # Añadir mayor incremento y decremento (basados en la media anual)
    log.write("Mayor Incremento y Decremento de Precipitación (basados en la media anual):\n")
    if mayor_incremento['anio'] is not None:
        log.write(f"Mayor incremento: Año {mayor_incremento['anio']} con {mayor_incremento['incremento']:.2f} L/m² al año\n")
    if mayor_decremento['anio'] is not None:
        log.write(f"Mayor decremento: Año {mayor_decremento['anio']} con {mayor_decremento['decremento']:.2f} L/m² al año\n")

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

    for anio in sorted(datos_globales):
        total_anual = datos_globales[anio]['total']
        media_anual = medias_anuales_por_anio.get(anio, 0)  # Usar la media anual del segundo método

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
