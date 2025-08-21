import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional

from config import PLAYER_MAP, PLAYER_AVG_MAP

def can_show_league(avg_json: Optional[Dict], players: List[Dict]) -> bool:
    if avg_json is None:
        return False
    seasons = {p.get("season_id") for p in players}
    if len(seasons) == 1:
        return True
    return False

def player_profile(player):
    col1, col2 = st.columns(2)
    col1.metric("👤 Nombre", player["name"])
    col2.metric("🏢 Equipo", player["tm_name"])

    col3, col4, col5, col6 = st.columns(4)
    col3.metric("🧍 Rol", player["role"])
    col4.metric("🌍 Nacionalidad", player["nat"])
    col5.metric("📏 Altura", f"{player['height']} cm")
    col6.metric("🎂 Edad", player["age"])

    col7, col8, col9, col10 = st.columns(4)
    col7.metric("🎮 Partidos", player["gp"])
    col8.metric("⏱️ Minutos", round(player["min"], 2))
    col9.metric("🆚 Récord", f"{player['w']}W - {player['l']}L")
    col10.metric("📊 Win%", f"{player['w_pct']*100:.1f}%")


def render_player_dashboard(data, avg_stats=None):
    """
    Renderiza el dashboard completo con estadísticas y gráficos.
    """
    players = data.get('player_stats', [])
    if not players:
        st.warning("No hay datos disponibles para los jugadores y temporadas seleccionados.")
        return
    
    if avg_stats is not None:
        avg_stats = avg_stats["average_stats"]
        show_league = can_show_league(avg_stats, players)
    else:
        show_league = False

    comparison = len(players) == 2

    df_players = pd.DataFrame(players).rename(columns=PLAYER_MAP)

    percentage_cols = [
          "W%", "2PT%", "3PT%", "FG%", "FT%", "eFG%", "TS%",
          "RIM FREQ", "PAINT FREQ", "MID FREQ", "C3 FREQ", "L3 FREQ", "FT Rate",
          "TO%", "LTO%", "DTO%", "AST%", "AST% (2P)", "AST% (3P)", "AST% (FT)",
          "USG%", "AST Ratio", "OR%", "OR% (after 2P)", "OR% (after 3P)",
          "OR% (after FT)", "DR%", "DR% (after 2P)", "DR% (after 3P)", "DR% (after FT)", "TR%",
          "ST%", "BLK%", "BLK% (2P)", "BLK% (3P)",
          "TM TS% (ON)", "TM OR% (ON)", "TM TO% (ON)",
          "OPP TS% (ON)", "OPP OR% (ON)", "OPP TO% (ON)",
          "TM TS% (OFF)", "TM OR% (OFF)", "TM TO% (OFF)",
          "OPP TS% (OFF)", "OPP OR% (OFF)", "OPP TO% (OFF)",
          "TM TS% (NET)", "TM OR% (NET)", "TM TO% (NET)",
          "OPP TS% (NET)", "OPP OR% (NET)", "OPP TO% (NET)",
          ]
    
    # Redondear las columnas de porcentaje a 4 decimales
    for col in percentage_cols:
        if col in df_players.columns:
            df_players[col] = df_players[col].round(4).astype(float) * 100

    # Redondear el resto de columnas numéricas a 2 decimales
    numeric_cols = df_players.select_dtypes(include=np.number).columns
    non_percentage_cols = [col for col in numeric_cols if col not in percentage_cols]
    df_players[non_percentage_cols] = df_players[non_percentage_cols].round(2).astype(float)

    if comparison and players[0]["name"] == players[1]["name"]:
        df_players["Nombre"] = df_players["Nombre"] + " - " + df_players["SEASON"].astype(str)

    if show_league:
        df_league = pd.DataFrame([avg_stats]).rename(columns=PLAYER_AVG_MAP)
        for col in percentage_cols:
            if col in df_league.columns:
                df_league[col] = df_league[col].round(4).astype(float) * 100

        numeric_cols = df_league.select_dtypes(include=np.number).columns
        non_percentage_cols = [col for col in numeric_cols if col not in percentage_cols]
        df_league[non_percentage_cols] = df_league[non_percentage_cols].round(2).astype(float)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 Perfil",
        "🎯 Tiro",
        "🔄 Uso y creación",
        "🔁 Rebote",
        "🛡️ Defensa",
        "📊 Impacto & Avanzadas"
    ])

    def fixed_expander(title: str):
        st.markdown(
            f"<h4 style='margin-bottom:0'>{title}</h4>"
            "<hr style='margin-top:0'>",
            unsafe_allow_html=True
        )
        return st.container()

    ##################################### TAB 1 #####################################
    with tab1:
        st.subheader("Perfil del jugador" if not comparison else "Perfil de jugadores")
        for player in players:
                with st.container(border=True):
                    with fixed_expander(player["name"] + " - " + player["season_id"]):
                        player_profile(player)
    
    ##################################### TAB 2 #####################################
    with tab2:
        st.subheader("Eficiencia de tiro")

        col1, col2 = st.columns(2)
        with col1:
            df_bar = df_players[["Nombre", "PTS"]].copy()
            if show_league and df_league is not None:
                df_bar = pd.concat([
                    df_bar,
                    pd.DataFrame({"Nombre": ["Media Liga"], "PTS": [df_league.iloc[0]["PTS"]]})
                ])
            
            df_bar['PTS_formatted'] = df_bar['PTS'].round(2).astype(str)
            fig_bar = px.bar(df_bar, x="Nombre", y="PTS", text="PTS_formatted", color="Nombre")
            fig_bar.update_traces(textposition="outside", )
            fig_bar.update_layout(xaxis_title="PTS", yaxis_title="")
            st.plotly_chart(fig_bar)

        with col2:
            metrics = ["FG%", "2PT%", "3PT%", "FT%", "eFG%", "TS%"]

            fig_radar = go.Figure()

            # Jugadores
            for _, row in df_players.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row[m] for m in metrics],
                    theta=metrics,
                    fill="toself",
                    name=row["Nombre"]
                ))

            # Media Liga
            if show_league and df_league is not None:
                league_row = df_league.iloc[0]
                fig_radar.add_trace(go.Scatterpolar(
                    r=[league_row[m] for m in metrics],
                    theta=metrics,
                    fill="toself",
                    name="Media Liga",
                    line=dict(dash="dot")
                ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
            )
            st.plotly_chart(fig_radar)

        # ---------------- Bar Chart: Volumen de tiro ----------------
        st.subheader("Volumen de tiro")

        stats = ["2PTM", "2PTA", "3PTM", "3PTA", "FGM", "FGA", "FTM", "FTA"]

        df_offense = df_players[["Nombre"] + stats].copy()

        if show_league and df_league is not None:
            league_row = df_league.iloc[0][stats]
            df_offense = pd.concat([
                df_offense,
                pd.DataFrame([{"Nombre": "Media Liga", **league_row.to_dict()}])
            ])

        df_offense_long = df_offense.melt(id_vars="Nombre", value_vars=stats,
                                         var_name="Stat", value_name="Value")
        
        df_offense_long['Value_formatted'] = df_offense_long['Value'].round(2).astype(str)
        fig_offense = px.bar(
            df_offense_long,
            x="Stat", y="Value",
            color="Nombre",
            barmode="group",
            text="Value_formatted"
        )

        fig_offense.update_traces(textposition="outside")
        fig_offense.update_layout(xaxis_title="", yaxis_title="")

        st.plotly_chart(fig_offense, use_container_width=True)

        # ---------------- Scatter: Freq vs PPT ----------------
        st.subheader("Relación frecuencia vs eficiencia (PPT)")

        freq_pps_pairs = [
            ("RIM FREQ", "RIM PPT", "RIM"),
            ("PAINT FREQ", "PAINT PPT", "PAINT"),
            ("MID FREQ", "MID PPT", "MID"),
            ("C3 FREQ", "C3 PPT", "C3"),
            ("L3 FREQ", "L3 PPT", "L3"),
        ]

        scatter_data = []

        def estimate_attempts(row, zone):
            """Estimación de intentos según zona."""
            if zone == "C3":
                return round(row["3PTA"] * row["C3 FREQ"], 2)
            elif zone == "L3":
                return round(row["3PTA"] * row["L3 FREQ"], 2)
            else:
                return round(row["FGA"] * row[f"{zone} FREQ"], 2)

        # Jugadores
        for _, row in df_players.iterrows():
            for freq_col, pps_col, label in freq_pps_pairs:
                scatter_data.append({
                    "Nombre": row["Nombre"],
                    "Zone": label,
                    "Frequency": row[freq_col],
                    "PPT": row[pps_col],
                    "Attempts": estimate_attempts(row, label)
                })

        # Media Liga
        if show_league and df_league is not None:
            league_row = df_league.iloc[0]
            for freq_col, pps_col, label in freq_pps_pairs:
                scatter_data.append({
                    "Nombre": "Media Liga",
                    "Zone": label,
                    "Frequency": league_row[freq_col],
                    "PPT": league_row[pps_col],
                    "Attempts": estimate_attempts(league_row, label)
                })

        df_freq_pps = pd.DataFrame(scatter_data)

        fig_freq_pps = px.scatter(
            df_freq_pps,
            x="Frequency",
            y="PPT",
            size="Attempts",
            color="Zone",
            symbol="Nombre",
            hover_data=["Nombre", "Attempts"],
        )

        fig_freq_pps.update_layout(
            xaxis_title="Frecuencia de tiro (%)",
            yaxis_title="Puntos por tiro (PPT)"
        )

        st.plotly_chart(fig_freq_pps, use_container_width=True)

        # ---------------- Pie Chart: Distribución de tiro ----------------
        st.subheader("Distribución de tiro")

        freq_cols = ["RIM FREQ", "PAINT FREQ", "MID FREQ", "C3 FREQ", "L3 FREQ"]

        # Ordenamos las columnas de frecuencia según los datos del jugador1 de mayor a menor
        freq_cols = sorted(freq_cols, key=lambda col: df_players.iloc[0][col], reverse=True)

        # Crear lista de figuras (jugadores + media liga si aplica)
        pie_figs = []
        for _, row in df_players.iterrows():
            fig_pie = px.pie(
                names=freq_cols,
                values=[row[c] for c in freq_cols],
                title=f"{row['Nombre']}",
                color=freq_cols
            )
            pie_figs.append(fig_pie)

        if show_league and df_league is not None:
            league_row = df_league.iloc[0]
            fig_pie_league = px.pie(
                names=freq_cols,
                values=[league_row[c] for c in freq_cols],
                title="Media Liga",
                color=freq_cols
            )
            pie_figs.append(fig_pie_league)

        # Mostrar en columnas (2 o 3 según corresponda)
        n = len(pie_figs)
        if n == 1:
            st.plotly_chart(pie_figs[0], use_container_width=True)
        elif n == 2:
            col1, col2 = st.columns(2)
            with col1: st.plotly_chart(pie_figs[0], use_container_width=True)
            with col2: st.plotly_chart(pie_figs[1], use_container_width=True)
        elif n == 3:
            col1, col2, col3 = st.columns(3)
            with col1: st.plotly_chart(pie_figs[0], use_container_width=True)
            with col2: st.plotly_chart(pie_figs[1], use_container_width=True)
            with col3: st.plotly_chart(pie_figs[2], use_container_width=True)

        # ---------------- Bar Chart: Otros ----------------
        st.subheader("Otros")

        col1, col2 = st.columns(2)
        with col1:
            df_bar = df_players[["Nombre", "BLKA"]].copy()
            if show_league and df_league is not None:
                df_bar = pd.concat([
                    df_bar,
                    pd.DataFrame({"Nombre": ["Media Liga"], "BLKA": [df_league.iloc[0]["BLKA"]]})
                ])

            df_bar['BLKA_formatted'] = df_bar['BLKA'].round(2).astype(str)
            fig_bar = px.bar(df_bar, x="Nombre", y="BLKA", text="BLKA_formatted", color="Nombre")
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(xaxis_title="BLKA", yaxis_title="")
            st.plotly_chart(fig_bar)

        with col2:
            df_bar = df_players[["Nombre", "FT Rate"]].copy()
            if show_league and df_league is not None:
                df_bar = pd.concat([
                    df_bar,
                    pd.DataFrame({"Nombre": ["Media Liga"], "FT Rate": [df_league.iloc[0]["FT Rate"]]})
                ])

            df_bar['FT_Rate_formatted'] = df_bar['FT Rate'].round(2).astype(str)
            fig_bar = px.bar(df_bar, x="Nombre", y="FT Rate", text="FT_Rate_formatted", color="Nombre")
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(xaxis_title="FT Rate", yaxis_title="")
            st.plotly_chart(fig_bar)

            
        ##################################### TAB 3 #####################################
    with tab3:
        st.subheader("Uso (USG) y creación")

        # --- Barras: USG%, POSS y PPP ---
        col1, col2 = st.columns(2)
        with col1:
            stats_usg = ["USG%", "POSS", "PPP"]
            df_usg = df_players[["Nombre"] + stats_usg].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_usg]
                df_usg = pd.concat([
                    df_usg,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_usg_long = df_usg.melt(id_vars="Nombre", value_vars=stats_usg,
                                         var_name="Stat", value_name="Value")
            
            df_usg_long['Value_formatted'] = df_usg_long['Value'].round(2).astype(str)
            fig_usg = px.bar(df_usg_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_usg.update_traces(textposition="outside")
            fig_usg.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_usg, use_container_width=True)

        # --- Barras: AST, TO y AST/TO ---
        with col2:
            stats_play = ["AST", "TO", "AST/TO"]
            df_play = df_players[["Nombre"] + stats_play].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_play]
                df_play = pd.concat([
                    df_play,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_play_long = df_play.melt(id_vars="Nombre", value_vars=stats_play,
                                         var_name="Stat", value_name="Value")
            
            df_play_long['Value_formatted'] = df_play_long['Value'].round(2).astype(str)
            fig_play = px.bar(df_play_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_play.update_traces(textposition="outside")
            fig_play.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_play, use_container_width=True)

        # --- Scatter: AST% vs TO% (tamaño por MIN) ---
        st.subheader("Eficiencia de creación: AST% vs TO%")
        scatter_rows = []
        for _, row in df_players.iterrows():
            scatter_rows.append({
                "Nombre": row["Nombre"], "AST%": row["AST%"], "TO%": row["TO%"], "MIN": row["MIN"]
            })
        if show_league and df_league is not None:
            r = df_league.iloc[0]
            scatter_rows.append({"Nombre": "Media Liga", "AST%": r["AST%"], "TO%": r["TO%"], "MIN": r["MIN"]})
        df_ast_to = pd.DataFrame(scatter_rows)
        fig_ast_to = px.scatter(df_ast_to, x="TO%", y="AST%", size="MIN", color="Nombre", hover_data=["MIN"], symbol="Nombre")
        fig_ast_to.update_layout(xaxis_title="TO%", yaxis_title="AST%")

        # Líneas de referencia
        if show_league and df_league is not None:
            fig_ast_to.add_shape(
                type="line", x0=r["TO%"], x1=r["TO%"],
                y0=df_ast_to["AST%"].min()-5, y1=df_ast_to["AST%"].max()+5,
                line=dict(dash="dash", color="gray")
            )
            fig_ast_to.add_shape(
                type="line", y0=r["AST%"], y1=r["AST%"],
                x0=df_ast_to["TO%"].min()-5, x1=df_ast_to["TO%"].max()+5,
                line=dict(dash="dash", color="gray")
            )

        st.plotly_chart(fig_ast_to, use_container_width=True)

        # --- Barras apiladas: distribución de asistencias por tipo de acción ---
        st.subheader("Distribución de asistencias (2P / 3P / FT)")
        parts = ["AST% (2P)", "AST% (3P)", "AST% (FT)"]
        df_ast_parts = df_players[["Nombre"] + parts].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][parts]
            df_ast_parts = pd.concat([
                df_ast_parts,
                pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
            ])
        df_ast_parts_long = df_ast_parts.melt(id_vars="Nombre", value_vars=parts,
                                             var_name="Tipo", value_name="Valor")
        
        df_ast_parts_long['Valor_formatted'] = df_ast_parts_long['Valor'].round(2).astype(str)
        fig_ast_parts = px.bar(df_ast_parts_long, x="Nombre", y="Valor", color="Tipo", barmode="stack", text="Valor_formatted")
        fig_ast_parts.update_traces(textposition="outside")
        fig_ast_parts.update_layout(xaxis_title="AST%", yaxis_title="")
        st.plotly_chart(fig_ast_parts, use_container_width=True)

        # --- Barras: Control de pérdidas ---
        st.subheader("Control de pérdidas")
        col1, col2 = st.columns(2)
        with col1:
            stats_to = ["TO%", "LTO%", "DTO%"]
            df_to = df_players[["Nombre"] + stats_to].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_to]
                df_to = pd.concat([
                    df_to,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_to_long = df_to.melt(id_vars="Nombre", value_vars=stats_to,
                                         var_name="Stat", value_name="Value")
            
            df_to_long['Value_formatted'] = df_to_long['Value'].round(2).astype(str)
            fig_to = px.bar(df_to_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_to.update_traces(textposition="outside")
            fig_to.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_to, use_container_width=True)
        with col2:
            stats_ratio = ["AST Ratio", "AST/TO"]
            df_ratio = df_players[["Nombre"] + stats_ratio].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_ratio]
                df_ratio = pd.concat([
                    df_ratio,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_ratio_long = df_ratio.melt(id_vars="Nombre", value_vars=stats_ratio,
                                             var_name="Stat", value_name="Value")
            
            df_ratio_long['Value_formatted'] = df_ratio_long['Value'].round(2).astype(str)
            fig_ratio = px.bar(df_ratio_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_ratio.update_traces(textposition="outside")
            fig_ratio.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_ratio, use_container_width=True)

    ##################################### TAB 4 #####################################
    with tab4:
        st.subheader("Rebote")

        # --- Barras:  OR/DR/TR ---
        col1, col2 = st.columns(2)
        with col1:
            stats_reb = ["OR", "DR", "TR"]
            df_reb = df_players[["Nombre"] + stats_reb].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_reb]
                df_reb = pd.concat([
                    df_reb,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_reb_long = df_reb.melt(id_vars="Nombre", value_vars=stats_reb,
                                         var_name="Stat", value_name="Value")
            
            df_reb_long['Value_formatted'] = df_reb_long['Value'].round(2).astype(str)
            fig_reb = px.bar(df_reb_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_reb.update_traces(textposition="outside")
            fig_reb.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_reb, use_container_width=True)

        # --- Barras: porcentajes de rebote OR%/DR%/TR% ---
        with col2:
            stats_reb_pct = ["OR%", "DR%", "TR%"]
            df_reb_pct = df_players[["Nombre"] + stats_reb_pct].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_reb_pct]
                df_reb_pct = pd.concat([
                    df_reb_pct,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_reb_pct_long = df_reb_pct.melt(id_vars="Nombre", value_vars=stats_reb_pct,
                                             var_name="Stat", value_name="Value")
            
            df_reb_pct_long['Value_formatted'] = df_reb_pct_long['Value'].round(2).astype(str)
            fig_reb_pct = px.bar(df_reb_pct_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_reb_pct.update_traces(textposition="outside")
            fig_reb_pct.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_reb_pct, use_container_width=True)

        # --- Rebote según tipo de tiro ---
        st.subheader("Rebote por contexto de tiro")
        col1, col2 = st.columns(2)
        with col1:
            or_after = ["OR% (after 2P)", "OR% (after 3P)", "OR% (after FT)"]
            df_or_after = df_players[["Nombre"] + or_after].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][or_after]
                df_or_after = pd.concat([
                    df_or_after,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_or_after_long = df_or_after.melt(id_vars="Nombre", value_vars=or_after,
                                                 var_name="Contexto", value_name="Valor")
            
            df_or_after_long['Valor_formatted'] = df_or_after_long['Valor'].round(2).astype(str)
            fig_or_after = px.bar(df_or_after_long, x="Contexto", y="Valor", color="Nombre", barmode="group", text="Valor_formatted")
            fig_or_after.update_traces(textposition="outside")
            fig_or_after.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_or_after, use_container_width=True)

        with col2:
            dr_after = ["DR% (after 2P)", "DR% (after 3P)", "DR% (after FT)"]
            df_dr_after = df_players[["Nombre"] + dr_after].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][dr_after]
                df_dr_after = pd.concat([
                    df_dr_after,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_dr_after_long = df_dr_after.melt(id_vars="Nombre", value_vars=dr_after,
                                                 var_name="Contexto", value_name="Valor")
            
            df_dr_after_long['Valor_formatted'] = df_dr_after_long['Valor'].round(2).astype(str)
            fig_dr_after = px.bar(df_dr_after_long, x="Contexto", y="Valor", color="Nombre", barmode="group", text="Valor_formatted")
            fig_dr_after.update_traces(textposition="outside")
            fig_dr_after.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_dr_after, use_container_width=True)

    ##################################### TAB 5 #####################################
    with tab5:
        st.subheader("Robos y tapones")

        col1, col2 = st.columns(2)
        # --- Barras: robos y tapones (volumen) ---
        with col1:
            stats_def = ["ST", "BLK"]
            df_def = df_players[["Nombre"] + stats_def].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_def]
                df_def = pd.concat([
                    df_def,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_def_long = df_def.melt(id_vars="Nombre", value_vars=stats_def,
                                         var_name="Stat", value_name="Value")
            
            df_def_long['Value_formatted'] = df_def_long['Value'].round(2).astype(str)
            fig_def = px.bar(df_def_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_def.update_traces(textposition="outside")
            fig_def.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_def, use_container_width=True)

        # --- Barras: ST% y BLK% ---
        with col2:
            stats_def_pct = ["ST%", "BLK%"]
            df_def_pct = df_players[["Nombre"] + stats_def_pct].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_def_pct]
                df_def_pct = pd.concat([
                    df_def_pct,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_def_pct_long = df_def_pct.melt(id_vars="Nombre", value_vars=stats_def_pct,
                                             var_name="Stat", value_name="Value")
            
            df_def_pct_long['Value_formatted'] = df_def_pct_long['Value'].round(2).astype(str)
            fig_def_pct = px.bar(df_def_pct_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_def_pct.update_traces(textposition="outside")
            fig_def_pct.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_def_pct, use_container_width=True)

        # --- Barras: BLK% por 2P vs 3P ---
        st.subheader("Detallando los tapones")
        stats_blk_split = ["BLK% (2P)", "BLK% (3P)"]
        df_blk_split = df_players[["Nombre"] + stats_blk_split].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][stats_blk_split]
            df_blk_split = pd.concat([
                df_blk_split,
                pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
            ])
        df_blk_split_long = df_blk_split.melt(id_vars="Nombre", value_vars=stats_blk_split,
                                             var_name="Contexto", value_name="Valor")
        
        df_blk_split_long['Valor_formatted'] = df_blk_split_long['Valor'].round(2).astype(str)
        fig_blk_split = px.bar(df_blk_split_long, x="Contexto", y="Valor", color="Nombre", barmode="group", text="Valor_formatted")
        fig_blk_split.update_traces(textposition="outside")
        fig_blk_split.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_blk_split, use_container_width=True)

        # --- Faltas por 100 posesiones ---
        st.subheader("Disciplina defensiva")
        stats_pf = ["PF 100 Poss", "DF 100 Poss"]
        df_pf = df_players[["Nombre"] + stats_pf].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][stats_pf]
            df_pf = pd.concat([
                df_pf,
                pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
            ])
        df_pf_long = df_pf.melt(id_vars="Nombre", value_vars=stats_pf,
                                 var_name="Stat", value_name="Value")
        
        df_pf_long['Value_formatted'] = df_pf_long['Value'].round(2).astype(str)
        fig_pf = px.bar(df_pf_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
        fig_pf.update_traces(textposition="outside")
        fig_pf.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_pf, use_container_width=True)

        # --- Scatter: presión al tiro rival (OPP TS%) vs generación de pérdidas (OPP TO%) ---
        st.subheader("Impacto sobre el rival (ON)")
        sc_rows = []
        for _, row in df_players.iterrows():
            sc_rows.append({
                "Nombre": row["Nombre"],
                "OPP TS% (ON)": row["OPP TS% (ON)"],
                "OPP TO% (ON)": row["OPP TO% (ON)"],
                "MIN": row["MIN"]
            })
        if show_league and df_league is not None:
            r = df_league.iloc[0]
            sc_rows.append({
                "Nombre": "Media Liga",
                "OPP TS% (ON)": r["OPP TS% (ON)"],
                "OPP TO% (ON)": r["OPP TO% (ON)"],
                "MIN": r["MIN"]
            })
        df_def_sc = pd.DataFrame(sc_rows)
        fig_def_sc = px.scatter(df_def_sc, x="OPP TS% (ON)", y="OPP TO% (ON)", size="MIN",
                                 color="Nombre", hover_data=["MIN"], symbol="Nombre")
        fig_def_sc.update_layout(xaxis_title="OPP TS% (ON)", yaxis_title="OPP TO% (ON)")

        st.plotly_chart(fig_def_sc, use_container_width=True)

    ##################################### TAB 6 #####################################
    with tab6:
        st.subheader("Impacto & Avanzadas")

        # --- Métricas individuales de eficiencia ---
        col1, col2 = st.columns(2)
        with col1:
            stats_ind = ["IND OFF RTG", "IND DEF RTG", "IND NET RTG"]
            df_ind = df_players[["Nombre"] + stats_ind].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_ind]
                df_ind = pd.concat([
                    df_ind,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_ind_long = df_ind.melt(id_vars="Nombre", value_vars=stats_ind,
                                         var_name="Stat", value_name="Value")
            
            df_ind_long['Value_formatted'] = df_ind_long['Value'].round(2).astype(str)
            fig_ind = px.bar(df_ind_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_ind.update_traces(textposition="outside")
            fig_ind.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_ind, use_container_width=True)

        # --- Métricas compuestas (BPM, VORP) ---
        with col2:
            stats_adv = ["OBPM", "DBPM", "BPM", "VORP"]
            df_adv = df_players[["Nombre"] + stats_adv].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_adv]
                df_adv = pd.concat([
                    df_adv,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_adv_long = df_adv.melt(id_vars="Nombre", value_vars=stats_adv,
                                         var_name="Stat", value_name="Value")
            
            df_adv_long['Value_formatted'] = df_adv_long['Value'].round(2).astype(str)
            fig_adv = px.bar(df_adv_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_adv.update_traces(textposition="outside")
            fig_adv.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_adv, use_container_width=True)

        # --- Individual Ratings ---
        st.subheader("Ratings individuales OFF vs DEF")
        df_rt = df_players[["Nombre", "IND OFF RTG", "IND DEF RTG", "IND NET RTG"]].copy()

        # Calcular referencia
        if show_league and df_league is not None:
            r = df_league.iloc[0][["IND OFF RTG", "IND DEF RTG", "IND NET RTG"]]
            x_ref, y_ref = r["IND OFF RTG"], r["IND DEF RTG"]
            # Añadimos Media Liga como equipo ficticio
            df_rt = pd.concat([
                df_rt,
                pd.DataFrame([{
                    "Nombre": "Media Liga",
                    "IND OFF RTG": x_ref,
                    "IND DEF RTG": y_ref,
                    "IND NET RTG": r["IND NET RTG"]
                }])
            ])
        else:
            x_ref, y_ref = df_rt["IND OFF RTG"].mean(), df_rt["IND DEF RTG"].mean()
        
        # Scatter
        fig_quad = px.scatter(
            df_rt,
            x="IND OFF RTG",
            y="IND DEF RTG",
            color="Nombre",
            symbol="Nombre",
            hover_data=["IND NET RTG"]
        )

        fig_quad.update_traces(marker=dict(size=14))

        # Líneas de referencia
        fig_quad.add_shape(
            type="line", x0=x_ref, x1=x_ref,
            y0=df_rt["IND DEF RTG"].min()-5, y1=df_rt["IND DEF RTG"].max()+5,
            line=dict(dash="dash", color="gray")
        )
        fig_quad.add_shape(
            type="line", y0=y_ref, y1=y_ref,
            x0=df_rt["IND OFF RTG"].min()-5, x1=df_rt["IND OFF RTG"].max()+5,
            line=dict(dash="dash", color="gray")
        )

        fig_quad.update_layout(
            xaxis_title="IND OFF RTG (más alto, mejor)",
            yaxis_title="IND DEF RTG (más bajo, mejor)"
        )

        st.plotly_chart(fig_quad, use_container_width=True)

        # --- Win Shares ---
        st.subheader("Win Shares")
        ws_stats = ["OFF WIN SHARE", "DEF WIN SHARE", "WIN SHARE", "WIN Share per 40"]
        df_ws = df_players[["Nombre"] + ws_stats].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][ws_stats]
            df_ws = pd.concat([
                df_ws,
                pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
            ])
        df_ws_long = df_ws.melt(id_vars="Nombre", value_vars=ws_stats,
                                 var_name="Stat", value_name="Value")
        
        df_ws_long['Value_formatted'] = df_ws_long['Value'].round(2).astype(str)
        fig_ws = px.bar(df_ws_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
        fig_ws.update_traces(textposition="outside")
        fig_ws.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_ws, use_container_width=True)

        # --- On/Off de equipo ---
        st.subheader("Contexto de equipo (ON vs OFF)")
        # OFF Rating
        cols = st.columns(2) 
        for i, (title, on_col, off_col) in enumerate([
            ("TM OFF RTG", "TM OFF RTG (ON)", "TM OFF RTG (OFF)"),
            ("TM DEF RTG", "TM DEF RTG (ON)", "TM DEF RTG (OFF)"),
        ]):
            rows = []
            for _, row in df_players.iterrows():
                rows.append({"Nombre": row["Nombre"], "Estado": "ON", "Valor": row[on_col], "Métrica": title})
                rows.append({"Nombre": row["Nombre"], "Estado": "OFF", "Valor": row[off_col], "Métrica": title})
            if show_league and df_league is not None:
                r = df_league.iloc[0]
                rows.append({"Nombre": "Media Liga", "Estado": "ON", "Valor": r[on_col], "Métrica": title})
                rows.append({"Nombre": "Media Liga", "Estado": "OFF", "Valor": r[off_col], "Métrica": title})

            df_onoff = pd.DataFrame(rows)
            fig_onoff = px.line(df_onoff, x="Estado", y="Valor", color="Nombre", markers=True)
            fig_onoff.update_layout(title=title, xaxis_title="", yaxis_title="")

            cols[i].plotly_chart(fig_onoff, use_container_width=True)

        for title, on_col, off_col in [
            ("TM NET RTG", "TM NET RTG (ON)", "TM NET RTG (OFF)"),
        ]:
            rows = []
            for _, row in df_players.iterrows():
                rows.append({"Nombre": row["Nombre"], "Estado": "ON", "Valor": row[on_col], "Métrica": title})
                rows.append({"Nombre": row["Nombre"], "Estado": "OFF", "Valor": row[off_col], "Métrica": title})
            if show_league and df_league is not None:
                r = df_league.iloc[0]
                rows.append({"Nombre": "Media Liga", "Estado": "ON", "Valor": r[on_col], "Métrica": title})
                rows.append({"Nombre": "Media Liga", "Estado": "OFF", "Valor": r[off_col], "Métrica": title})
            df_onoff = pd.DataFrame(rows)
            fig_onoff = px.line(df_onoff, x="Estado", y="Valor", color="Nombre", markers=True)
            fig_onoff.update_layout(title=title, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_onoff, use_container_width=True)

        # --- NET Team y diferenciales ---
        col1, col2 = st.columns(2)
        with col1:
            # NET con jugador ON/OFF + diferencial NET
            net_stats = ["TM NET RTG (ON)", "TM NET RTG (OFF)", "TM NET RTG (NET)"]
            df_net = df_players[["Nombre"] + net_stats].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][net_stats]
                df_net = pd.concat([
                    df_net,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_net_long = df_net.melt(id_vars="Nombre", value_vars=net_stats,
                                         var_name="Stat", value_name="Value")
            
            df_net_long['Value_formatted'] = df_net_long['Value'].round(2).astype(str)
            fig_net = px.bar(df_net_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_net.update_traces(textposition="outside")
            fig_net.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_net, use_container_width=True)

        with col2:
            # TS% y OR% y TO% del equipo con jugador ON vs OFF vs NET
            tm_stats = ["TM TS% (ON)", "TM TS% (OFF)", "TM TS% (NET)"]
            df_tm = df_players[["Nombre"] + tm_stats].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][tm_stats]
                df_tm = pd.concat([
                    df_tm,
                    pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
                ])
            df_tm_long = df_tm.melt(id_vars="Nombre", value_vars=tm_stats,
                                         var_name="Stat", value_name="Value")
            
            df_tm_long['Value_formatted'] = df_tm_long['Value'].round(2).astype(str)
            fig_tm = px.bar(df_tm_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
            fig_tm.update_traces(textposition="outside")
            fig_tm.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_tm, use_container_width=True)

        # --- Resumen rápido: PER, VAL y +/- ---
        st.subheader("Resumen rápido")
        quick_stats = ["PER", "VAL", "+/-"]
        df_quick = df_players[["Nombre"] + quick_stats].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][quick_stats]
            df_quick = pd.concat([
                df_quick,
                pd.DataFrame([{"Nombre": "Media Liga", **league_vals.to_dict()}])
            ])
        df_quick_long = df_quick.melt(id_vars="Nombre", value_vars=quick_stats,
                                         var_name="Stat", value_name="Value")
        
        df_quick_long['Value_formatted'] = df_quick_long['Value'].round(2).astype(str)
        fig_quick = px.bar(df_quick_long, x="Stat", y="Value", color="Nombre", barmode="group", text="Value_formatted")
        fig_quick.update_traces(textposition="outside")
        fig_quick.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_quick, use_container_width=True)