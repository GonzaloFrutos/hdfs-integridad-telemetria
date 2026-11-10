import hashlib
import pandas as pd
import sys

def calcular_sha256(ruta_archivo):
    """Calcula la firma criptográfica SHA-256 de un archivo binario."""
    sha256 = hashlib.sha256()
    with open(ruta_archivo, 'rb') as f:
        for bloque in iter(lambda: f.read(65536), b''):
            sha256.update(bloque)
    return sha256.hexdigest()

def depurar_dataset(origen, destino):
    print(f"--- INICIANDO TRATAMIENTO DE DATOS EN: {origen} ---")
    
    # 1. Firma original
    hash_bruto = calcular_sha256(origen)
    print(f"SHA-256 Fichero Bruto: {hash_bruto}")
    
    # 2. Carga del conjunto de datos
    df = pd.read_csv(origen, encoding='utf-8')
    filas_iniciales = len(df)
    print(f"Registros iniciales: {filas_iniciales}")
    
    # 3. Limpieza y depuración lógicas
    # a. Eliminación de duplicados exactos
    df = df.drop_duplicates()
    
    # b. Gestión de nulos en campos críticos
    df = df.dropna(subset=['temp_celsius', 'peso_kg', 'destino'])
    
    # c. Filtrado de inconsistencias y valores fuera de rango
    df = df[df['peso_kg'] > 0]                                 # Elimina pesos negativos (-45.50 kg)
    df = df[(df['temp_celsius'] >= -30) & (df['temp_celsius'] <= 50)] # Elimina temperaturas absurdas (98.4 °C)
    df = df[df['estado_envio'] != 'DESCONOCIDO_ERROR']         # Elimina estados no catalogados
    
    # 4. Guardado del fichero saneado
    df.to_csv(destino, index=False, encoding='utf-8')
    filas_finales = len(df)
    print(f"Registros saneados:  {filas_finales}")
    print(f"Registros eliminados: {filas_iniciales - filas_finales}")
    
    # 5. Firma resultante
    hash_limpio = calcular_sha256(destino)
    print(f"SHA-256 Fichero Saneado: {hash_limpio}")
    print("--- TRATAMIENTO FINALIZADO CON ÉXITO ---")

if __name__ == "__main__":
    archivo_origen = "telemetria_envios - telemetria_envios.csv"
    archivo_destino = "telemetria_limpia.csv"
    
    try:
        depurar_dataset(archivo_origen, archivo_destino)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_origen}'. Revisa la ruta.")
        sys.exit(1)