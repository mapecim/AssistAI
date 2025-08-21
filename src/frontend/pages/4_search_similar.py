import streamlit as st
import requests
import pandas as pd
from frontend.utils.sidebar import show_sidebar

from config import BACKEND_URL, PLAYER_MAP

# Lógica de la página de informes
st.set_page_config(page_title="AssistAI - Buscar Jugadores Similares", page_icon="🔍", initial_sidebar_state='expanded', layout='wide')

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.error("Por favor, inicie sesión para acceder a esta página.")
#     st.stop()

show_sidebar()

st.title("Buscar Jugadores Similares 🔍")

urlAPI = BACKEND_URL

@st.cache_data
def fetch_data():
    try:
        players_response = requests.get(f"{urlAPI}/database/players")
        players_response.raise_for_status()
        players_list = players_response.json()["players"]

        seasons_response = requests.get(f"{urlAPI}/database/seasons")
        seasons_response.raise_for_status()
        seasons_list = seasons_response.json()["seasons"]

        player_stats_names_response = requests.get(f"{urlAPI}/database/player-stats-names")
        player_stats_names_response.raise_for_status()
        player_stats_names = player_stats_names_response.json()["player_stats_names"]
        cols_to_exclude = ['id', 'name', 'tm_name', 'season_id', 'nat', 'gp', 'w', 'l', 'w_pct']
        player_stats_names = [s for s in player_stats_names if s not in cols_to_exclude]
        player_stats_names = [PLAYER_MAP.get(s, s) for s in player_stats_names]

        return players_list, seasons_list, player_stats_names
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API para obtener los datos de la base de datos")
        st.stop()

players_list, seasons_list, player_stats_names = fetch_data()

# Selección para el Jugador base (siempre visible)
st.subheader("Jugador base")
col1, col2 = st.columns(2)
player1_name = col1.selectbox("Nombre", [""] + players_list, key="p1_name")
season1_name = col2.selectbox("Temporada", [""] + [s["name"] for s in seasons_list], key="s1_name")
season1_id = next((s["id"] for s in seasons_list if s["name"] == season1_name), None)

same_role = st.checkbox("Buscar solo con jugadores del mismo rol")

selected_metrics = st.multiselect(
    "Selecciona métricas a ponderar",
    player_stats_names
)

weights = {}
if selected_metrics:
    st.write("Asigna un peso:")
    for metric in selected_metrics:
        weight_value = st.slider(f"{metric}", 0.0, 5.0, 1.0, 0.1)
        weights[metric] = weight_value

if st.button("Buscar"):
    if not player1_name or not season1_id:
        st.warning("Por favor, seleccione un jugador y una temporada.")
    else:
        with st.spinner("Buscando..."):
            try:
                response = requests.get(
                    f"{urlAPI}/search-similar/compare-player",
                    params={
                        "player_name": player1_name,
                        "season_id": season1_id,
                        "same_role": same_role
                    }
                )
                response.raise_for_status()
                stats = response.json()

                # Mostrar jugador base como cabecera
                col1, col2, col3 = st.columns(3)
                col1.metric("Nombre", stats["jugador_base"]["name"])
                col2.metric("Temporada", stats["jugador_base"]["season_id"])
                col3.metric("Rol", stats["jugador_base"]["role"])

                st.markdown("---")
                st.subheader("Jugadores Similares")

                # Convertir resultados a DataFrame para tabla
                df_results = pd.DataFrame(stats["resultados_similares"])
                df_results["similarity_score"] = df_results["similarity_score"].apply(lambda x: f"{float(x):.2f}%")
                
                st.dataframe(
                    df_results.rename(columns={
                        "name": "Nombre",
                        "season_id": "Temporada",
                        "team_name": "Equipo",
                        "similarity_score": "Similitud"
                    }),
                    hide_index=True
                )

                # Mostrar tarjetas para el top 3
                st.markdown("### 🏆 Top 3 Similares")
                top3 = stats["resultados_similares"][:3]
                cols = st.columns(3)
                for i, player in enumerate(top3):
                    with cols[i]:
                        st.metric(
                            f"{player['name']} ({player['season_id']})",
                            f"{float(player['similarity_score']):.2f}%",
                            delta=None
                        )
                        st.caption(player["team_name"])

            except requests.exceptions.RequestException as e:
                    st.error(f"Error al obtener los datos")