import serial
import time
import numpy as np

# Connexion au port virtuel côté "ESP32"
port = "/tmp/vport_esp32"
ser = serial.Serial(port, 921600)
print(f"Faux ESP32 démarré sur {port}. Envoi des trames CSI...")

try:
    step = 0
    while True:
        # Simulation de 64 valeurs d'amplitude CSI (nombres aléatoires + mouvement périodique)
        t = step * 0.02
        motion = np.sin(2 * np.pi * 1.5 * t) * 2.0 if (step // 50) % 2 == 1 else 0.0
        subcarriers = np.random.uniform(10, 20, 64) + motion

        # Format CSV classique : valeur1,valeur2,valeur3...\n
        csv_line = ",".join([f"{val:.2f}" for val in subcarriers]) + "\n"

        ser.write(csv_line.encode('utf-8'))
        time.sleep(0.02)  # 50 paquets par seconde
        step += 1

except KeyboardInterrupt:
    ser.close()
    print("Faux ESP32 éteint.")
