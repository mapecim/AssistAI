import streamlit as st
import requests
import os
from frontend.utils.sidebar import show_sidebar

from config import BACKEND_URL

# Lógica de la página de predicción
st.set_page_config(page_title="AssistAI - Performance Prediction", page_icon="🔮", initial_sidebar_state='expanded', layout='wide')

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.error("Por favor, inicie sesión para acceder a esta página.")
#     st.stop()

show_sidebar()

st.title("Performance Prediction 🔮")
st.write("Selecciona una alineación de cinco jugadores para predecir su rendimiento.")

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
        
        return players_list, seasons_list
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con la API para obtener los datos de la base de datos")
        st.stop()
players_list, seasons_list = fetch_data()

# Selección para 5 jugadores
selected_players = []
st.subheader("Selecciona 5 jugadores y sus temporadas")
for i in range(5):
    cols = st.columns(2)
    player_name = cols[0].selectbox(f"Player {i+1}", players_list, key=f"p{i+1}_name")
    season_name = cols[1].selectbox(f"Season {i+1}", [s["name"] for s in seasons_list], key=f"s{i+1}_name")
    season_id = next((s["id"] for s in seasons_list if s["name"] == season_name), None)
    selected_players.append({f"player{i+1}_name": player_name, f"season{i+1}_id": season_id})

if st.button("Predict Performance"):
    # Comprobar que todos los desplegables están seleccionados
    if all(p[f"player{i+1}_name"] and p[f"season{i+1}_id"] for i, p in enumerate(selected_players)):
        # Lógica para llamar al endpoint de predicción
        
        params = {}
        for i, player_data in enumerate(selected_players):
            params[f"player{i+1}_name"] = player_data[f"player{i+1}_name"]
            params[f"season{i+1}_id"] = player_data[f"season{i+1}_id"]

        try:
            response = requests.get(
                f"{urlAPI}/performance-prediction/predict",
                params=params
            )
            response.raise_for_status()
            prediction_result = response.json()

            st.markdown("---")
            st.subheader("Predicted Lineup Performance")

            predicted_net_rating = prediction_result.get("predicted_net_rating")
            lineup = prediction_result.get("lineup")

            # Lógica para determinar el color y el icono
            if predicted_net_rating is None:
                st.error("No se pudo obtener la predicción del Net Rating.")
            else:
                if predicted_net_rating > 5:
                    color = "#28a745" # verde
                    icon = "🔥"
                    message = "¡Una alineación de élite! Espera un rendimiento superior."
                elif predicted_net_rating > 0:
                    color = "#17a2b8" # azul
                    icon = "👍"
                    message = "Esta alineación debería tener un rendimiento positivo."
                elif predicted_net_rating > -5:
                    color = "#ffc107" # amarillo
                    icon = "👀"
                    message = "Una alineación con un rendimiento aceptable, pero no destacable."
                else:
                    color = "#dc3545" # rojo
                    icon = "👎"
                    message = "Esta alineación podría tener problemas. Cuidado con el rendimiento bajo."

                st.write(f"**Lineup:** {', '.join(lineup)}")

                st.markdown(
                    f"""
                    <div style="
                        background-color: {color};
                        padding: 20px;
                        border-radius: 10px;
                        color: white;
                        text-align: center;
                    ">
                        <h3>{icon} Predicted Net Rating: {predicted_net_rating:.2f} {icon}</h3>
                        <p>{message}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        except requests.exceptions.RequestException as e:
            st.error(f"Error al obtener la predicción")
    else:
        st.warning("Por favor, selecciona un jugador y una temporada para los cinco espacios.")
