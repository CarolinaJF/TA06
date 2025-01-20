import glob
import os
import re  # Para usar expresiones regulares
from tqdm import tqdm  # Importamos tqdm para la barra de progreso

# Ruta de la carpeta que contiene los archivos .dat
carpeta = 'E01/ayuda1'

# Patrón para buscar archivos .dat
patron = '*.dat'

# Obtener la lista de archivos .dat en la carpeta
archivos = glob.glob(os.path.join(carpeta, patron))

# Crear un archivo de log para guardar los errores (modo 'a' para no sobrescribir)
archivo_log = 'error.log'

# Inicializamos contadores globales
total_valores = 0
total_faltantes = 0
total_archivos = 0
total_lineas = 0

# Inicializamos la barra de progreso con tqdm
with open(archivo_log, 'a') as log:
    # Usamos tqdm para la barra de progreso en los archivos
    for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
        with open(archivo, 'r') as f:
            contenido = f.read()
        
            # Dividir el contenido en líneas, eliminando líneas vacías al final del archivo
            lines = contenido.strip().split('\n')

            # Verificar que haya suficientes líneas para evitar errores de índice
            if len(lines) > 2:  # Ignorar las dos primeras filas
                total_archivos += 1  # Contamos el archivo procesado
                lineas_archivo = 0  # Contador de líneas procesadas en este archivo

                # Variables para controlar el mes de cada año
                meses_por_ano = {}  # Diccionario para llevar el conteo de meses por cada año
                year = None  # Año actual procesado

                # Verificar si hay líneas vacías entre las filas (esto incluye líneas que solo contienen espacios)
                for i, linea in enumerate(lines[2:]):  # Empezamos desde la tercera línea
                    lineas_archivo += 1
                    if not linea.strip():  # Si la línea está vacía o solo contiene espacios en blanco
                        log.write(f"ERROR: Línea vacía detectada en el archivo {archivo}, línea {i+3}\n")  # Línea i+3 porque empezamos desde la tercera línea

                    # Obtener las columnas de la línea actual
                    columnas = linea.split()  # Suponemos que se usa el espacio como delimitador

                    # Verificar que la cantidad de valores en la fila no supere 34
                    if len(columnas) > 34:
                        log.write(f"ERROR: Más de 34 valores en la fila del archivo {archivo}, línea {i+3}, valores: {len(columnas)}\n")

                    # Verificar el formato de la primera columna (PX donde X es un número)
                    primera_columna = columnas[0]  # La primera columna no debe ser ignorada
                    if not re.match(r'P\d+', primera_columna):  # Comprobar que la primera columna siga el formato 'P' seguido de un número
                        log.write(f"ERROR: Formato incorrecto en la primera columna del archivo {archivo}, columna: {primera_columna}, línea {i+3}\n")
                        print(f"ERROR: Formato incorrecto en la primera columna en el archivo {archivo}, línea {i+3}, columna: {primera_columna}")

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

                    # Verificación de la columna 3 (mes)
                    columna_mes = columnas[2] if len(columnas) > 2 else None  # La columna 3 (índice 2)
                    
                    if columna_mes:
                        try:
                            mes = int(columna_mes)
                            if mes < 1 or mes > 12:
                                log.write(f"ERROR: El valor de la columna 3 no es un mes válido (1-12) en el archivo {archivo}, línea {i+3}, valor: {columna_mes}\n")
                            else:
                                # Comprobamos que el mes sigue el patrón secuencial dentro de un año
                                if year not in meses_por_ano:
                                    meses_por_ano[year] = 0  # Inicializamos el contador de meses para este año
                                
                                # Comprobamos que el mes sea el siguiente en el patrón
                                if mes != meses_por_ano[year] + 1:
                                    log.write(f"ERROR: El mes de la columna 3 no sigue el patrón de meses en el archivo {archivo}, línea {i+3}, valor: {columna_mes}, año: {year}\n")
                                
                                # Incrementamos el mes procesado para este año
                                meses_por_ano[year] += 1
                                if meses_por_ano[year] == 12:  # Si ya procesamos 12 meses, pasamos al siguiente año
                                    year += 1
                        except ValueError:
                            log.write(f"ERROR: La columna 3 no tiene un valor numérico en el archivo {archivo}, línea {i+3}, valor: {columna_mes}\n")

                    # Si se encontraron caracteres no deseados, escribir en el log
                    if caracteres_no_deseados:
                        log.write(f"Archivo: {archivo}\n")
                        log.write(f"Línea {i+3}\n")  # Número de línea real
                        log.write(f"Columnas: {columnas}\n")
                        log.write(f"Caracteres no deseados: {caracteres_no_deseados}\n")
                        log.write('\n')

                total_lineas += lineas_archivo  # Contamos las líneas procesadas en este archivo

# Calcular porcentaje de valores faltantes
if total_valores > 0:
    porcentaje_faltantes = (total_faltantes / total_valores) * 100
else:
    porcentaje_faltantes = 0

# Escribir los resúmenes en el log
with open(archivo_log, 'a') as log:
    log.write("\nResumen Final:\n")
    log.write(f"Total de archivos procesados: {total_archivos}\n")
    log.write(f"Total de líneas procesadas: {total_lineas}\n")
    log.write(f"Total de valores procesados (excluyendo -999): {total_valores}\n")
    log.write(f"Total de valores faltantes (-999): {total_faltantes}\n")
    log.write(f"Porcentaje de valores faltantes sobre el total de valores: {porcentaje_faltantes:.2f}%\n")
    log.write('\n')

# Imprimir en consola el resumen final
print("\nResumen Final:")
print(f"Total de archivos procesados: {total_archivos}")
print(f"Total de líneas procesadas: {total_lineas}")
print(f"Total de valores procesados (excluyendo -999): {total_valores}")
print(f"Total de valores faltantes (-999): {total_faltantes}")
print(f"Porcentaje de valores faltantes sobre el total de valores: {porcentaje_faltantes:.2f}%")


