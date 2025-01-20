import os
import pandas as pd
import logging
from tqdm import tqdm  # Para mostrar la barra de carga

# Configuración de logging
logging.basicConfig(
    filename='log_análisis_meteorología.log', 
    level=logging.WARNING,  # Reducir el nivel de logging para que solo muestre advertencias o errores
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def leer_archivo(filepath):
    """
    Lee un archivo meteorológico y realiza comprobaciones básicas.
    """
    try:
        # Leer el archivo con separador de espacios múltiples
        data = pd.read_csv(filepath, sep=r'\s+', skiprows=2, header=None)

        # Agregar nombres de columnas basados en el formato proporcionado
        num_dias = 31  # Número máximo de días en un mes
        columnas = ['ID', 'Año', 'Mes'] + [f'Día_{i}' for i in range(1, num_dias + 1)]
        data.columns = columnas

        return data
    except Exception as e:
        logging.error(f"Error al leer el archivo '{filepath}': {e}")
        raise

def verificar_datos(data, filepath):
    """
    Verifica la consistencia de los datos en un archivo.
    """
    try:
        # Verificar tipos de datos
        assert data['Año'].dtype == int, "La columna 'Año' no es entera."
        assert data['Mes'].dtype == int, "La columna 'Mes' no es entera."

        # Verificar valores faltantes (-999)
        valores_faltantes = (data == -999).sum().sum()
        total_valores = data.size
        porcentaje_faltantes = (valores_faltantes / total_valores) * 100

        return porcentaje_faltantes
    except AssertionError as e:
        logging.error(f"Error en la verificación de datos en '{filepath}': {e}")
        raise
    except Exception as e:
        logging.error(f"Error inesperado durante la verificación de datos en '{filepath}': {e}")
        raise

def procesar_carpeta(folderpath):
    """
    Procesa todos los archivos en una carpeta.
    """
    try:
        # Lista de todos los archivos en la carpeta
        archivos = [os.path.join(folderpath, f) for f in os.listdir(folderpath) if f.endswith('.dat')]
        
        if not archivos:
            logging.warning("No se encontraron archivos .dat en la carpeta.")
            return pd.DataFrame(), 0

        # DataFrame combinado
        datos_combinados = pd.DataFrame()
        delimitadores_totales = 0

        # Barra de progreso utilizando tqdm
        for archivo in tqdm(archivos, desc="Procesando archivos", unit="archivo"):
            try:
                # Leer y verificar cada archivo
                datos = leer_archivo(archivo)
                verificar_datos(datos, archivo)

                # Contar delimitadores (espacios) en el archivo
                with open(archivo, 'r') as f:
                    for line in f:
                        delimitadores_totales += line.count(' ')

                # Combinar datos
                datos_combinados = pd.concat([datos_combinados, datos], ignore_index=True)
            except Exception as e:
                logging.error(f"Error procesando el archivo '{archivo}': {e}")

        return datos_combinados, delimitadores_totales
    except Exception as e:
        logging.error(f"Error al procesar la carpeta '{folderpath}': {e}")
        raise

def calcular_estadisticas(datos_combinados):
    """
    Calcula estadísticas como cantidad de datos por año y mes, número de columnas y delimitadores.
    """
    try:
        # Crear una columna 'Año-Mes' para agrupar
        datos_combinados['Año-Mes'] = datos_combinados['Año'].astype(str) + '-' + datos_combinados['Mes'].astype(str).str.zfill(2)

        # Calcular cantidad de datos por 'Año-Mes'
        datos_por_año_mes = datos_combinados.groupby('Año-Mes').size()

        # Número de columnas
        num_columnas = len(datos_combinados.columns)

        return datos_por_año_mes, num_columnas
    except Exception as e:
        logging.error(f"Error al calcular estadísticas: {e}")
        raise

def main():
    folderpath = 'E01/ayuda1'  # Ruta a la carpeta

    try:
        # PASO 1: Procesar carpeta
        datos_combinados, delimitadores_totales = procesar_carpeta(folderpath)

        if not datos_combinados.empty:
            # PASO 2: Calcular estadísticas
            datos_por_año_mes, num_columnas = calcular_estadisticas(datos_combinados)

            # Mostrar estadísticas de manera concisa
            print("### Estadísticas del análisis ###\n")

            print("Cantidad de datos por Año-Mes:")
            for año_mes, cantidad in datos_por_año_mes.items():
                print(f"{año_mes}: {cantidad} registros")

            print(f"\nNúmero total de columnas: {num_columnas}")
            print(f"Cantidad total de delimitadores (espacios) en los archivos: {delimitadores_totales}")
            
        else:
            print("No se procesaron datos.")

    except Exception as e:
        logging.critical(f"Se ha producido un error crítico en main: {e}")
        print(f"Se ha producido un error: {e}")

if __name__ == '__main__':
    main()
