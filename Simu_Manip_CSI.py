import numpy as np

# --- 1. Paramètres de simulation ---
num_packets = 500      # Nombre de trames reçues au cours du temps
num_subcarriers = 64   # Nombre de sous-porteuses OFDM (standard 802.11n 20MHz)

# --- 2. Génération d'un canal de base complexe (Réel + Imaginaire) ---
np.random.seed(42)
# Canal statique de base + bruit thermique gaussien
base_channel = (np.random.randn(1, num_subcarriers) + 1j * np.random.randn(1, num_subcarriers)) * 0.5
thermal_noise = (np.random.randn(num_packets, num_subcarriers) + 1j * np.random.randn(num_packets, num_subcarriers)) * 0.05

# --- 3. Simulation d'un mouvement humain (Effet Doppler / Variation de trajet) ---
# On simule par exemple une respiration ou un balancement à 0.5 Hz
t = np.linspace(0, 10, num_packets)
human_movement = np.sin(2 * np.pi * 0.5 * t)[:, np.newaxis] * 0.4

# Matrice CSI combinée (Dimensions : [Trames, Sous-porteuses])
H_csi = base_channel + thermal_noise + human_movement

# --- 4. Extraction des métriques physiques (Amplitude et Phase) ---
# Amplitude = sqrt(Re^2 + Im^2)
amplitude = np.abs(H_csi)

# Phase = arctan2(Im, Re) (en radians)
phase = np.angle(H_csi)

print(f"Dimensions de la matrice CSI : {H_csi.shape}")
print(f"Amplitude moyenne sur la sous-porteuse 10 : {np.mean(amplitude[:, 10]):.4f}")
