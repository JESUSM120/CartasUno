import os

# Ruta de la carpeta que contiene las imágenes
carpeta = "/home/jesusmc/Imágenes/Uno"

# Recorre todos los archivos de la carpeta
for nombre_archivo in os.listdir(carpeta):
    # Verifica si el archivo es un archivo regular
    if os.path.isfile(os.path.join(carpeta, nombre_archivo)):
        # Divide el nombre del archivo en color y número
        partes = nombre_archivo.split("_")
        if len(partes) == 2:
            color, numero = partes
            # Reemplaza los espacios por guiones bajos en el nombre del archivo
            nuevo_nombre = f"{color}_{numero}"
            # Renombra el archivo
            os.rename(os.path.join(carpeta, nombre_archivo), os.path.join(carpeta, nuevo_nombre))
        else:
            print(f"El nombre de archivo '{nombre_archivo}' no está en el formato esperado.")
