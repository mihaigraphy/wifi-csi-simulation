import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- 1. Simulation d'une matrice CSI (Trames x Sous-porteuses) ---
num_packets = 500
num_subcarriers = 64
np.random.seed(42)

# Simulation de données complexes et passage à l'amplitude
H_csi = (np.random.randn(num_packets, num_subcarriers) +
         1j * np.random.randn(num_packets, num_subcarriers)) + \
        np.sin(np.linspace(0, 20, num_packets))[:, np.newaxis] * 0.5
amplitude = np.abs(H_csi)  # Forme : (500, 64)

# --- 2. Prétraitement (Standardisation) ---
# L'ACP est sensible à l'échelle. On centre et réduit chaque sous-porteuse.
scaler = StandardScaler()
amplitude_scaled = scaler.fit_transform(amplitude)

# --- 3. Application de l'ACP (Scikit-Learn) ---
# On choisit de garder par exemple les 3 premières composantes principales
n_components = 3
pca = PCA(n_components=n_components)
X_pca = pca.fit_transform(amplitude_scaled)  # Forme de sortie : (500, 3)

# --- 4. Analyse de la variance expliquée ---
# Te indique quelle part d'information est portée par chaque composante
explained_variance = pca.explained_variance_ratio_
print(f"Variance expliquée par composante : {explained_variance * 100}%")
print(f"Somme de la variance conservée : {np.sum(explained_variance) * 100:.2f}%")

# --- 5. Visualisation de la première composante (PC1) ---
plt.figure(figsize=(10, 4))
plt.plot(X_pca[:, 0], color='crimson', label='PC1 (Composante Principale 1)')
plt.title("Évolution temporelle de la 1ère Composante Principale (PC1 du CSI)", fontsize=12)
plt.xlabel("Index des trames (Temps)")
plt.ylabel("Amplitude projetée")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
