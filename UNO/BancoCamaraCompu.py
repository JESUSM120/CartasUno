import cv2
import os

# Configuración de la cámara
cap = cv2.VideoCapture(2)

# Dirección para guardar las imágenes
save_dir = "C:/Users/Jesus/Pictures/Unov2"
os.makedirs(save_dir, exist_ok=True)

# Función para guardar la imagen
def save_image(img, count):
    file_name = f"imagen_{count:03d}.jpg"
    file_path = os.path.join(save_dir, file_name)
    cv2.imwrite(file_path, img)
    print(f"Imagen {count} guardada en {file_path}")

# Main loop
count = 1
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Hacer una copia del frame para guardar la imagen sin el rectángulo
    frame_copy = frame.copy()

    # Definir el área para la carta (ajustar según sea necesario)
    x, y, w, h = 100, 100, 200, 300
    
    # Incrementar el tamaño del rectángulo
    incremento = 12  # Asumiendo 10 píxeles como medio centímetro
    x -= incremento
    y -= incremento
    w += 2 * incremento
    h += 2 * incremento
    
    # Dibujar el rectángulo en el frame original
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Mostrar el frame con el rectángulo
    cv2.imshow('Captura de imagen', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('l'):
        # Extraer y guardar la región de interés (ROI) del frame sin el rectángulo
        carta_img = frame_copy[y:y+h, x:x+w]
        save_image(carta_img, count)
        count += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
