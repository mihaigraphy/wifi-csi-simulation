# CSI Wi-Fi – Station Interaction Dashboard

> **Projet** : Analyse en temps réel du canal de communication Wi-Fi sur un système Wi-Fi 802.11k/n (OFDM, 20 MHz – 64 sous-porteuses).

## 📦 Structure du dépôt

```
Simulation/
├── README.md                ← Ce fichier
├── Makefile                 # Automatisation (install, clean, all)
├── ACPS               (à confirmer, voici la liste complète ci-dessous)
└── *.py                  : scripts principaux
```

### Raftesbooks (files principaux)

| Fichier | Rôle |
|---|---|
| `ACP.py` | Utilitaire `apply CSI` – simulation d'un flux entrant (PCI‑ALEX / oscillateur). Contient les variables clés `num_packets`, `num_subcarriers`, amplitudes complexes. |
| `Filtre_Butterworth.py` | Filtre passe-bas de Butterworth (wnh) sur amplitude brute pour isoler mouvements infrarrangés (~0.5 Hz). |
| `Heatmap_2D.py` | Trace de la chaleur à partir de `amplitude = np.abs(H)` – visualisation spatiale et temporelle. |
| `Simu_Manip_CSI.py` | Version manipulatrice (manipulation matricielle) – base de données CSI/Phase. |
| `Live_Simulation.py` | Flux vidéo interrompu (FIFO) sur port virtuel `/tmp/vport_pc` via `pyserial`. Visualise la composante PC1 en temps réel. |
| `IHM.py` | Interactif avec curseur / radar / heatmap live + détection de présence. Envoie les données à `Interactive_Dashboard.py`. |
| `Interactive_Dashboard.py` | 🎯 **NOUVEAU** : interface 2D animée (60 FPS) présentant : <br>• Carte de couverture physique (émetteur / récepteur, cible humaine) <br>• Propagation des ondes Wi-Fi, rayons réfléchis <br>• Heatmap CSI, courbe ACP/PC1 <br>• Jauge d'activité + badge alert > Sliders + Radiobuttons controls. |

## ✅ Requirement Système

* **OS** : Linux (Fedora)  
* **Python** : ≥ 3.15 (moteur `lib65537`-based sandbox)  
* **Environnement virtuel** : active `~/Documents/Ingé/EPISEN/S5/Mespi/Simulation/.venv`  
  ```bash
  source ./.venv/bin/activate
  ```

### Emplacements nécessaires du port virtuel
* Port série virtuel : **`/tmp/vport_pc`** – doit être exposé pour que les scripts capturent la chaîne critiquet. Configurez vos OSPF/UP et QoS pour que `/tmp/vport_pc` soit accessible aux applications système (FDLB, OSPF, etc.).

### Commandes utiles

```bash
# Aktiver-en l'environnement
source Simulation/.venv/bin/activate

# Générer les dépendances (incluant skML, numpy, pandas, etc.)
${VENV}/bin/pip install -r Simulation/requirements.txt

# Installe scikit-learn ADDITIONNLY
${VENV}/bin/pip install scikit-learn pyserial

# Lancer le simulateur interactif (Live DS)
./Simulation/Interactive_Dashboard.py
```

## 📋 Résumé des fichiers

### ACP (filtrer le canal)

```python
# Dédéfin des constantes
num_packets = 500       # nombre de trames receves
num_subcarriers = 64    # sous-porteuses OFDM (standard 802.11n 20MHz)

np.random.seed(42)
# Bloc OUBNOUS pour générer H_csi (complexe)
base_noise = (np.random.randn(num_packets, num_subcarriers) + 1j * np.random.randn(...)) * 0.2
human_movement = np.sin(2*np.pi*0.5*t)[..., np.newaxis] * 0.5
H_csi = base_noise + human_movement
amplitude_raw = np.abs(H_csi)
```

### Filtre Butterworth (sur amplitude)

```python
from scipy.signal import butter, filtfilt
nyquist = 0.5*fs
normal_cutoff = cutoff_freq/nyquist
b, a = butter(order, normal_cutoff, btype='low', analog=False)
filtered = filtfilt(b, a, data, axis=0)
```

### Radar/Heatmap

```python
import pickle
# Heatmap : amplitude = np.abs(H) ou H_csi; cmap='magma'; aspect='auto'
```

### Script Interactif Principal

- Lit `serial.readline()` depuis `/tmp/vport_pc`.
- FIFO `np.vstack((buffer_csi[1:], new_packet))`.
- Reduces complex → ampéllité (`np.abs`).
- Calcule la transformée `StandardScaler → PCA(n_components=1)`.
- Produit la jauge live et détecte si `max(|pc1|) > seuil`.

## 🛠️ Lignes Clés Optimisées

Les dernières versions (voir `Interactive_Dashboard.py`) utilisent :

- **`FuncAnimation`** pour dessiner la grille 40 FPS natively (intervalle de 16 ms ≈ 60 images/s).
- **Pré-allocation** des surfaces GraphicsObjects (`patches`, rectangles, `bbox`).
- **Réalignement** des ondes par boucle locale (pas de `fill_cat` ni `blit` coûteux).
- **Réutilisation** du scaler, PCA et matrice `cmap` (pas de refit inutile lors du frame).
- **Mode réactif** du `RadioButtons` et du bouton `reset`.
- **Cache** par frame, graphiquement léger.

## 🔧 Scénarios Tests Prévus

| Scénario | Mode Radio | Résultat attendu |
|---|---|---|
| Silence total (signal faible bruit) | `_Absence_` | Heatmap près du fond (#0f172a), PC1 bleu, jauge 0/alert. |
| Respiration lente (~0.5 Hz) | `_Respiration_` | Cible tourne doucement autour (5/4). Jauge +0.25+. Seuil actif si > seuil. |
| Marche/Moulement (~1.2 Hz) | `_Marche_` | Cible trace ligne sinueuse ; PC1 montaille plus dynamiquement. Seuil adaptatif avec slider. |

## 🧢 Fonctionnalités (à jour)

- **Animations fluides** grâce à `FuncAnimation` personnalisé + `intervals≈16 ms`.
- **Dashboard SVG/Matplotlib Dark Background** cohérent.
- **Seuils ajustables** via `Slider` en bas.
- **Jauge colorée** reflétant intensité (`#38bdf8` bleu clair  |  `#ef4444` rouge vif).
- **Log CSV automatisé** `csi_alerts_log.csv` (chronologie, max amplitude, seuil).

## 📄 Build & CI

Aucun processus de construction configuré (`Makefile` définit `all: install`, `clean`, `venv`). Pour le runner CI, exécutez manuellement :

```bash
source .venv/bin/activate && pip install -r requirements.txt
```

## 📝 Notes Supplémentaires

- Le port virtuel `/tmp/vport_pc` n'est pas une adresse LAN réelle. Il doit provenir d'un routeur virtuel ou d'un emulateur (e.g. **Piwik**, **WireGuard** bare-metal, ou une prise directe de l'étiquetage FRD/OSSFAOD). Vérifiez qu'il est accessible depuis le sysctl / firewalld / ufw.
- Les paramètres CSI en temps réel proviennent du flux numérique SNR (suggestion de la couche 5 GHz). Pour produire les vues radaro, vous devez disposer du localizer (BTS/AP position/intensity).


---
*Version 1.0 – Draft generated for "Mespi / Simulation" project.*
