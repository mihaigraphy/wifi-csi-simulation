import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.animation import FuncAnimation
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ==============================================================================
#  1. INITIALISATION & CONFIGURATION DU STYLE
# ==============================================================================
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 8), num="CSI Wi-Fi - Radar & Détection Live Fluide")
fig.patch.set_facecolor('#0f172a')

# Disposition optimisée avec subplots
gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 0.9], hspace=0.35, wspace=0.25,
                      left=0.06, right=0.96, top=0.92, bottom=0.18)

ax_room = fig.add_subplot(gs[0, 0])     # Vue 2D Pièce (Radar)
ax_heatmap = fig.add_subplot(gs[0, 1])  # Heatmap CSI
ax_pc1 = fig.add_subplot(gs[1, 0])      # Signal ACP (PC1)
ax_status = fig.add_subplot(gs[1, 1])   # Dashboard de Statut

# Paramètres du buffer de données
num_subcarriers = 64
window_size = 60
buffer_csi = np.ones((window_size, num_subcarriers), dtype=np.float32) * 0.5
time_axis = np.arange(window_size)
subcarrier_pattern = np.sin(np.linspace(0, np.pi * 3, num_subcarriers)).astype(np.float32)

# Objets pour le traitement
scaler = StandardScaler()
pca = PCA(n_components=1)

# ==============================================================================
#  2. CONFIGURATION DES ÉLÉMENTS GRAPHIQUES (ARTISTS)
# ==============================================================================

# --- A. VUE 2D DE LA PIÈCE ---
ax_room.set_facecolor('#1e293b')
ax_room.set_xlim(0, 10)
ax_room.set_ylim(0, 8)
ax_room.set_title("1. Cartographie 2D de la Pièce & Ondes Wi-Fi", fontsize=11, fontweight='bold', color='#e2e8f0')
ax_room.set_xlabel("Distance X (m)", color='#94a3b8')
ax_room.set_ylabel("Distance Y (m)", color='#94a3b8')
ax_room.tick_params(colors='#94a3b8')

tx_pos = (1.5, 4.0)
rx_pos = (8.5, 4.0)

ax_room.plot(tx_pos[0], tx_pos[1], 'g^', markersize=14, label='Émetteur (Tx)')
ax_room.plot(rx_pos[0], rx_pos[1], 'bs', markersize=12, label='Récepteur (Rx)')
ax_room.plot([tx_pos[0], rx_pos[0]], [tx_pos[1], rx_pos[1]], 'w--', alpha=0.3, label='Ligne de vue')

person_point, = ax_room.plot([], [], 'ro', markersize=16, label='Cible humaine')
ray_tx, = ax_room.plot([], [], 'r:', alpha=0.6, lw=1.5)
ray_rx, = ax_room.plot([], [], 'r:', alpha=0.6, lw=1.5)

# Cercles d'ondes Wi-Fi concentriques
wave_circles = [Circle(tx_pos, radius=float(r), color='#38bdf8', fill=False, alpha=0.2, lw=1.5)
                for r in np.linspace(0.5, 4.0, 5)]
for circle in wave_circles:
    ax_room.add_patch(circle)

ax_room.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155', fontsize=8, labelcolor='#e2e8f0')

# --- B. HEATMAP SPATIO-TEMPORELLE ---
ax_heatmap.set_title("2. Matrice CSI (Temps x Sous-porteuses)", fontsize=11, fontweight='bold', color='#e2e8f0')
im_heatmap = ax_heatmap.imshow(
    buffer_csi.T, aspect='auto', origin='lower', cmap='magma',
    extent=(0, window_size, 1, num_subcarriers), vmin=0, vmax=2, interpolation='nearest'
)
ax_heatmap.set_xlabel("Fenêtre glissante (Trames)", color='#94a3b8')
ax_heatmap.set_ylabel("Sous-porteuses OFDM", color='#94a3b8')
ax_heatmap.tick_params(colors='#94a3b8')
cbar = fig.colorbar(im_heatmap, ax=ax_heatmap, pad=0.02)
cbar.ax.tick_params(colors='#94a3b8')
cbar.set_label("Amplitude CSI", color='#94a3b8')

# --- C. SIGNAL ACP (PC1) ---
ax_pc1.set_facecolor('#1e293b')
ax_pc1.set_xlim(0, window_size)
ax_pc1.set_ylim(-3.5, 3.5)
ax_pc1.set_title("3. Signal Extrait de Mouvement (ACP - PC1)", fontsize=11, fontweight='bold', color='#e2e8f0')
ax_pc1.set_xlabel("Index temporel", color='#94a3b8')
ax_pc1.set_ylabel("Amplitude projetée", color='#94a3b8')
ax_pc1.tick_params(colors='#94a3b8')
ax_pc1.grid(True, linestyle=':', color='#334155', alpha=0.7)

line_pc1, = ax_pc1.plot(time_axis, np.zeros(window_size), color='#38bdf8', lw=2.5, label='PC1')
line_thresh_pos = ax_pc1.axhline(y=1.2, color='#ef4444', linestyle='--', lw=1.5, label='Seuil Alarme')
line_thresh_neg = ax_pc1.axhline(y=-1.2, color='#ef4444', linestyle='--', lw=1.5)
ax_pc1.legend(loc='upper right', facecolor='#0f172a', edgecolor='#334155', fontsize=8, labelcolor='#e2e8f0')

# --- D. DASHBOARD DE STATUT & JAUGE ---
ax_status.set_facecolor('#1e293b')
ax_status.axis('off')
ax_status.set_title("4. Indicateurs & État du Système", fontsize=11, fontweight='bold', color='#e2e8f0')

status_box = FancyBboxPatch((0.05, 0.52), 0.9, 0.38, boxstyle="round,pad=0.05",
                            facecolor='#166534', edgecolor='#22c55e', lw=2)
ax_status.add_patch(status_box)

status_text = ax_status.text(0.5, 0.71, "✅ SITUATION CALME\nAucune présence détectée",
                             ha='center', va='center', fontsize=13, fontweight='bold', color='#ffffff')

ax_status.text(0.05, 0.38, "Niveau d'activité instantané :", fontsize=10, color='#94a3b8')
bar_bg = Rectangle((0.05, 0.20), 0.9, 0.12, facecolor='#0f172a', edgecolor='#334155')
ax_status.add_patch(bar_bg)
bar_level = Rectangle((0.05, 0.20), 0.01, 0.12, facecolor='#38bdf8')
ax_status.add_patch(bar_level)

gauge_text = ax_status.text(0.5, 0.08, "Intensité : 0.00 / Seuil : 1.20",
                            ha='center', va='center', fontsize=9, color='#cbd5e1')

# ==============================================================================
#  3. CONTRÔLES INTERACTIFS
# ==============================================================================
ax_slider_thresh = plt.axes((0.10, 0.08, 0.35, 0.03), facecolor='#1e293b')
ax_radio_mode = plt.axes((0.55, 0.04, 0.25, 0.09), facecolor='#1e293b')
ax_button_reset = plt.axes((0.84, 0.06, 0.10, 0.05), facecolor='#1e293b')

slider_thresh = Slider(
    ax=ax_slider_thresh, label='Sensibilité Seuil ', valmin=0.5, valmax=2.5, valinit=1.2,
    color='#ef4444', track_color='#0f172a'
)
slider_thresh.label.set_color('#e2e8f0')
slider_thresh.valtext.set_color('#e2e8f0')

radio_mode = RadioButtons(
    ax=ax_radio_mode, labels=('1. Absence totale', '2. Respiration / Repos', '3. Marche / Mouvement'),
    active=0, activecolor='#38bdf8'
)
for text in radio_mode.labels:
    text.set_color('#e2e8f0')
    text.set_fontsize(9)

btn_reset = Button(ax=ax_button_reset, label='Réinitialiser', color='#334155', hovercolor='#475569')
btn_reset.label.set_color('#ffffff')
btn_reset.label.set_fontweight('bold')

def reset_buffer(event):
    global buffer_csi
    buffer_csi.fill(0.5)

btn_reset.on_clicked(reset_buffer)

current_alert_state = False

# ==============================================================================
#  4. FONCTION DE MISE À JOUR OPTIMISÉE
# ==============================================================================
def update(frame):
    global buffer_csi, current_alert_state

    mode_label = radio_mode.value_selected
    if 'Absence' in mode_label:
        mode = 0
    elif 'Respiration' in mode_label:
        mode = 1
    else:
        mode = 2

    t = frame * 0.035

    # 1. Position de la cible
    if mode == 0:
        px, py = 8.5, 7.0
        activity_amp = 0.03
    elif mode == 1:
        px = 5.0 + 0.08 * np.sin(2 * np.pi * 0.3 * t)
        py = 4.0 + 0.05 * np.cos(2 * np.pi * 0.3 * t)
        activity_amp = 0.25
    else:
        walk_t = np.sin(2 * np.pi * 0.15 * t)
        px = 5.0 + 2.5 * walk_t
        py = 4.0 + 1.8 * np.cos(2 * np.pi * 0.15 * t)
        activity_amp = 1.4

    # 2. Mise à jour position 2D
    person_point.set_data([px], [py])
    ray_tx.set_data([tx_pos[0], px], [tx_pos[1], py])
    ray_rx.set_data([px, rx_pos[0]], [py, rx_pos[1]])

    # 3. Ondes Wi-Fi
    for i, circle in enumerate(wave_circles):
        r = ((frame * 0.08 + i * 0.7) % 4.0) + 0.2
        circle.set_radius(r)
        circle.set_alpha(max(0.0, 0.35 * (1.0 - r / 4.2)))

    # 4. Simulation du paquet CSI (FIFO roulant optimisé)
    dist_factor = np.sqrt((px - 5.0)**2 + (py - 4.0)**2)
    noise = np.random.randn(num_subcarriers) * 0.04
    motion_effect = np.sin(2 * np.pi * 1.2 * t + dist_factor) * activity_amp * subcarrier_pattern
    new_packet = np.clip(0.5 + noise + motion_effect * 0.3, 0.01, 2.0)

    buffer_csi[:-1] = buffer_csi[1:]
    buffer_csi[-1] = new_packet

    # 5. Calcul ACP allégé
    scaled = scaler.fit_transform(buffer_csi)
    pc1 = pca.fit_transform(scaled).ravel()

    # 6. Mise à jour des tracés
    im_heatmap.set_array(buffer_csi.T)
    line_pc1.set_ydata(pc1)

    threshold = slider_thresh.val
    line_thresh_pos.set_ydata([threshold, threshold])
    line_thresh_neg.set_ydata([-threshold, -threshold])

    # 7. Logique d'alerte & UI dashboard
    max_recent = np.max(np.abs(pc1[-15:]))
    ratio = min(1.0, float(max_recent / (threshold * 1.5)))
    bar_level.set_width(0.9 * ratio)

    is_alert = max_recent > threshold
    if is_alert != current_alert_state:
        current_alert_state = is_alert
        if is_alert:
            status_box.set_facecolor('#991b1b')
            status_box.set_edgecolor('#ef4444')
            status_text.set_text("🚨 ACTIVITÉ DÉTECTÉE !\nMouvement / Présence suspecte")
            line_pc1.set_color('#ef4444')
            bar_level.set_facecolor('#ef4444')
        else:
            status_box.set_facecolor('#166534')
            status_box.set_edgecolor('#22c55e')
            status_text.set_text("✅ SITUATION CALME\nAucune présence détectée")
            line_pc1.set_color('#38bdf8')
            bar_level.set_facecolor('#38bdf8')

    gauge_text.set_text(f"Intensité : {max_recent:.2f}  |  Seuil d'alerte : {threshold:.2f}")

    return (person_point, ray_tx, ray_rx, im_heatmap, line_pc1, line_thresh_pos,
            line_thresh_neg, bar_level, status_box, status_text, gauge_text)

# ==============================================================================
#  5. LANCEMENT DE L'ANIMATION OPTIMISÉE (BLIT=TRUE POUR 60 FPS RÉELS)
# ==============================================================================
# blit=True accélère drastiquement le rafraîchissement graphique sous Linux
ani = FuncAnimation(fig, update, interval=16, blit=True, cache_frame_data=False)

print("Lancement de la simulation ultra-fluide (60 FPS)... Fermez la fenêtre pour quitter.")
plt.show()
