import numpy as np
import matplotlib.pyplot as plt

# --- 1. Simulation rapide des données CSI (Trames x Sous-porteuses) ---
num_packets = 500      # Axe temporel (nombre de trames reçues)
num_subcarriers = 64   # Axe fréquentiel (sous-porteuses OFDM)

np.random.seed(42)
base_channel = (np.random.randn(1, num_subcarriers) + 1j * np.random.randn(1, num_subcarriers)) * 0.5
thermal_noise = (np.random.randn(num_packets, num_subcarriers) + 1j * np.random.randn(num_packets, num_subcarriers)) * 0.05

# Simulation d'un mouvement périodique (ex: balancement ou respiration)
t = np.linspace(0, 10, num_packets)
human_movement = np.sin(2 * np.pi * 0.5 * t)[:, np.newaxis] * 0.4

H_csi = base_channel + thermal_noise + human_movement
amplitude = np.abs(H_csi)  # Dimensions : (500, 64)

# --- 2. Tracé de la Heatmap 2D ---
plt.figure(figsize=(10, 5))

# On transpose (.T) pour mettre le Temps sur l'axe X et les Sous-porteuses sur l'axe Y
plt.imshow(
    amplitude.T,
    aspect='auto',          # Adapte les proportions de l'image à la fenêtre
    origin='lower',         # Place l'indice 0 en bas de l'axe Y
    cmap='jet',             # Palette de couleurs (jet, viridis, plasma...)
    extent=[0, 10, 1, num_subcarriers] # Étendue réelle des axes : [t_min, t_max, sc_min, sc_max]
)

plt.colorbar(label="Amplitude CSI")
plt.xlabel("Temps (secondes)", fontsize=12)
plt.ylabel("Index des sous-porteuses OFDM", fontsize=12)
plt.title("Évolution spatio-temporelle de l'amplitude CSI (Effet de mouvement)", fontsize=14)

plt.tight_layout()
plt.show()
