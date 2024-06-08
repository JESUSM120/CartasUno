import cv2
import os

# Cargar imágenes de referencia del juego Uno desde una carpeta
directorio_referencia = "/home/jesusmc/Imágenes/Uno 2"
imagenes_referencia = {}
for archivo in os.listdir(directorio_referencia):
    if archivo.endswith(".jpg") or archivo.endswith(".png"):
        nombre, extension = os.path.splitext(archivo)
        color, numero = nombre.split("_")
        imagen = cv2.imread(os.path.join(directorio_referencia, archivo))
        imagenes_referencia[(color, numero)] = imagen

# Función para comparar una carta detectada con las imágenes de referencia
def comparar_con_referencia(imagen_detectada):
    mejor_coincidencia = None
    mejor_similitud = 0
    
    for (color_ref, numero_ref), imagen_referencia in imagenes_referencia.items():
        # Calcular la similitud entre la carta detectada y la imagen de referencia
        similitud = calcular_similitud(imagen_detectada, imagen_referencia)
        
        # Actualizar la mejor coincidencia
        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_coincidencia = (color_ref, numero_ref)
    
    return mejor_coincidencia

# Función para calcular la similitud entre dos imágenes
def calcular_similitud(imagen1, imagen2):
    # Convertir imágenes a escala de grises
    gris1 = cv2.cvtColor(imagen1, cv2.COLOR_BGR2GRAY)
    gris2 = cv2.cvtColor(imagen2, cv2.COLOR_BGR2GRAY)
    
    # Calcular histogramas de las imágenes
    hist1 = cv2.calcHist([gris1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([gris2], [0], None, [256], [0, 256])
    
    # Calcular la similitud utilizando la correlación de histogramas
    similitud = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similitud

# Captura de video desde la cámara
captura = cv2.VideoCapture(0)

while True:
    ret, frame = captura.read()
    if not ret:
        break

    # Redimensionar la imagen para facilitar la visualización
    #frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

    # Comparar con las imágenes de referencia
    carta_detectada = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir de BGR a RGB para matplotlib
    mejor_coincidencia = comparar_con_referencia(carta_detectada)

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
