import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- Initialisation de l'application Dash ---
app = dash.Dash(__name__)
app.title = "CSI Wi-Fi - Dashboard Live"

# Paramètres globaux du buffer
num_subcarriers = 64
window_size = 60
buffer_csi = np.ones((window_size, num_subcarriers), dtype=np.float32) * 0.5
scaler = StandardScaler()
pca = PCA(n_components=1)

# --- Design de l'interface (Layout) ---
app.layout = html.Div(style={'backgroundColor': '#0f172a', 'color': '#e2e8f0', 'padding': '20px', 'fontFamily': 'sans-serif'}, children=[

    # Titre principal
    html.H1("📡 Radar & Monitoring Wi-Fi CSI (Live Web)", style={'textAlign': 'center', 'color': '#38bdf8', 'marginBottom': '20px'}),

    # Grille principale (2 colonnes)
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        # Graphique 1 : Signal ACP (PC1)
        html.Div(style={'flex': '1', 'backgroundColor': '#1e293b', 'padding': '15px', 'borderRadius': '8px'}, children=[
            dcc.Graph(id='live-pc1-graph', config={'displayModeBar': False})
        ]),
        # Graphique 2 : Heatmap CSI
        html.Div(style={'flex': '1', 'backgroundColor': '#1e293b', 'padding': '15px', 'borderRadius': '8px'}, children=[
            dcc.Graph(id='live-heatmap', config={'displayModeBar': False})
        ]),
    ]),

    # Panneau de contrôle et Statut
    html.Div(style={'display': 'flex', 'gap': '20px', 'backgroundColor': '#1e293b', 'padding': '20px', 'borderRadius': '8px', 'alignItems': 'center'}, children=[

        # Contrôles (Slider & Radio)
        html.Div(style={'flex': '1'}, children=[
            html.Label("Sensibilité du Seuil d'Alarme :", style={'fontWeight': 'bold'}),
            dcc.Slider(id='threshold-slider', min=0.5, max=2.5, step=0.1, value=1.2,
                       marks={0.5: '0.5', 1.2: '1.2 (Normal)', 2.5: '2.5'},
                       tooltip={"placement": "bottom", "always_visible": True}),

            html.Br(),
            html.Label("Mode de Simulation :", style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='mode-radio',
                options=[
                    {'label': ' 1. Absence totale', 'value': 0},
                    {'label': ' 2. Respiration / Repos', 'value': 1},
                    {'label': ' 3. Marche / Mouvement', 'value': 2}
                ],
                value=0,
                style={'marginTop': '10px'}
            )
        ]),

        # Boîte de Statut (Alerte / Calme)
        html.Div(id='status-box', style={
            'flex': '1', 'padding': '20px', 'borderRadius': '6px', 'textAlign': 'center',
            'backgroundColor': '#166534', 'border': '2px solid #22c55e'
        }, children=[
            html.H3("✅ SITUATION CALME", id='status-title', style={'margin': '0 0 10px 0', 'color': '#ffffff'}),
            html.P("Aucune présence détectée", id='status-text', style={'margin': '0', 'fontSize': '16px', 'color': '#e2e8f0'})
        ])
    ]),

    # Composant d'intervalle pour le rafraîchissement (équivalent de FuncAnimation à ~30 FPS / 30ms)
    dcc.Interval(id='interval-component', interval=30, n_intervals=0)
])

# --- Callback de mise à jour en temps réel ---
@app.callback(
    [Output('live-pc1-graph', 'figure'),
     Output('live-heatmap', 'figure'),
     Output('status-box', 'style'),
     Output('status-title', 'children'),
     Output('status-text', 'children')],
    [Input('interval-component', 'n_intervals')],
    [State('threshold-slider', 'value'),
     State('mode-radio', 'value')]
)
def update_dashboard(n_intervals, threshold, mode):
    global buffer_csi

    t = n_intervals * 0.035

    # 1. Simulation dynamique selon le mode choisi
    if mode == 0:
        activity_amp = 0.03
    elif mode == 1:
        activity_amp = 0.25
    else:
        activity_amp = 1.4

    # 2. Simulation d'un nouveau paquet CSI (FIFO roulant)
    subcarrier_pattern = np.sin(np.linspace(0, np.pi * 3, num_subcarriers))
    noise = np.random.randn(num_subcarriers) * 0.04
    motion_effect = np.sin(2 * np.pi * 1.2 * t) * activity_amp * subcarrier_pattern
    new_packet = np.clip(0.5 + noise + motion_effect * 0.3, 0.01, 2.0)

    buffer_csi[:-1] = buffer_csi[1:]
    buffer_csi[-1] = new_packet

    # 3. Calcul ACP (Standardisation + PCA)
    scaled = scaler.fit_transform(buffer_csi)
    pc1 = pca.fit_transform(scaled).ravel()

    # 4. Analyse d'alerte
    max_recent = np.max(np.abs(pc1[-15:]))
    is_alert = max_recent > threshold

    # Style dynamique de la boîte de statut
    if is_alert:
        status_style = {'flex': '1', 'padding': '20px', 'borderRadius': '6px', 'textAlign': 'center', 'backgroundColor': '#991b1b', 'border': '2px solid #ef4444'}
        status_title = "🚨 ACTIVITÉ DÉTECTÉE !"
        status_text = f"Intensité : {max_recent:.2f} > Seuil : {threshold:.2f}"
        pc1_color = '#ef4444'
    else:
        status_style = {'flex': '1', 'padding': '20px', 'borderRadius': '6px', 'textAlign': 'center', 'backgroundColor': '#166534', 'border': '2px solid #22c55e'}
        status_title = "✅ SITUATION CALME"
        status_text = f"Intensité : {max_recent:.2f} (Sous le seuil)"
        pc1_color = '#38bdf8'

    # 5. Création de la figure Plotly pour le Signal PC1
    fig_pc1 = go.Figure()
    fig_pc1.add_trace(go.Scatter(y=pc1, mode='lines', line=dict(color=pc1_color, width=3), name='PC1'))
    fig_pc1.add_hline(y=threshold, line=dict(color='#ef4444', dash='dash'), name='Seuil +')
    fig_pc1.add_hline(y=-threshold, line=dict(color='#ef4444', dash='dash'), showlegend=False)
    fig_pc1.update_layout(
        title="Signal Extrait de Mouvement (ACP - PC1)",
        paper_bgcolor='#1e293b', plot_bgcolor='#1e293b', font=dict(color='#e2e8f0'),
        margin=dict(l=30, r=30, t=40, b=30), height=250
    )

    # 6. Création de la figure Plotly pour la Heatmap CSI
    fig_heatmap = go.Figure(data=go.Heatmap(z=buffer_csi.T, colorscale='Magma'))
    fig_heatmap.update_layout(
        title="Matrice CSI (Temps x Sous-porteuses)",
        paper_bgcolor='#1e293b', plot_bgcolor='#1e293b', font=dict(color='#e2e8f0'),
        margin=dict(l=30, r=30, t=40, b=30), height=250
    )

    return fig_pc1, fig_heatmap, status_style, status_title, status_text

# --- Lancement du serveur local ---
if __name__ == '__main__':
    print("Démarrage du serveur Dash... Ouvre http://127.0.0.1:8050 dans ton navigateur.")
    app.run_server(debug=False, host='127.0.0.1', port=8050)
