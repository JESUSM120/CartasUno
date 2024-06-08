import os
import pandas as pd

# Directorio de imágenes de referencia del juego Uno
directorio_referencia = "C:\\Users\\Jesus\\Pictures\\UnoV1"

# Listas para almacenar los nombres de las imágenes y las descripciones
nombres_imagenes = []
descripciones = []

# Recorrer el directorio y obtener los nombres de las imágenes
for archivo in os.listdir(directorio_referencia):
    if archivo.endswith(".jpg") or archivo.endswith(".png"):
        nombre, extension = os.path.splitext(archivo)
        nombres_imagenes.append(nombre)
        descripciones.append("")  # Inicialmente vacío, para que puedas llenarlas después

# Crear un DataFrame con los nombres de las imágenes y las descripciones
df = pd.DataFrame({
    "Nombre de la Imagen": nombres_imagenes,
    "Descripción": descripciones
})

# Guardar el DataFrame en un archivo Excel
archivo_excel = "imagenes_descripciones.xlsx"
df.to_excel(archivo_excel, index=False)

print(f"Archivo Excel '{archivo_excel}' creado con éxito.")
