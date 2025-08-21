import streamlit as st
import requests
import re
import time
from frontend.utils.sidebar import show_sidebar

from config import BACKEND_URL

# Lógica de la página del chat
st.set_page_config(page_title="AssistAI - Chat", page_icon="💬", initial_sidebar_state='expanded', layout='wide')

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.error("Por favor, inicie sesión para acceder al chat.")
#     st.stop()

show_sidebar()

# Lógica del chat (migrada desde tu código original)
urlAPI = BACKEND_URL

st.title("AssistAI Chat 💬")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_placeholder" not in st.session_state:
    st.session_state.welcome_placeholder = st.empty()

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False

if "chat_id" not in st.session_state:
    try:
        r = requests.get(f"{urlAPI}/chat/get_id")
    except requests.exceptions.ConnectionError:
        st.error("La API de AssistAI no está disponible. Por favor, inténtelo de nuevo más tarde.")
        st.stop()
    st.session_state['chat_id'] = r.json()
    st.session_state['status'] = 'active'
    
if not st.session_state.welcome_shown:
    st.session_state.welcome_placeholder.markdown("""
        ¡Bienvenido a **AssistAI Chat**! 👋

        Soy tu asistente personal de estadísticas y términos de baloncesto. Puedes preguntarme sobre cualquier dato del juego o pedirme que te explique conceptos relacionados con el baloncesto, y te daré una respuesta clara y útil. Además, me puedes dar la url de un partido Euroliga para que te proporcione un informe detallado del mismo.

        **Ejemplos de preguntas que puedes hacerme:**
        * "¿Quién fue el mejor tirador de 3 de la 2023/24?"
        * "¿Cuál es el equipo con más victorias esta temporada?"
        * "¿Qué es el PER?"
        * "¿Cómo se calcula el rating ofensivo?"
        * "Analiza este partido https://www.euroleaguebasketball.net/en/euroleague/game-center/2024-25/as-monaco-fenerbahce-beko-istanbul/E2024/330/"

        ¡Empieza a chatear escribiendo tu primer mensaje en la barra de abajo! 👇
    """)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # st.markdown(message["content"], unsafe_allow_html=True)

        latex_pattern = re.compile(r'\s*\\\[\s*(.*?)\s*\\\]\s*', re.DOTALL)
        parts = latex_pattern.split(message["content"])

        for i, part in enumerate(parts):
            if i % 2 == 0:  # Parte de texto normal
                if part.strip():
                    st.markdown(part, unsafe_allow_html=True)
            else:  # Parte con código LaTeX
                st.latex(part)

if prompt := st.chat_input("Pregunta lo que quieras"):
    if not st.session_state.welcome_shown:
        st.session_state.welcome_placeholder.empty()
        st.session_state.welcome_shown = True

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        FULL_RESPONSE = ""

        with st.spinner("Pensando..."):
            try:
                r = requests.get(f"{urlAPI}/chat/response?user_question={prompt}&id={st.session_state['chat_id']}")
                assistant_response = r.json()
                if isinstance(assistant_response, str) or assistant_response['success'] == False:
                    assistant_response = "Lo siento, he sufrido algún error al responder a tu pregunta. Inténtalo de nuevo más tarde."
                else:
                    assistant_response = assistant_response['response']['raw']
            except requests.exceptions.RequestException:
                assistant_response = "Lo siento, he sufrido algún error al responder a tu pregunta. Inténtalo de nuevo más tarde."

        latex_pattern = re.compile(r'\s*\\\[\s*(.*?)\s*\\\]\s*', re.DOTALL)
        parts = latex_pattern.split(assistant_response)

        if len(parts) == 1:
            for char in assistant_response:
                FULL_RESPONSE += char
                time.sleep(0.005)
                message_placeholder.markdown(FULL_RESPONSE + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(FULL_RESPONSE, unsafe_allow_html=True)
        else:
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Parte de texto normal
                    if part.strip():
                        st.markdown(part, unsafe_allow_html=True)
                else:  # Parte con código LaTeX
                    st.latex(part)

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})