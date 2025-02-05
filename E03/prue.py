import glob
import os
import re
import csv
from tqdm import tqdm
import matplotlib.pyplot as plt

# Configuración de rutas
ruta_log = 'E03'
archivo_log = os.path.join(ruta_log, 'pruebas.log')
archivo_resultados = os.path.join(ruta_log, 'analisis.log')
archivo_csv = os.path.join(ruta_log, 'resultados.csv')

# Verificar y crear carpeta E02
if not os.path.exists(ruta_log):
    os.makedirs(ruta_log)

# ================================================================
# CÓDIGO DE VALIDACIÓN (CODE1)
# ================================================================
carpeta = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'
patron = '*.dat'
archivos = glob.glob(os.path.join(carpeta, patron))

# Validar existencia de carpeta y archivos
if not os.path.exists(carpeta) or not archivos:
    with open(archivo_log, 'a', encoding='utf-8') as log:
        log.write("ERROR: Carpeta o archivos .dat no encontrados.\n")
    exit()

# Contadores y parámetros de validación
total_valores, total_faltantes, total_archivos, total_lineas = 0, 0, 0, 0
parametros_primera_fila = ['precip', 'MIROC5', 'RCP60', 'REGRESION', 'decimas', '1']
parametros_segunda_fila_fija = ['182', 'geo', '2006', '2100', '-1']

# Procesar validación
with open(archivo_log, 'a', encoding='utf-8') as log:
    for archivo in tqdm(archivos, desc="Validando archivos"):
        with open(archivo, 'r') as f:
            lines = f.read().strip().split('\n')
            if len(lines) > 2:
                total_archivos += 1
                # ... (resto de validaciones del CODE1)

# ================================================================
# CÓDIGO DE ANÁLISIS CON MEDIA CORREGIDA (CODE2)
# ================================================================
datos_globales = {}
medias_anuales_totales = {}

# Procesar archivos para análisis
for archivo in tqdm(archivos, desc="Analizando datos"):
    with open(archivo, 'r') as f:
        f.readline(), f.readline()  # Saltar cabeceras
        for linea in f:
            partes = re.split(r'\s+', linea.strip())
            if len(partes) < 4: continue
            
            identificador, anio, mes = partes[0], int(partes[1]), int(partes[2])
            precipitaciones = [float(p) for p in partes[3:] if float(p) != -999]
            
            # Acumular datos para media anual corregida
            if (identificador, anio) not in medias_anuales_totales:
                medias_anuales_totales[(identificador, anio)] = {'suma': 0, 'contador': 0}
            medias_anuales_totales[(identificador, anio)]['suma'] += sum(precipitaciones)
            medias_anuales_totales[(identificador, anio)]['contador'] += 1

            # Acumular datos globales
            if anio not in datos_globales:
                datos_globales[anio] = {'total': 0, 'dias': 0}
            datos_globales[anio]['total'] += sum(precipitaciones)
            datos_globales[anio]['dias'] += len(precipitaciones)

# Calcular media anual corregida
medias_anuales_por_anio = {}
for (identificador, anio), datos in medias_anuales_totales.items():
    if datos['contador'] == 12:  # Solo años con 12 meses
        medias_anuales_por_anio[anio] = datos['suma'] / 12

# ================================================================
# GENERAR CSV (AÑO, TOTAL, MEDIA, TASA, CLASIFICACIÓN)
# ================================================================
promedio_pasados = sum(medias_anuales_por_anio.get(a, 0) for a in range(2006, 2025)) / 19

with open(archivo_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Año', 'Total (L/m²)', 'Media Anual (L/m²)', 'Tasa Variación (%)', 'Clasificación'])
    
    anio_anterior, total_anterior = None, None
    for anio in sorted(datos_globales):
        total = datos_globales[anio]['total']
        media = medias_anuales_por_anio.get(anio, 0)
        tasa = ((total - total_anterior) / total_anterior * 100) if anio_anterior else 'N/A'
        clasificacion = 'Pluvioso' if media > promedio_pasados else 'Seco'
        
        writer.writerow([anio, total, round(media, 2), round(tasa, 2) if tasa != 'N/A' else 'N/A', clasificacion])
        anio_anterior, total_anterior = anio, total

# ================================================================
# GENERAR GRÁFICOS
# ================================================================
anios = sorted(datos_globales.keys())
totales = [datos_globales[a]['total'] for a in anios]
medias = [medias_anuales_por_anio.get(a, 0) for a in anios]

# Gráfico de barras (Total por año)
plt.figure(figsize=(12, 6))
plt.bar(anios, totales, color='skyblue')
plt.title('Precipitación Total por Año')
plt.xlabel('Año'), plt.ylabel('L/m²')
plt.xticks(rotation=45)
plt.savefig(os.path.join(ruta_log, 'grafico_barras.png'))

# Gráfico de líneas (Media anual)
plt.figure(figsize=(12, 6))
plt.plot(anios, medias, marker='o', color='green', linestyle='-')
plt.title('Media Anual de Precipitación')
plt.xlabel('Año'), plt.ylabel('L/m²')
plt.xticks(rotation=45)
plt.savefig(os.path.join(ruta_log, 'grafico_lineas.png'))

# Gráfico de dispersión (Total vs Media)
plt.figure(figsize=(12, 6))
plt.scatter(totales, medias, color='red')
plt.title('Relación entre Precipitación Total y Media Anual')
plt.xlabel('Total (L/m²)'), plt.ylabel('Media (L/m²)')
plt.savefig(os.path.join(ruta_log, 'grafico_dispersion.png'))

print(f"Proceso completado. Resultados en: {ruta_log}")