import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report

# --- 1. Simulation d'un dataset (Absent vs Présent) ---
num_windows = 200      # Nombre total d'enregistrements (fenêtres)
window_size = 50       # Nombre de paquets par fenêtre (ex: 1 seconde à 50 Hz)
num_subcarriers = 64   # Nombre de sous-porteuses OFDM

X_windows = []
y_labels = []

np.random.seed(42)
for i in range(num_windows):
    # On alterne : les 100 premiers échantillons = Absent (0), les 100 suivants = Présent (1)
    is_present = i >= 100

    # Bruit thermique de base
    base_noise = np.random.randn(window_size, num_subcarriers) * 0.05

    if is_present:
        # Simulation d'un mouvement ou d'une respiration dans la pièce
        t = np.linspace(0, 2, window_size)
        movement = np.sin(2 * np.pi * 1.0 * t)[:, np.newaxis] * 0.4
        csi_window = base_noise + movement
        label = 1
    else:
        csi_window = base_noise
        label = 0

    X_windows.append(np.abs(csi_window))
    y_labels.append(label)

X_windows = np.array(X_windows)  # Forme : (200, 50, 64)
y_labels = np.array(y_labels)    # Forme : (200,)

# --- 2. Extraction de features (ACP + Variance par fenêtre) ---
X_features = []
for window in X_windows:
    # A. Standardisation de la fenêtre
    scaler = StandardScaler()
    scaled_window = scaler.fit_transform(window)

    # B. Application de l'ACP (on réduit à 3 composantes principales)
    pca = PCA(n_components=3)
    pca_result = pca.fit_transform(scaled_window)  # Forme : (50, 3)

    # C. Calcul de la variance sur le temps pour chaque composante principale
    # C'est notre signature de mouvement/présence (vecteur de taille 3)
    feature_vector = np.var(pca_result, axis=0)
    X_features.append(feature_vector)

X_features = np.array(X_features)  # Forme finale pour le SVM : (200, 3)

# --- 3. Séparation Train / Test et Entraînement du SVM ---
X_train, X_test, y_train, y_test = train_test_split(X_features, y_labels, test_size=0.3, random_state=42)

# Initialisation et entraînement du SVM (Noyau RBF, un classique non linéaire)
svm_clf = SVC(kernel='rbf', C=1.0, gamma='scale')
svm_clf.fit(X_train, y_train)

# --- 4. Évaluation du modèle ---
y_pred = svm_clf.predict(X_test)
print("--- Rapport de Classification SVM ---")
print(classification_report(y_test, y_pred, target_names=["Absent", "Présent"]))
