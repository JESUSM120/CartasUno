import cv2
import os
import numpy as np
import pandas as pd

# Directorios de imágenes
directorio_cartas = "C:\\Users\\Jesus\\Pictures\\UnoV1"
directorio_comodines = "C:\\Users\\Jesus\\Pictures\\Comodines"

# Cargar imágenes de referencia del juego Uno desde una carpeta
imagenes_referencia = {}
for archivo in os.listdir(directorio_cartas):
    if archivo.endswith(".jpg") or archivo.endswith(".png"):
        nombre, extension = os.path.splitext(archivo)
        color, numero = nombre.split("_")
        imagen = cv2.imread(os.path.join(directorio_cartas, archivo))
        imagenes_referencia[(color, numero)] = imagen

# Cargar imágenes de comodines desde una carpeta
comodines_referencia = {}
for archivo in os.listdir(directorio_comodines):
    if archivo.endswith(".jpg") or archivo.endswith(".png"):
        nombre, extension = os.path.splitext(archivo)
        color, tipo = nombre.split("_")  # Asumimos que el nombre del archivo describe el color y tipo de comodín
        imagen = cv2.imread(os.path.join(directorio_comodines, archivo))
        comodines_referencia[(color, tipo)] = imagen

# Cargar descripciones desde el archivo Excel
archivo_excel = "C:\\Users\\Jesus\\Documents\\UNO\\imagenes_descripciones.xlsx"
df_descripciones = pd.read_excel(archivo_excel)
descripciones = {row["Nombre de la Imagen"]: row["Descripción"] for index, row in df_descripciones.iterrows()}

# Inicializar el detector ORB
orb = cv2.ORB_create()

# Función para calcular descriptores ORB
def calcular_descriptores(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    keypoints, descriptores = orb.detectAndCompute(gris, None)
    return keypoints, descriptores

# Calcular descriptores para las imágenes de referencia
descriptores_referencia = {}
for (color, numero), imagen in imagenes_referencia.items():
    keypoints, descriptores = calcular_descriptores(imagen)
    descriptores_referencia[(color, numero)] = descriptores

# Calcular descriptores para las imágenes de comodines
descriptores_comodines = {}
for (color, tipo), imagen in comodines_referencia.items():
    keypoints, descriptores = calcular_descriptores(imagen)
    descriptores_comodines[(color, tipo)] = descriptores

# Función para comparar una carta detectada con las imágenes de referencia
def comparar_con_referencia(imagen_detectada, comodines=False):
    mejor_coincidencia = None
    mejor_similitud = 0

    # Calcular descriptores para la imagen detectada
    _, descriptores_detectada = calcular_descriptores(imagen_detectada)
    
    if descriptores_detectada is None:
        return None
    
    # Seleccionar el conjunto de descriptores adecuado
    descriptores_a_usar = descriptores_comodines if comodines else descriptores_referencia
    
    # Comparar con cada conjunto de descriptores de las imágenes de referencia
    for ref, descriptores_ref in descriptores_a_usar.items():
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptores_detectada, descriptores_ref)
        similitud = len(matches)
        
        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_coincidencia = ref
    
    return mejor_coincidencia

# Función para detectar el color de la carta en el juego Uno
def detectar_color_uno(imagen):
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Definir los umbrales de color en HSV para los colores del juego Uno
    umbrales = {
        'Rojo': [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
        'Amarillo': [(20, 100, 100), (30, 255, 255)],
        'Verde': [(40, 50, 50), (90, 255, 255)],
        'Azul': [(100, 50, 50), (140, 255, 255)]
    }
    
    color_detectado = 'desconocido'
    max_area = 0
    
    for color, umbrales_color in umbrales.items():
        mask = None
        for (lower, upper) in zip(umbrales_color[0::2], umbrales_color[1::2]):
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            if mask is None:
                mask = cv2.inRange(imagen_hsv, lower_bound, upper_bound)
            else:
                mask += cv2.inRange(imagen_hsv, lower_bound, upper_bound)
        
        # Calcular el área del color detectado
        area = cv2.countNonZero(mask)
        
        if area > max_area:
            max_area = area
            color_detectado = color
    
    return color_detectado

# Captura de video desde la cámara
captura = cv2.VideoCapture(2)
captura.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
captura.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

# Dimensiones del rectángulo fijo en el centro
rect_width = 250
rect_height = 350

# Variables de estado
tipo_carta = "1"
leyenda = "Detectando cartas normales"

while True:
    ret, frame = captura.read()
    if not ret:
        break

    # Crear un marco negro del mismo tamaño que el frame
    black_frame = np.zeros_like(frame)

    # Definir el rectángulo fijo en el centro de la imagen
    frame_height, frame_width = frame.shape[:2]
    x_center = frame_width // 2
    y_center = frame_height // 2
    x = x_center - rect_width // 2
    y = y_center - rect_height // 2

    # Dibujar el rectángulo fijo en el centro en el frame original
    cv2.rectangle(frame, (x, y), (x + rect_width, y + rect_height), (0, 255, 0), 2)

    # Recortar la región de interés
    roi = frame[y:y + rect_height, x:x + rect_width]
    
    # Aplicar un filtro de nitidez a la región de interés
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    roi_sharpened = cv2.filter2D(roi, -1, kernel)

    # Convertir la región de interés a escala de grises y aplicar desenfoque
    gray = cv2.cvtColor(roi_sharpened, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detección de bordes
    edged = cv2.Canny(blurred, 50, 150)
    
    # Encontrar contornos en la región de interés
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Suponiendo que la carta es el contorno más grande
        largest_contour = max(contours, key=cv2.contourArea)
        x_contour, y_contour, w_contour, h_contour = cv2.boundingRect(largest_contour)
        
        # Ajustar el recorte para asegurarse de que se captura toda la carta detectada
        carta_detectada = roi[y_contour:y_contour + h_contour, x_contour:x_contour + w_contour]
        
        # Detectar el color de la carta
        color_detectado = detectar_color_uno(carta_detectada)
        
        # Comparar con las imágenes de referencia según el tipo de carta
        if tipo_carta == "1":
            mejor_coincidencia = comparar_con_referencia(carta_detectada, comodines=False)
        elif tipo_carta == "2":
            mejor_coincidencia = comparar_con_referencia(carta_detectada, comodines=True)
        
        if mejor_coincidencia:
            if tipo_carta == "1":
                color, numero = mejor_coincidencia
                descripcion = descripciones.get(f"{color}_{numero}", "Descripción no disponible")
                cv2.putText(frame, f'Color: {color_detectado}, Numero: {numero}', (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                color, tipo_comodin = mejor_coincidencia
                descripcion = descripciones.get(f"{color}_{tipo_comodin}", "Descripción no disponible")
                cv2.putText(frame, f'Color: Multicolor, Tipo: {tipo_comodin}', (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Añadir un fondo negro detrás del texto de la descripción
            text_size = cv2.getTextSize(descripcion, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = 10  # Ajuste para iniciar el texto desde la izquierda
            text_y = y + rect_height + 40  # Ajuste de la posición y
            cv2.rectangle(frame, (text_x - 5, text_y - text_size[1] - 10), (text_x + text_size[0] + 5, text_y + 10), (0, 0, 0), cv2.FILLED)
            cv2.putText(frame, f'{descripcion}', (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            cv2.putText(frame, 'Carta no identificada', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Mostrar la leyenda en la parte superior
    cv2.putText(frame, leyenda, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Fusionar el frame con el marco negro
    result_frame = cv2.bitwise_or(frame, black_frame)
    
    # Mostrar el resultado
    cv2.imshow('Carta Uno', result_frame)

    # Esperar a que el usuario presione una tecla
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        tipo_carta = "1"
        leyenda = "Detectando cartas normales"
    elif key == ord('2'):
        tipo_carta = "2"
        leyenda = "Detectando comodines"

# Liberar la captura y cerrar todas las ventanas
captura.release()
cv2.destroyAllWindows()
