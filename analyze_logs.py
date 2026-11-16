import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Chargement des données avec Pandas ---
log_filename = "csi_alerts_log.csv"

try:
    # On lit le CSV et on convertit automatiquement la colonne 'Timestamp' en datetime
    df = pd.read_csv(log_filename, parse_dates=['Timestamp'])
    print(f"Fichier '{log_filename}' chargé avec succès. {len(df)} alertes trouvées.")
except FileNotFoundError:
    print(f"Erreur : Le fichier {log_filename} est introuvable. Lance d'abord le script de live monitoring.")
    exit()

# Si le fichier est vide (seulement l'en-tête)
if df.empty:
    print("Le fichier de log ne contient aucune alerte pour le moment.")
    exit()

# --- 2. Tracé de l'historique temporel ---
plt.figure(figsize=(12, 6))

# Tracé des pics d'amplitude détectés au cours du temps
plt.scatter(
    df['Timestamp'],
    df['Max_Amplitude_PC1'],
    color='crimson',
    s=50,
    zorder=3,
    label='Alerte de Mouvement (PC1 Max)'
)

# Tracé de la ligne de seuil correspondante
plt.plot(
    df['Timestamp'],
    df['Threshold_Used'],
    color='gray',
    linestyle='--',
    alpha=0.7,
    label='Seuil configuré'
)

# --- 3. Mise en forme du graphique ---
plt.title("Historique des alertes de présence - Wi-Fi CSI", fontsize=14)
plt.xlabel("Date et Heure", fontsize=12)
plt.ylabel("Amplitude de la Composante Principale (PC1)", fontsize=12)
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)

# Ajustement automatique de l'affichage des dates sur l'axe X
plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.show()
