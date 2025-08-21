import streamlit as st
from streamlit_theme import st_theme
import yaml
import os
from yaml.loader import SafeLoader
from frontend.utils.sidebar import show_sidebar

# Carga de credenciales desde users.yaml
def load_credentials():
    yaml_path = os.path.join(os.path.dirname(__file__), "users.yaml")
    with open(yaml_path, "r") as file:
        credentials = yaml.load(file, Loader=SafeLoader)
    return credentials['credentials']['usernames']

def login(usernames):
    st.set_page_config(page_title="AssistAI", page_icon='🏀', initial_sidebar_state='collapsed', layout='wide')

    st.title("Login")
    
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
    
        if submit_button:
            if username in usernames and usernames[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["name"] = usernames[username]["name"]
                st.success("Login correcto")
                st.rerun()
            elif not username and not password:
                st.warning("Por favor, ingresa tus credenciales")
            else:
                st.error("Usuario o contraseña inválidos")
                st.session_state["logged_in"] = False
                st.session_state.pop('username', None)
                st.session_state.pop('name', None)

def show_main_page():
    st.set_page_config(page_title="AssistAI", page_icon='🏀', initial_sidebar_state='expanded', layout='wide')
    show_sidebar()

    st.title("Bienvenido a AssistAI 🏀")
    st.write(f"Hola! Usa los botones de abajo o el menú de la izquierda para navegar.")

    st.markdown(
        """
        ### ¿Qué puedes hacer aquí?
        - **💬 Chat:** haz preguntas sobre datos de baloncesto y recibe respuestas inteligentes.
        - **📈 Player Report:** genera informes detallados de jugadores.
        - **📊 Team Report:** analiza el rendimiento de equipos completos.
        - **🔍 Search Similar Players:** encuentra jugadores con características similares.
        - **🔮 Performance Prediction:** predice el impacto de combinaciones de jugadores en pista.
        """,
        unsafe_allow_html=True
    )

    theme = st_theme()
    if theme is not None:
        if theme['base'] == "light":
            st.markdown("""
                <style>
                    .button-container {
                        display: flex;
                        justify-content: center;     /* centra horizontalmente */
                        align-items: center;         /* centra verticalmente */
                        flex-wrap: wrap;             /* permite pasar a segunda fila */
                        gap: 10px;
                        width: 100%;
                    }
                            
                    .big-button {
                        display: inline-block;
                        padding: 15px 25px;
                        font-size: 20px;
                        font-weight: bold;
                        color: #31333f !important;
                        background-color: #F0F2F6;
                        border: 2px solid black;
                        border-radius: 10px;
                        text-decoration: none !important;
                        text-align: center;
                        margin: 10px;
                        cursor: pointer;
                    }
                    .big-button:hover {
                        background-color: #31333f;
                        color: white !important;
                    }
                </style>
                            
                <div class="button-container">
                    <a class="big-button" href="/chat" target="_self">💬 Chat</a>
                    <a class="big-button" href="/player_report" target="_self">📈 Player Report</a>
                    <a class="big-button" href="/team_report" target="_self">📊 Team Report</a>
                    <a class="big-button" href="/search_similar" target="_self">🔍 Search Similar Players</a>
                    <a class="big-button" href="/performance_prediction" target="_self">🔮 Performance Prediction</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                    .button-container {
                        display: flex;
                        justify-content: center;     /* centra horizontalmente */
                        align-items: center;         /* centra verticalmente */
                        flex-wrap: wrap;             /* permite pasar a segunda fila */
                        gap: 10px;
                        width: 100%;
                    }
                            
                    .big-button {
                        display: inline-block;
                        padding: 15px 25px;
                        font-size: 20px;
                        font-weight: bold;
                        color: white !important;
                        background-color: #262730;
                        border: 2px solid white;
                        border-radius: 10px;
                        text-decoration: none !important;
                        text-align: center;
                        margin: 10px;
                    }
                    .big-button:hover {
                        background-color: white;
                        color: black !important;
                    }
                </style>
                            
                <div class="button-container">
                    <a class="big-button" href="/chat" target="_self">💬 Chat</a>
                    <a class="big-button" href="/player_report" target="_self">📈 Player Report</a>
                    <a class="big-button" href="/team_report" target="_self">📊 Team Report</a>
                    <a class="big-button" href="/search_similar" target="_self">🔍 Search Similar Players</a>
                    <a class="big-button" href="/performance_prediction" target="_self">🔮 Performance Prediction</a>
                </div>
                """, unsafe_allow_html=True)


# Lógica principal
# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False

# if not st.session_state["logged_in"]:
#     usernames = load_credentials()
#     login(usernames)
# else:
#     show_main_page()

show_main_page()
