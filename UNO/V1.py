import cv2
import os

# Función para preprocesar la imagen
def preprocesar_imagen(imagen):
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (5, 5), 0)
    return gris

# Cargar imágenes de referencia del juego Uno desde una carpeta
directorio_referencia = "C:\\Users\\Jesus\\Pictures\\UnoV2"
imagenes_referencia = {}
for archivo in os.listdir(directorio_referencia):
    if archivo.endswith(".jpg") or archivo.endswith(".png"):
        nombre, extension = os.path.splitext(archivo)
        color, numero = nombre.split("_")
        imagen = cv2.imread(os.path.join(directorio_referencia, archivo))
        # Preprocesar la imagen de referencia
        imagen = preprocesar_imagen(imagen)
        imagenes_referencia[(color, numero)] = imagen

# Función para comparar una carta detectada con las imágenes de referencia
def comparar_con_referencia(imagen_detectada, umbral_similitud=0.7):
    mejor_coincidencia = None
    mejor_similitud = 0
    
    for (color_ref, numero_ref), imagen_referencia in imagenes_referencia.items():
        # Calcular la similitud entre la carta detectada y la imagen de referencia
        similitud = calcular_similitud(imagen_detectada, imagen_referencia)
        
        # Actualizar la mejor coincidencia
        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_coincidencia = (color_ref, numero_ref)
    
    # Verificar si la mejor coincidencia supera el umbral de similitud
    if mejor_similitud < umbral_similitud:
        mejor_coincidencia = None
    
    return mejor_coincidencia

# Función para calcular la similitud entre dos imágenes
def calcular_similitud(imagen1, imagen2):
    # Calcular histogramas de las imágenes
    hist1 = cv2.calcHist([imagen1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([imagen2], [0], None, [256], [0, 256])
    
    # Calcular la similitud utilizando la correlación de histogramas
    similitud = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similitud

# Captura de video desde la cámara
captura = cv2.VideoCapture(1)

while True:
    ret, frame = captura.read()
    if not ret:
        break

    # Preprocesar la imagen capturada
    frame_preprocesado = preprocesar_imagen(frame)

    # Comparar con las imágenes de referencia
    mejor_coincidencia = comparar_con_referencia(frame_preprocesado)

    # Mostrar el resultado en la ventana
    if mejor_coincidencia:
        color, numero = mejor_coincidencia
        cv2.putText(frame, f'Color: {color}, Numero: {numero}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, 'Carta no identificada', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.imshow('Carta Uno', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

captura.release()
cv2.destroyAllWindows()
