import cv2
import numpy as np

# Función para convertir BGR a HSV y obtener el valor del punto central
def obtener_color_central(frame):
    # Convertir el frame de BGR a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Obtener las dimensiones del frame
    height, width, _ = frame.shape
    
    # Calcular el punto central
    x_center = width // 2
    y_center = height // 2
    
    # Obtener el valor HSV del punto central
    color_central_hsv = hsv[y_center, x_center]
    
    return color_central_hsv

# Captura de video desde la cámara
captura = cv2.VideoCapture(2)  # Cambiar el índice si se necesita usar otra cámara

while True:
    ret, frame = captura.read()
    if not ret:
        break

    # Obtener el valor HSV del punto central
    color_central_hsv = obtener_color_central(frame)
    
    # Dibujar un círculo en el punto central
    height, width, _ = frame.shape
    x_center = width // 2
    y_center = height // 2
    cv2.circle(frame, (x_center, y_center), 5, (0, 255, 0), 2)
    
    # Mostrar el valor HSV en la imagen
    hsv_text = f'H: {color_central_hsv[0]}, S: {color_central_hsv[1]}, V: {color_central_hsv[2]}'
    cv2.putText(frame, hsv_text, (x_center - 100, y_center - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Mostrar el frame
    cv2.imshow('Color HSV del Centro', frame)
    
    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura y cerrar las ventanas
captura.release()
cv2.destroyAllWindows()
