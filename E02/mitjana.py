import os

# Función para leer los datos de un archivo .dat
def leer_datos_archivo(archivo):
    datos = []
    with open(archivo, 'r') as f:
        # Saltar las dos primeras líneas de cabecera
        f.readline()
        f.readline()
        
        for linea in f:
            # Convertir la línea en una lista de valores
            partes = linea.split()
            identificador = partes[0]  # Mantener el identificador como cadena
            anio = int(partes[1])
            mes = int(partes[2])
            precipitaciones = list(map(float, partes[3:]))  # Convertir los datos de precipitación a flotantes
            datos.append((identificador, anio, mes, precipitaciones))
    return datos

# Función para calcular la media anual de precipitaciones por pluviómetro
def calcular_media_anual(datos):
    medias = {}  # Diccionario para almacenar las medias anuales por pluviómetro
    for identificador, anio, mes, precipitaciones in datos:
        # Filtrar las precipitaciones válidas (no -999)
        precipitaciones_validas = [p for p in precipitaciones if p != -999]
        
        if not precipitaciones_validas:  # Si no hay precipitaciones válidas, no lo consideramos
            continue
        
        suma_precipitaciones = sum(precipitaciones_validas)
        
        # Acumular la suma de precipitaciones para este pluviómetro y año
        if (identificador, anio) not in medias:
            medias[(identificador, anio)] = {'suma': 0, 'contador': 0}
        
        medias[(identificador, anio)]['suma'] += suma_precipitaciones
        medias[(identificador, anio)]['contador'] += 1
    
    # Calcular la media anual final por pluviómetro
    medias_anuales = {}
    for (identificador, anio), datos_pluviometro in medias.items():
        if datos_pluviometro['contador'] > 0:
            media_anual = datos_pluviometro['suma'] / 12  # Dividir la suma de precipitaciones entre 12 meses
            medias_anuales[(identificador, anio)] = media_anual
    
    return medias_anuales

# Función para calcular la suma de medias anuales para un año específico
def calcular_suma_medias_anuales_por_anio(medias_anuales, anio):
    suma_total = 0
    for (identificador, anio_dato), media_anual in medias_anuales.items():
        if anio_dato == anio:
            suma_total += media_anual
    return suma_total

# Función principal para procesar los archivos .dat
def procesar_archivos(directorio):
    archivos = [f for f in os.listdir(directorio) if f.endswith('.dat')]
    medias_anuales_totales = {}  # Diccionario para acumular las medias anuales de todos los archivos

    # Leer y procesar cada archivo .dat
    for archivo in archivos:
        print(f"Procesando archivo: {archivo}")
        datos = leer_datos_archivo(os.path.join(directorio, archivo))
        medias_anuales = calcular_media_anual(datos)
        
        # Acumular las medias anuales directamente, no como listas
        for clave, media in medias_anuales.items():
            if clave not in medias_anuales_totales:
                medias_anuales_totales[clave] = 0  # Inicializar la suma con 0
            medias_anuales_totales[clave] += media  # Acumular la media anual
    
    # Mostrar solo la media y el año correspondiente
    for anio in range(2006, 2101):  # Años entre 2006 y 2100
        suma_medias = calcular_suma_medias_anuales_por_anio(medias_anuales_totales, anio)
        
        # Dividir entre el número de pluviómetros y mostrar el resultado
        num_pluviometros = len([clave for clave in medias_anuales_totales if clave[1] == anio])
        if num_pluviometros > 0:
            resultado = suma_medias / num_pluviometros  # Dividir por el número de pluviómetros
            print(f"Año {anio}: Media anual de precipitación: {resultado:.2f} mm")
        else:
            print(f"No hay datos suficientes para calcular la media anual de precipitación para el año {anio}")

# Directorio donde están los archivos .dat
directorio_archivos = 'E01/precip.MIROC5.RCP60.2006-2100.SDSM_REJ'  # Cambia esto a la ruta correcta
procesar_archivos(directorio_archivos)
