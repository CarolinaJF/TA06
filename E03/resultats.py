import glob
import os
import re
from tqdm import tqdm

# Configuración de rutas
ruta_log = 'E04/dades'
archivo_resultados = os.path.join(ruta_log, 'pruebas.log')
carpeta = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'
patron = '*.dat'

# Crear directorios si no existen
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# Obtener lista de archivos
archivos = glob.glob(os.path.join(carpeta, patron))

# Parámetros para validaciones
parametros_primera_fila = ['precip', 'MIROC5', 'RCP60', 'REGRESION', 'decimas', '1']
parametros_segunda_fila_fija = ['182', 'geo', '2006', '2100', '-1']

# Variables para análisis global
datos_globales = {}
dia_mas_lluvioso_pasado = {'anio': None, 'dia': None, 'precipitacion': float('-inf')}
dia_menos_lluvioso_pasado = {'anio': None, 'dia': None, 'precipitacion': float('inf')}
dia_mas_lluvioso_futuro = {'anio': None, 'dia': None, 'precipitacion': float('-inf')}
dia_menos_lluvioso_futuro = {'anio': None, 'dia': None, 'precipitacion': float('inf')}
total_valores = total_faltantes = total_archivos = total_lineas = 0

# Procesamiento de archivos
with open(archivo_resultados, 'a') as log:
    for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
        with open(archivo, 'r') as f:
            contenido = f.read().strip()
            lines = contenido.split('\n')

            if len(lines) < 3:
                log.write(f"ERROR: Archivo {archivo} tiene menos de 3 líneas\n")
                continue

            # Validación de encabezados
            primera_fila = lines[0].strip().split()
            if primera_fila != parametros_primera_fila:
                log.write(f"ERROR: Encabezado incorrecto en {archivo}. Esperado: {parametros_primera_fila}, encontrado: {primera_fila}\n")
                continue

            segunda_linea = lines[1].strip().split()
            if len(segunda_linea) >= 4:
                id_pluviometro = segunda_linea[0]
                columnas_fijas = segunda_linea[3:]
                if columnas_fijas != parametros_segunda_fila_fija:
                    log.write(f"ERROR: Parámetros incorrectos en {archivo}, línea 2. Esperado: {parametros_segunda_fila_fija}, encontrado: {columnas_fijas}\n")
            else:
                log.write(f"ERROR: Segunda línea en {archivo} tiene menos de 4 columnas\n")
                continue

            # Procesar datos desde la tercera línea
            total_archivos += 1
            for i, linea in enumerate(lines[2:], start=3):
                total_lineas += 1
                if not linea.strip():
                    log.write(f"ERROR: Línea vacía en {archivo}, línea {i}\n")
                    continue

                columnas = re.split(r'\s+', linea.strip())
                if len(columnas) < 4:
                    log.write(f"ERROR: Línea incompleta en {archivo}, línea {i}\n")
                    continue

                if columnas[0] != id_pluviometro:
                    log.write(f"ERROR: ID de pluviómetro incorrecto en {archivo}, línea {i}\n")
                    continue

                try:
                    anio = int(columnas[1])
                    datos_dia = list(map(float, columnas[3:]))
                    if anio not in datos_globales:
                        datos_globales[anio] = {'total': 0, 'dias': 0}

                    datos_globales[anio]['total'] += sum(d for d in datos_dia if d != -999)
                    datos_globales[anio]['dias'] += sum(1 for d in datos_dia if d != -999)

                    for idx, precipitacion in enumerate(datos_dia):
                        if precipitacion != -999:
                            total_valores += 1
                            if precipitacion > dia_mas_lluvioso_pasado['precipitacion'] and 2006 <= anio <= 2024:
                                dia_mas_lluvioso_pasado = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                            if precipitacion < dia_menos_lluvioso_pasado['precipitacion'] and 2006 <= anio <= 2024:
                                dia_menos_lluvioso_pasado = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                            if precipitacion > dia_mas_lluvioso_futuro['precipitacion'] and 2025 <= anio <= 2100:
                                dia_mas_lluvioso_futuro = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                            if precipitacion < dia_menos_lluvioso_futuro['precipitacion'] and 2025 <= anio <= 2100:
                                dia_menos_lluvioso_futuro = {'anio': anio, 'dia': idx + 1, 'precipitacion': precipitacion}
                        elif precipitacion == -999:
                            total_faltantes += 1

                except ValueError:
                    log.write(f"ERROR: Formato inválido en {archivo}, línea {i}\n")

    # Generar reporte final
    datos_pasados = {k: v for k, v in datos_globales.items() if 2006 <= k <= 2024}
    datos_futuros = {k: v for k, v in datos_globales.items() if 2025 <= k <= 2100}
    promedio_pasados = sum(d['total'] for d in datos_pasados.values()) / len(datos_pasados) if datos_pasados else 0
    promedio_futuros = sum(d['total'] for d in datos_futuros.values()) / len(datos_futuros) if datos_futuros else 0

    log.write(f"Resumen:\nTotal archivos procesados: {total_archivos}\nTotal líneas procesadas: {total_lineas}\n")
    log.write(f"Día más lluvioso pasado: {dia_mas_lluvioso_pasado}\nDía menos lluvioso pasado: {dia_menos_lluvioso_pasado}\n")
    log.write(f"Día más lluvioso futuro: {dia_mas_lluvioso_futuro}\nDía menos lluvioso futuro: {dia_menos_lluvioso_futuro}\n")
    log.write(f"Promedio precipitación años pasados: {promedio_pasados:.2f}\nPromedio precipitación años futuros: {promedio_futuros:.2f}\n")
