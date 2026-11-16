import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def butter_lowpass_filter(data, cutoff_freq, fs, order=4):
    """
    Applique un filtre passe-bas de Butterworth.
    data : tableau numpy (temps x sous-porteuses)
    cutoff_freq : fréquence de coupure en Hz (ex: 2.0 Hz pour la respiration/mouvement lent)
    fs : fréquence d'échantillonnage (nombre de paquets reçus par seconde, ex: 50 Hz)
    order : ordre du filtre (plus il est élevé, plus la pente de coupure est raide)
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    # axis=0 applique le filtre le long du temps pour chaque sous-porteuse
    filtered_data = filtfilt(b, a, data, axis=0)
    return filtered_data

# --- 1. Simulation d'une matrice CSI bruitée ---
num_packets = 500
num_subcarriers = 64
fs = 50.0      # Fréquence d'acquisition : 50 paquets par seconde
t = np.linspace(0, 10, num_packets)

np.random.seed(42)
# Bruit haute fréquence + mouvement lent (0.5 Hz)
base_noise = (np.random.randn(num_packets, num_subcarriers) + 1j * np.random.randn(num_packets, num_subcarriers)) * 0.2
human_movement = np.sin(2 * np.pi * 0.5 * t)[:, np.newaxis] * 0.5
H_csi = base_noise + human_movement
amplitude_raw = np.abs(H_csi)

# --- 2. Filtrage Butterworth (Coupure à 2 Hz) ---
cutoff_frequency = 2.0  # On garde les mouvements sous 2 Hz, on supprime le reste
amplitude_smooth = butter_lowpass_filter(amplitude_raw, cutoff_frequency, fs, order=4)

# --- 3. Comparaison visuelle sur une sous-porteuse ---
plt.figure(figsize=(12, 5))
plt.plot(t, amplitude_raw[:, 10], label='Amplitude Brute (Bruitée)', color='lightgray', alpha=0.8)
plt.plot(t, amplitude_smooth[:, 10], label='Amplitude Filtrée (Butterworth)', color='royalblue', linewidth=2)
plt.title("Effet du filtre passe-bas de Butterworth sur une sous-porteuse CSI", fontsize=12)
plt.xlabel("Temps (secondes)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
