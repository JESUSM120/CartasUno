import cv2
import os
import numpy as np
import pandas as pd

# Cargar imágenes de referencia del juego Uno desde una carpeta
directorio_referencia = "C:\\Users\\Jesus\\Pictures\\UnoV1"
imagenes_referencia = {}
for archivo in os.listdir(directorio_referencia):
    if archivo.endswith(".jpg") or archivo.endswith(".png"):
        nombre, extension = os.path.splitext(archivo)
        color, numero = nombre.split("_")
        imagen = cv2.imread(os.path.join(directorio_referencia, archivo))
        imagenes_referencia[(color, numero)] = imagen

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

# Función para comparar una carta detectada con las imágenes de referencia
def comparar_con_referencia(imagen_detectada):
    mejor_coincidencia = None
    mejor_similitud = 0
    
    # Calcular descriptores para la imagen detectada
    _, descriptores_detectada = calcular_descriptores(imagen_detectada)
    
    if descriptores_detectada is None:
        return None
    
    # Comparar con cada conjunto de descriptores de las imágenes de referencia
    for (color_ref, numero_ref), descriptores_ref in descriptores_referencia.items():
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptores_detectada, descriptores_ref)
        similitud = len(matches)
        
        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_coincidencia = (color_ref, numero_ref)
    
    return mejor_coincidencia

# Función para detectar el color de la carta en el juego Uno
def detectar_color_uno(imagen):
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Definir los umbrales de color en HSV para los colores del juego Uno
    umbrales = {
        'rojo': [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
        'amarillo': [(20, 100, 100), (30, 255, 255)],
        'verde': [(40, 50, 50), (90, 255, 255)],
        'azul': [(100, 50, 50), (140, 255, 255)]
    }
    
    color_detectado = 'desconocido'
    max_area = 0
    
    for color, (lower1, upper1, *rest) in umbrales.items():
        # Crear máscara de color
        mask1 = cv2.inRange(imagen_hsv, np.array(lower1), np.array(upper1))
        
        if rest:
            lower2, upper2 = rest
            mask2 = cv2.inRange(imagen_hsv, np.array(lower2), np.array(upper2))
            mask = cv2.add(mask1, mask2)
        else:
            mask = mask1
        
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
        
        # Comparar con las imágenes de referencia
        mejor_coincidencia = comparar_con_referencia(carta_detectada)
        
        if mejor_coincidencia:
            color, numero = mejor_coincidencia
            descripcion = descripciones.get(f"{color}_{numero}", "Descripción no disponible")
            cv2.putText(frame, f'Color: {color_detectado}, Numero: {numero}', (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f'{descripcion}', (x, y + rect_height + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            cv2.putText(frame, 'Carta no identificada', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Fusionar el frame con el marco negro
    result_frame = cv2.bitwise_or(frame, black_frame)
    
    # Mostrar el resultado
    cv2.imshow('Carta Uno', result_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

captura.release()
cv2.destroyAllWindows()
