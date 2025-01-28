import glob
import os
import re  # Para usar expresiones regulares
from tqdm import tqdm  # Importamos tqdm para la barra de progreso
import time   
import datetime

# Ruta personalizada para los archivos de log (puedes cambiar esta ruta)
ruta_log = 'E04/dades'  # Cambia esto por la ruta deseada, por ejemplo: 'C:/mis_logs' o '/home/usuario/logs'
archivo_resultados = 'E04/dades/datos.log'

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
archivo_log = os.path.join(ruta_log, 'datos.log')


# Inicializamos contadores globales
total_valores = 0
total_faltantes = 0
total_archivos = 0
total_lineas = 0

# Parámetros esperados para la primera fila
parametros_primera_fila = ['precip', 'MIROC5', 'RCP60', 'REGRESION', 'decimas', '1']

# Parámetros esperados para la segunda fila (columnas fijas)
parametros_segunda_fila_fija = ['182', 'geo', '2006', '2100', '-1']

# Inicializamos la barra de progreso con tqdm
with open(archivo_log, 'a') as log:
    # Usamos tqdm para la barra de progreso en los archivos
    for archivo in tqdm(archivos, desc="Validando archivos", unit="archivo"):
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
                            pass  # Comentado ya que no se necesita el manejo del año ahora

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

                total_lineas += lineas_archivo  # Contamos las líneas procesadas en este archivo

# Calcular porcentaje de valores faltantes
if total_valores > 0:
    porcentaje_faltantes = (total_faltantes / total_valores) * 100
else:
    porcentaje_faltantes = 0

# Escribir los resúmenes en el log de resultados
with open(archivo_log, 'a') as log:
    log.write(f"Fecha de entrada: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write("Resumen Final:\n")
    log.write(f"Total de archivos procesados: {total_archivos}\n")
    log.write(f"Total de líneas procesadas: {total_lineas}\n")
    log.write(f"Total de valores procesados (excluyendo -999): {total_valores}\n")
    log.write(f"Total de valores faltantes (-999): {total_faltantes}\n")
    log.write(f"Porcentaje de valores faltantes sobre el total de valores: {porcentaje_faltantes:.2f}%\n\n")


print("Validación exitosa. Resultados guardados en:", archivo_log)
time.sleep(3)
os.system('clear')
print("Iniciando procesamiento de datos...")
time.sleep(2)
os.system('clear')

import time    
import glob
import os
import os
import re  # Para usar expresiones regulares
from tqdm import tqdm  # Importamos tqdm para la barra de progreso


# Verificar si la ruta existe, si no, crearla
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)


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
time.sleep(5)
os.system('clear')

import csv
import matplotlib.pyplot as plt
import seaborn as sns

# Supongamos que 'datos_globales' contiene todos los datos ya procesados
archivo_csv = 'E04/dades/resultados_generales.csv'

# Calculamos el total de precipitación de todos los años para obtener el promedio
total_precip = sum(datos['total'] for datos in datos_globales.values())
num_anos = len(datos_globales)
promedio_precip = total_precip / num_anos if num_anos > 0 else 0

# Variables para identificar los años más y menos pluviosos
max_precipitacion = -float('inf')
min_precipitacion = float('inf')
anio_max = None
anio_min = None

# Datos para gráficos
anos = []
total_precipitaciones = []
clasificaciones = []

# Abre el archivo CSV en modo escritura
with open(archivo_csv, 'w', newline='') as csvfile:
    fieldnames = ['Año', 'Total Precipitación (L/m²)', 'Media Anual (L/m² al Año)', 'Tasa de Variación (%)', 'Clasificación']
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Escribe el encabezado en el archivo CSV
    writer.writeheader()
    
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
        
        # Clasificar el año según su precipitación
        if total_anual > promedio_precip:
            clasificacion = "Pluvioso"
        elif total_anual < promedio_precip:
            clasificacion = "Seco"
        else:
            clasificacion = "Normal"
        
        # Actualizar los años más y menos pluviosos
        if total_anual > max_precipitacion:
            max_precipitacion = total_anual
            anio_max = anio
        
        if total_anual < min_precipitacion:
            min_precipitacion = total_anual
            anio_min = anio

        # Añadir datos para los gráficos
        anos.append(anio)
        total_precipitaciones.append(total_anual)
        clasificaciones.append(clasificacion)

        # Crear un diccionario con los resultados
        if tasa_variacion is not None:
            row = {
                'Año': anio,
                'Total Precipitación (L/m²)': int(total_anual),
                'Media Anual (L/m² al Año)': round(media_anual, 2),
                'Tasa de Variación (%)': round(tasa_variacion, 2),
                'Clasificación': clasificacion
            }
        else:
            row = {
                'Año': anio,
                'Total Precipitación (L/m²)': int(total_anual),
                'Media Anual (L/m² al Año)': round(media_anual, 2),
                'Tasa de Variación (%)': 'N/A',
                'Clasificación': clasificacion
            }

        # Escribir la fila en el archivo CSV
        writer.writerow(row)

        # Actualizar valores del año anterior
        anio_anterior = anio
        total_anterior = total_anual

# Añadir los años más y menos pluviosos al final del archivo CSV
with open(archivo_csv, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Escribir una fila adicional con los resultados de los años más y menos pluviosos
    writer.writerow([])
    writer.writerow(["Año Más Pluvioso", anio_max, "Total Precipitación (L/m²)", max_precipitacion])
    writer.writerow(["Año Menos Pluvioso", anio_min, "Total Precipitación (L/m²)", min_precipitacion])

print(f"Resultados globales exportados a: {archivo_csv}")

# Mostrar estadísticas visuales

import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import datetime

# Suprimir advertencias de FutureWarning (opcional, si necesitas mantener limpio el entorno)
warnings.simplefilter(action='ignore', category=FutureWarning)

# Gráfico de barras: Precipitación total por año
plt.figure(figsize=(10,6))
sns.barplot(x=anos, y=total_precipitaciones, hue=anos, palette="viridis", dodge=False)  # Usamos `hue=anos` y `dodge=False` para mantener el formato esperado
plt.title("Precipitación Total por Año")
plt.xlabel("Año")
plt.ylabel("Precipitación Total (L/m²)")
plt.xticks(rotation=45)
plt.legend([], [], frameon=False)  # Eliminamos la leyenda si no es necesaria
plt.tight_layout()
plt.show()

# Gráfico de líneas: Tasa de variación de la precipitación
tasa_variacion = [None if x == 0 else (total_precipitaciones[i] - total_precipitaciones[i-1]) / total_precipitaciones[i-1] * 100 for i, x in enumerate(total_precipitaciones)]
plt.figure(figsize=(10,6))
sns.lineplot(x=anos[1:], y=tasa_variacion[1:], marker="o", color="blue")
plt.title("Tasa de Variación de la Precipitación entre Años")
plt.xlabel("Año")
plt.ylabel("Tasa de Variación (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gráfico de dispersión: Relación entre precipitación total y clasificación
plt.figure(figsize=(10,6))
sns.scatterplot(x=anos, y=total_precipitaciones, hue=clasificaciones, palette="coolwarm", s=100)
plt.title("Relación entre Precipitación Total y Clasificación")
plt.xlabel("Año")
plt.ylabel("Precipitación Total (L/m²)")
plt.legend(title="Clasificación")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
