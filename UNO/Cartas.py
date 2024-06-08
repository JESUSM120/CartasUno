import cv2
import numpy as np

def capture_image():
    cap = cv2.VideoCapture(0)  # Cambia el índice si tienes múltiples cámaras
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara")
            break
        cv2.imshow("Captura de imagen", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return frame

def preprocess_image(image):
    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Aplicar desenfoque para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Aplicar umbralización
    _, thresh = cv2.threshold(blurred, 128, 255, cv2.THRESH_BINARY_INV)
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Encontrar el contorno más grande
        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        card = image[y:y+h, x:x+w]
        card = cv2.resize(card, (300, 500))  # Redimensionar a un tamaño estándar
        return card
    else:
        print("No se encontró ninguna carta en la imagen")
        return None

# Capturar la imagen desde la cámara
frame = capture_image()

# Procesar la imagen capturada
preprocessed_image = preprocess_image(frame)

# Mostrar la imagen preprocesada si se detecta una carta
if preprocessed_image is not None:
    cv2.imshow("Carta procesada", preprocessed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No se detectó ninguna carta.")
