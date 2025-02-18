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
carpeta = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'

# Crear un archivo de log para guardar los errores (modo 'a' para no sobrescribir)
archivo_log = os.path.join(ruta_log, 'pruebas.log')

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