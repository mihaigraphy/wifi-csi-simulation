import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import time
import csv
from datetime import datetime

# --- 1. Initialisation du fichier de log CSV ---
log_filename = "csi_alerts_log.csv"
# Ouverture du fichier en mode écriture ('w') avec écriture de l'en-tête
with open(log_filename, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Max_Amplitude_PC1", "Threshold_Used"])

print(f"Fichier de log initialisé : {log_filename}")

# --- 2. Configuration de la figure et du widget ---
plt.ion()
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)

num_subcarriers = 64
window_size = 50
buffer_csi = np.zeros((window_size, num_subcarriers))

line, = ax.plot([], [], color='royalblue', lw=2, label='PC1 CSI')
initial_threshold = 1.0
threshold_line = ax.axhline(y=initial_threshold, color='crimson', linestyle='--', lw=1.5, label='Seuil d\'alarme')

ax.set_ylim(-3, 3)
ax.set_xlim(0, window_size)
ax.set_title("Streaming Live CSI - Monitoring avec Journalisation CSV", fontsize=12)
ax.set_xlabel("Index des trames glissantes")
ax.set_ylabel("Amplitude projetée")
ax.legend(loc='upper right')
ax.grid(True, linestyle='--', alpha=0.6)

# Widget Slider
ax_slider = plt.axes([0.25, 0.1, 0.5, 0.03])
thresh_slider = Slider(ax=ax_slider, label='Seuil d\'alerte', valmin=0.1, valmax=2.5, valinit=initial_threshold, color='crimson')

print("Démarrage du live... Appuie sur Ctrl+C pour stopper et sauvegarder.")

# Variables pour le cooldown des alertes (éviter le spam dans le CSV)
last_alert_time = 0
cooldown_seconds = 2.0

try:
    step = 0
    while True:
        # Simulation d'un nouveau paquet
        t = step * 0.02
        motion_factor = 1.8 if (step // 60) % 2 == 1 else 0.2
        new_packet_complex = (np.random.randn(1, num_subcarriers) + 1j * np.random.randn(1, num_subcarriers)) * 0.1 + np.sin(2 * np.pi * 1.5 * t) * motion_factor
        new_packet = np.abs(new_packet_complex)

        # Mise à jour du buffer et ACP
        buffer_csi = np.vstack((buffer_csi[1:], new_packet))
        scaler = StandardScaler()
        scaled_buffer = scaler.fit_transform(buffer_csi)
        pca = PCA(n_components=1)
        pc1 = pca.fit_transform(scaled_buffer).flatten()

        current_threshold = thresh_slider.val
        threshold_line.set_ydata([current_threshold, current_threshold])

        max_val = np.max(np.abs(pc1))
        current_time = time.time()

        # Logique d'alerte et écriture dans le CSV
        if max_val > current_threshold:
            line.set_color('crimson')

            # Si le cooldown est passé, on enregistre l'alerte dans le fichier CSV
            if (current_time - last_alert_time) > cooldown_seconds:
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open(log_filename, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp_str, f"{max_val:.4f}", f"{current_threshold:.2f}"])

                print(f"[ALERTE] Mouvement détecté à {timestamp_str} | Max: {max_val:.2f} > Seuil: {current_threshold:.2f}")
                last_alert_time = current_time
        else:
            line.set_color('royalblue')

        # Rafraîchissement graphique
        line.set_ydata(pc1)
        line.set_xdata(np.arange(window_size))
        fig.canvas.draw()
        fig.canvas.flush_events()

        time.sleep(0.02)
        step += 1

except KeyboardInterrupt:
    print(f"\nArrêt demandé. Les alertes ont été enregistrées dans {log_filename}.")
    plt.ioff()
    plt.show()
