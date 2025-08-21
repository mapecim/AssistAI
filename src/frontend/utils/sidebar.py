import streamlit as st

def show_sidebar():
    st.sidebar.title("AssistAI 🏀")
    # st.sidebar.subheader(f"Bienvenido {st.session_state['name']}")
    st.sidebar.page_link("app.py", label="🏀 Home")
    st.sidebar.page_link("pages/1_chat.py", label="💬 Chat")
    st.sidebar.page_link("pages/2_player_report.py", label="📈 Player Report")
    st.sidebar.page_link("pages/3_team_report.py", label="📊 Team Report")
    st.sidebar.page_link("pages/4_search_similar.py", label="🔍 Search Similar Players")
    st.sidebar.page_link("pages/5_performance_prediction.py", label="🔮 Performance Prediction")

    # st.sidebar.markdown("---")
    # if st.sidebar.button("Cerrar sesión"):
    #     st.session_state["logged_in"] = False
    #     st.session_state.pop('username', None)
    #     st.session_state.pop('name', None)
    #     st.session_state.pop('chat_id', None)
    #     st.session_state.pop('messages', None)
    #     st.rerun()
