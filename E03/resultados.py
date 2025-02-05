import glob
import os
import re
from tqdm import tqdm
from datetime import datetime
import csv

# Ruta personalizada para los archivos de log (puedes cambiar esta ruta)
ruta_log = 'E03'  # Cambia esto por la ruta deseada, por ejemplo: 'C:/mis_logs' o '/home/usuario/logs'

# Verificar si la ruta existe, si no, crearla
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/ayuda1'

# Crear un archivo de log para guardar los errores (modo 'a' para no sobrescribir)
archivo_log = os.path.join(ruta_log, 'datos.log')

# Registrar la fecha y hora actual en el archivo de log
with open(archivo_log, 'a', encoding='utf-8') as log:
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.write(f"Fecha y hora de inicio del procesamiento: {fecha_actual}\n\n")

# Validar si la carpeta existe
if not os.path.exists(carpeta):
    with open(archivo_log, 'a', encoding='utf-8') as log:
        log.write(f"ERROR: La carpeta {carpeta} no existe. Verifica la ruta.\n")
    exit()  # Detener el script si la carpeta no existe

# Patrón para buscar archivos .dat
patron = '*.dat'

# Obtener la lista de archivos .dat en la carpeta
archivos = glob.glob(os.path.join(carpeta, patron))

# Validar si hay archivos .dat en la carpeta
if not archivos:
    with open(archivo_log, 'a', encoding='utf-8') as log:
        log.write(f"ERROR: No se encontraron archivos .dat en la carpeta {carpeta}.\n")
    exit()  # Detener el script si no hay archivos .dat

# Inicializamos contadores globales
total_valores = 0
total_faltantes = 0
total_archivos = 0
total_lineas = 0

# Parámetros esperados para la primera fila
parametros_primera_fila = ['precip', 'MIROC5', 'RCP60', 'REGRESION', 'decimas', '1']

# Parámetros esperados para la segunda fila (columnas fijas)
parametros_segunda_fila_fija = ['182', 'geo', '2006', '2100', '-1']

# Rango válido de años
anio_minimo = 2006
anio_maximo = 2100

# Inicializamos la barra de progreso con tqdm
with open(archivo_log, 'a', encoding='utf-8') as log:
    # Usamos tqdm para la barra de progreso en los archivos
    for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
        with open(archivo, 'r') as f:
            contenido = f.read()

            # Dividir el contenido en líneas, eliminando líneas vacías al final del archivo
            lines = contenido.strip().split('\n')

            # Verificar que haya suficientes líneas para evitar errores de índice
            if len(lines) > 2:  # Empezamos desde la segunda línea
                total_archivos += 1  # Contamos el archivo procesado
                lineas_archivo = 0  # Contador de líneas procesadas en este archivo

                # Verificar la primera fila
                primera_fila = lines[0].strip().split()
                if primera_fila != parametros_primera_fila:
                    log.write(f"ERROR: La primera fila en el archivo {archivo} no contiene los parámetros esperados: {parametros_primera_fila}, encontrada: {primera_fila}\n\n")

                # Obtener la segunda línea (que contiene los parámetros esperados)
                segunda_linea = lines[1].strip().split()

                # Verificar las columnas 2 y 3 (variables) y el resto de columnas fijas
                if len(segunda_linea) >= 4:
                    columna2 = segunda_linea[1]
                    columna3 = segunda_linea[2]
                    columnas_fijas = segunda_linea[3:]

                    # Verificar que las columnas 2 y 3 sean números
                    try:
                        float(columna2)
                    except ValueError:
                        log.write(f"ERROR: La columna 2 (valor: {columna2}) no es un número válido en el archivo {archivo}, línea 2\n\n")

                    try:
                        float(columna3)
                    except ValueError:
                        log.write(f"ERROR: La columna 3 (valor: {columna3}) no es un número válido en el archivo {archivo}, línea 2\n\n")

                    # Verificar que las columnas 4 a 7 coincidan con los valores fijos
                    if columnas_fijas != parametros_segunda_fila_fija:
                        log.write(f"ERROR: La segunda fila no coincide con los valores esperados en el archivo {archivo}, línea 2. Esperado: {parametros_segunda_fila_fija}, encontrado: {columnas_fijas}\n\n")
                else:
                    log.write(f"ERROR: La segunda fila en el archivo {archivo} no tiene suficientes columnas para la validación en línea 2\n\n")

                # Obtener el ID del pluviómetro desde la primera columna de la segunda línea
                id_pluviometro = segunda_linea[0]  # La primera columna en la segunda línea

                # Diccionario para contar los meses por año
                meses_por_anio = {}

                # Procesar las líneas desde la tercera
                for i, linea in enumerate(lines[2:], start=3):  # Empezamos desde la tercera línea
                    lineas_archivo += 1
                    if not linea.strip():  # Si la línea está vacía o solo contiene espacios en blanco
                        log.write(f"ERROR: Línea vacía detectada en el archivo {archivo}, línea {i}\n\n")
                        continue

                    # Dividir las columnas usando re.split para manejar espacios múltiples
                    columnas = re.split(r'\s+', linea.strip())

                    # Verificar que el ID del pluviómetro en la primera columna coincida con el de la segunda línea
                    if columnas[0] != id_pluviometro:
                        log.write(f"ERROR: El ID del pluviómetro no coincide en el archivo {archivo}, línea {i}, valor esperado: {id_pluviometro}, encontrado: {columnas[0]}\n\n")

                    # Verificar que la cantidad de valores en la fila no supere 34
                    if len(columnas) > 34:
                        log.write(f"ERROR: Más de 31 días en la fila del archivo {archivo}, línea {i}, días: {len(columnas)-3}\n\n")

                    # Validar la columna 2 (años)
                    if len(columnas) > 1:
                        anio = columnas[1]
                        if re.match(r'^\d{4}$', anio):  # Verificar que sea un año válido
                            anio = int(anio)  # Convertir a entero para comparar
                            # Verificar si el año está fuera del rango 2006-2100
                            if anio < anio_minimo or anio > anio_maximo:
                                log.write(f"ERROR: El año {anio} en el archivo {archivo}, línea {i} está fuera del rango válido (2006-2100)\n\n")
                            else:
                                # Solo contar los meses si el año está dentro del rango válido
                                if anio not in meses_por_anio:
                                    meses_por_anio[anio] = 0
                                meses_por_anio[anio] += 1

                    # Excluir la primera columna para las demás verificaciones
                    columnas = columnas[1:]

                    # Verificar si las columnas contienen caracteres no deseados y contar los valores
                    caracteres_no_deseados = []
                    for columna in columnas:
                        try:
                            # Intentar convertir a número flotante
                            numero = float(columna)
                            total_valores += 1  # Contamos un valor procesado

                            if numero == -999:
                                total_faltantes += 1  # Contamos el valor faltante
                            elif numero >= 0:
                                continue
                            else:
                                caracteres_no_deseados.append(columna)
                        except ValueError:
                            # Si no es un número válido, añadir a los caracteres no deseados
                            caracteres_no_deseados.append(columna)

                    # Si se encontraron caracteres no deseados, escribir en el log
                    if caracteres_no_deseados:
                        log.write(f"Archivo: {archivo}\n")
                        log.write(f"Línea {i}\n")  # Número de línea real
                        log.write(f"Caracteres no deseados: {caracteres_no_deseados}\n\n")

                # Verificar que cada año tenga exactamente 12 meses (solo para años dentro del rango válido)
                for anio, meses in meses_por_anio.items():
                    if anio_minimo <= anio <= anio_maximo and meses != 12:
                        log.write(f"ERROR: El año {anio} en el archivo {archivo} no tiene 12 meses, tiene {meses} meses\n\n")

                total_lineas += lineas_archivo  # Contamos las líneas procesadas en este archivo

# Calcular porcentaje de valores faltantes
if total_valores > 0:
    porcentaje_faltantes = (total_faltantes / total_valores) * 100
else:
    porcentaje_faltantes = 0

# Escribir los resúmenes en el log de resultados
with open(archivo_log, 'a', encoding='utf-8') as log:
    log.write("Resumen Final:\n")
    log.write(f"Total de archivos procesados: {total_archivos}\n")
    log.write(f"Total de líneas procesadas: {total_lineas}\n")
    log.write(f"Total de valores procesados (excluyendo -999): {total_valores}\n")
    log.write(f"Total de valores faltantes (-999): {total_faltantes}\n")
    log.write(f"Porcentaje de valores faltantes sobre el total de valores: {porcentaje_faltantes:.2f}%\n\n")

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
with open(archivo_log, 'a', encoding='utf-8') as log:
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

# Crear archivo CSV con los resultados
archivo_csv = os.path.join(ruta_log, 'resultados.csv')
with open(archivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Escribir el encabezado
    writer.writerow(['Año', 'Total Precipitación (L/m²)', 'Media Anual (L/m² al Año)', 'Tasa de Variación (%)', 'Clasificación'])

    # Escribir los datos de cada año
    anio_anterior = None
    total_anterior = None

    for anio in sorted(datos_globales):
        total_anual = datos_globales[anio]['total']
        media_anual = medias_anuales_por_anio.get(anio, 0)

        # Calcular la tasa de variación sobre el total anual
        if anio_anterior is not None and total_anterior > 0:
            tasa_variacion = ((total_anual - total_anterior) / total_anterior) * 100
        else:
            tasa_variacion = None

        # Determinar la clasificación (Lluvioso o Seco)
        if media_anual > promedio_pasados:
            clasificacion = "Lluvioso"
        else:
            clasificacion = "Seco"

        # Escribir la fila en el CSV
        if tasa_variacion is not None:
            writer.writerow([anio, int(total_anual), f"{media_anual:.2f}", f"{tasa_variacion:.2f}", clasificacion])
        else:
            writer.writerow([anio, int(total_anual), f"{media_anual:.2f}", "N/A", clasificacion])

        # Actualizar valores del año anterior
        anio_anterior = anio
        total_anterior = total_anual

print(f"Resultados globales guardados en: {archivo_log}")
print(f"Resultados en formato CSV guardados en: {archivo_csv}")