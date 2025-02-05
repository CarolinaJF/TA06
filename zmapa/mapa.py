import os
import csv

# Directorio que contiene los archivos .dat
directorio = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'

# Archivo CSV de salida
archivo_csv = 'zmapa/coordenadas.csv'

# Lista para almacenar las coordenadas
coordenadas = []

# Recorre todos los archivos .dat en el directorio
for nombre_archivo in os.listdir(directorio):
    if nombre_archivo.endswith('.dat'):
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        
        # Abre el archivo .dat y lee la segunda línea
        with open(ruta_archivo, 'r') as archivo:
            lineas = archivo.readlines()
            if len(lineas) > 1:
                segunda_linea = lineas[1].strip().split()
                
                # Asegúrate de que la segunda línea tenga al menos 3 datos
                if len(segunda_linea) >= 3:
                    latitud = segunda_linea[1]
                    longitud = segunda_linea[2]
                    coordenadas.append([latitud, longitud])

# Escribe las coordenadas en el archivo CSV
with open(archivo_csv, 'w', newline='') as archivo_csv_salida:
    escritor_csv = csv.writer(archivo_csv_salida)
    escritor_csv.writerow(['Latitud', 'Longitud'])  # Escribe el encabezado
    escritor_csv.writerows(coordenadas)  # Escribe las coordenadas

print(f"Se han guardado {len(coordenadas)} coordenadas en {archivo_csv}")