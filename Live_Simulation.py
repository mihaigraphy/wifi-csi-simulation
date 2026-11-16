import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import serial
import time

# --- 1. Connexion au port série (virtuel /tmp/vport_pc) ---
SERIAL_PORT = "/tmp/vport_pc"
BAUD_RATE = 921600

print(f"Connexion au port série {SERIAL_PORT}...")
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print(f"Erreur de connexion au port série {SERIAL_PORT} : {e}")
    exit(1)

# --- 2. Configuration de la fenêtre interactive Matplotlib ---
plt.ion()  # Active le mode interactif
fig, ax = plt.subplots(figsize=(10, 4))

num_subcarriers = 64
window_size = 50   # Nombre de paquets affichés à l'écran (fenêtre glissante)
buffer_csi = np.zeros((window_size, num_subcarriers))

line, = ax.plot([], [], color='royalblue', lw=2)
ax.set_ylim(-3, 3)
ax.set_xlim(0, window_size)
ax.set_title("Streaming Live - Composante Principale CSI (PC1)", fontsize=12)
ax.set_xlabel("Index des trames glissantes")
ax.set_ylabel("Amplitude projetée")
ax.grid(True, linestyle='--', alpha=0.6)

print("Démarrage du flux live en attente de paquets... Appuie sur Ctrl+C dans le terminal pour stopper.")

try:
    while True:
        # --- 3. Lecture du port série ---
        line_data = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line_data:
            continue

        try:
            # Transformation de la ligne CSV en tableau numpy
            csi_packet = np.array([float(x) for x in line_data.split(",")])
        except ValueError:
            # Ignorer les lignes de texte non numériques / en-têtes
            continue

        print(f"Paquet reçu ! Taille : {csi_packet.shape} | Moyenne : {np.mean(csi_packet):.2f}")

        new_packet = csi_packet.reshape(1, -1)

        # Ajustement automatique de la taille du buffer si nécessaire
        if new_packet.shape[1] != buffer_csi.shape[1]:
            num_subcarriers = new_packet.shape[1]
            buffer_csi = np.zeros((window_size, num_subcarriers))

        # --- 4. Mise à jour de la fenêtre glissante (FIFO) ---
        buffer_csi = np.vstack((buffer_csi[1:], new_packet))

        # --- 5. Traitement à la volée (Standardisation + ACP) ---
        scaler = StandardScaler()
        scaled_buffer = scaler.fit_transform(buffer_csi)

        pca = PCA(n_components=1)
        pc1 = pca.fit_transform(scaled_buffer).flatten()

        # --- 6. Rafraîchissement du graphique ---
        line.set_ydata(pc1)
        line.set_xdata(np.arange(window_size))
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("\nArrêt du flux live demandé par l'utilisateur.")
finally:
    ser.close()
    plt.ioff()
    plt.show()
