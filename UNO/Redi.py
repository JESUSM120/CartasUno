import os
import cv2

def resize_images_in_folder(folder_path, width=300, height=500):
    # Lista todos los archivos en la carpeta
    file_list = os.listdir(folder_path)
    
    for file_name in file_list:
        # Crear la ruta completa al archivo
        file_path = os.path.join(folder_path, file_name)
        
        # Verificar si es un archivo de imagen
        if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Leer la imagen
            image = cv2.imread(file_path)
            
            # Redimensionar la imagen
            resized_image = cv2.resize(image, (width, height))
            
            # Guardar la imagen redimensionada, reemplazando la original
            cv2.imwrite(file_path, resized_image)
            print(f"Imagen {file_name} redimensionada y guardada.")
        else:
            print(f"{file_name} no es una imagen o no es un archivo válido.")

# Ruta a la carpeta con las imágenes
folder_path = r'/home/jesusmc/Imágenes/Uno'
# Llamar a la función para redimensionar las imágenes
resize_images_in_folder(folder_path)
