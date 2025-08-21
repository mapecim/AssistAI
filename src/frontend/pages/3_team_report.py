import streamlit as st
import requests
from frontend.utils.sidebar import show_sidebar
from src.frontend.utils.dashboard_team import render_team_dashboard

from config import BACKEND_URL

# Lógica de la página de informes
st.set_page_config(page_title="AssistAI - Team Report", page_icon="📊", initial_sidebar_state='expanded', layout='wide')

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.error("Por favor, inicie sesión para acceder a esta página.")
#     st.stop()

show_sidebar()

st.title("Team Report 📊")

urlAPI = BACKEND_URL

@st.cache_data
def fetch_data():
    try:
        teams_response = requests.get(f"{urlAPI}/database/teams")
        teams_response.raise_for_status()
        teams_list = teams_response.json()["teams"]

        seasons_response = requests.get(f"{urlAPI}/database/seasons")
        seasons_response.raise_for_status()
        seasons_list = seasons_response.json()["seasons"]
        
        return teams_list, seasons_list
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API para obtener los datos de la base de datos")
        st.stop()

teams_list, seasons_list = fetch_data()

st.header("Team Analysis")

# Selección para el Equipo 1 (siempre visible)
st.subheader("Equipo 1")
col1, col2 = st.columns(2)
team1_name = col1.selectbox("Equipo 1", [""] + teams_list, key="t1_name")
season1_name = col2.selectbox("Seleccionar Temporada", [""] + [s["name"] for s in seasons_list], key="s1_name")
season1_id = next((s["id"] for s in seasons_list if s["name"] == season1_name), None)

# Opción para añadir un segundo equipo
compare_mode = st.checkbox("Comparar con otro equipo")

if compare_mode:
    # Selección para el Equipo 2 (solo visible si se activa el checkbox)
    st.subheader("Equipo 2")
    col3, col4 = st.columns(2)
    team2_name = col3.selectbox("Equipo 2", [""] + teams_list, key="t2_name")
    season2_name = col4.selectbox("Seleccionar Temporada", [""] + [s["name"] for s in seasons_list], key="s2_name")
    season2_id = next((s["id"] for s in seasons_list if s["name"] == season2_name), None)
else:
    team2_name = None
    season2_id = None

if st.button("Crear Informe"):
    if not team1_name or not season1_id:
        st.warning("Por favor, seleccione un equipo y una temporada para el Equipo 1.")
    elif compare_mode and (not team2_name or not season2_id):
        st.warning("Por favor, seleccione un equipo y una temporada para el Equipo 2.")
    else:
        with st.spinner("Generando informe..."):
            try:
                if compare_mode:
                    response = requests.get(
                        f"{urlAPI}/team-report/report_stats",
                        params={
                            "team1": team1_name,
                            "season1": season1_id,
                            "team2": team2_name,
                            "season2": season2_id
                        }
                    )
                else:
                    response = requests.get(
                        f"{urlAPI}/team-report/report_stats",
                        params={
                            "team1": team1_name,
                            "season1": season1_id
                        }
                    )
                response.raise_for_status()
                stats = response.json()

                avg_stats = None

                if not compare_mode or season1_id == season2_id:
                    response2 = requests.get(
                        f"{urlAPI}/team-report/season_avg_stats",
                        params={
                            "season": season1_id
                        }
                    )
                    response2.raise_for_status()
                    avg_stats = response2.json()

                render_team_dashboard(stats, avg_stats)

            except requests.exceptions.RequestException as e:
                    st.error(f"Error al obtener los datos")