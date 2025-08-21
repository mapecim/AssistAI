import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional

from config import TEAM_MAP, TEAM_AVG_MAP

def can_show_league(avg_json: Optional[Dict], teams: List[Dict]) -> bool:
    if avg_json is None:
        return False
    seasons = {t.get("season_id") for t in teams}
    return len(seasons) == 1


def team_profile(team: Dict):
    col = st.columns(1)[0]
    col.metric("🏢 Equipo", team["tm_name"])

    col2, col3, col4, col5 = st.columns(4)
    col2.metric("🎮 Partidos", team["gp"])
    col3.metric("⏱️ Minutos", round(float(team["min"]), 2))
    col4.metric("🆚 Récord", f"{team['w']}W - {team['l']}L")
    col5.metric("📊 Win%", f"{(team['w'] / team['gp']) * 100:.1f}%")


def render_team_dashboard(data: Dict, avg_stats: Optional[Dict] = None):
    """
    Renderiza el dashboard completo con estadísticas y gráficos, adaptado para 1 o 2 equipos.
    """
    teams = data.get("team_stats", [])
    if not teams:
        st.warning("No hay datos disponibles para los equipos seleccionados.")
        return

    if avg_stats is not None:
        avg_stats = avg_stats["average_stats"]
        show_league = can_show_league(avg_stats, teams)
    else:
        show_league = False

    comparison = len(teams) == 2

    df_teams = pd.DataFrame(teams).rename(columns=TEAM_MAP)

    percentage_cols = [
        "2PT%", "3PT%", "FG%", "FT%", "eFG%", "TS%",
        "RIM FREQ", "PAINT FREQ", "MID FREQ", "C3 FREQ", "L3 FREQ", "FT Rate",
        "TO%", "LTO%", "DTO%", "AST%", "AST% (2P)", "AST% (3P)", "AST% (FT)", "AST Ratio",
        "OR%", "OR% (after 2P)", "OR% (after 3P)", "OR% (after FT)",
        "DR%", "DR% (after 2P)", "DR% (after 3P)", "DR% (after FT)", "TR%",
        "ST%", "BLK%"
    ]

    # Redondear columnas de porcentaje
    for col in percentage_cols:
        if col in df_teams.columns:
            df_teams[col] = df_teams[col].round(4).astype(float) * 100

    numeric_cols = df_teams.select_dtypes(include=np.number).columns
    non_percentage_cols = [c for c in numeric_cols if c not in percentage_cols]
    df_teams[non_percentage_cols] = df_teams[non_percentage_cols].round(2).astype(float)

    if comparison and (teams[0]["tm_name"] == teams[1]["tm_name"]):
        df_teams["Equipo"] = df_teams["Equipo"] + " - " + df_teams["SEASON"].astype(str)

    if show_league:
        df_league = pd.DataFrame([avg_stats]).rename(columns=TEAM_AVG_MAP)
        for col in percentage_cols:
            if col in df_league.columns:
                df_league[col] = df_league[col].round(4).astype(float) * 100

        numeric_cols = df_league.select_dtypes(include=np.number).columns
        non_percentage_cols = [col for col in numeric_cols if col not in percentage_cols]
        df_league[non_percentage_cols] = df_league[non_percentage_cols].round(2).astype(float)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📌 Perfil",
        "🎯 Tiro",
        "🔄 Ritmo y creación",
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
        st.subheader("Perfil del equipo" if not comparison else "Perfil de equipos")
        for t in teams:
            with st.container(border=True):
                with fixed_expander(t["tm_name"] + " - " + t["season_id"]):
                    team_profile(t)

    ##################################### TAB 2 #####################################
    with tab2:
        st.subheader("Eficiencia de tiro")

        col1, col2 = st.columns(2)
        with col1:
            df_bar = df_teams[["Equipo", "PTS"]].copy()
            if show_league and df_league is not None:
                df_bar = pd.concat([
                    df_bar,
                    pd.DataFrame({"Equipo": ["Media Liga"], "PTS": [df_league.iloc[0]["PTS"]]})
                ])
            
            df_bar['PTS_formatted'] = df_bar['PTS'].round(2).astype(str)
            fig_bar = px.bar(df_bar, x="Equipo", y="PTS", text="PTS_formatted", color="Equipo")
            fig_bar.update_traces(textposition="outside", )
            fig_bar.update_layout(xaxis_title="PTS", yaxis_title="")
            st.plotly_chart(fig_bar)

        with col2:
            metrics = ["FG%", "2PT%", "3PT%", "FT%", "eFG%", "TS%"]

            fig_radar = go.Figure()

            # Jugadores
            for _, row in df_teams.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row[m] for m in metrics],
                    theta=metrics,
                    fill="toself",
                    name=row["Equipo"]
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

        df_offense = df_teams[["Equipo"] + stats].copy()

        if show_league and df_league is not None:
            league_row = df_league.iloc[0][stats]
            df_offense = pd.concat([
                df_offense,
                pd.DataFrame([{"Equipo": "Media Liga", **league_row.to_dict()}])
            ])

        df_offense_long = df_offense.melt(id_vars="Equipo", value_vars=stats,
                                         var_name="Stat", value_name="Value")
        
        df_offense_long['Value_formatted'] = df_offense_long['Value'].round(2).astype(str)
        fig_offense = px.bar(
            df_offense_long,
            x="Stat", y="Value",
            color="Equipo",
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
                return row["3PTA"] * row["C3 FREQ"]
            elif zone == "L3":
                return row["3PTA"] * row["L3 FREQ"]
            else:
                return row["FGA"] * row[f"{zone} FREQ"]

        # Jugadores
        for _, row in df_teams.iterrows():
            for freq_col, pps_col, label in freq_pps_pairs:
                scatter_data.append({
                    "Equipo": row["Equipo"],
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
                    "Equipo": "Media Liga",
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
            symbol="Equipo",
            hover_data=["Equipo", "Attempts"],
        )

        fig_freq_pps.update_layout(
            xaxis_title="Frecuencia de tiro (%)",
            yaxis_title="Puntos por tiro (PPT)"
        )

        st.plotly_chart(fig_freq_pps, use_container_width=True)

        # ---------------- Pie Chart: Frecuencias de tiro ----------------
        st.subheader("Distribución de tiro")

        freq_cols = ["RIM FREQ", "PAINT FREQ", "MID FREQ", "C3 FREQ", "L3 FREQ"]

        # Ordenamos las columnas de frecuencia según los datos del jugador1 de mayor a menor
        freq_cols = sorted(freq_cols, key=lambda col: df_teams.iloc[0][col], reverse=True)

        # Crear lista de figuras (jugadores + media liga si aplica)
        pie_figs = []
        for _, row in df_teams.iterrows():
            fig_pie = px.pie(
                names=freq_cols,
                values=[row[c] for c in freq_cols],
                title=f"{row['Equipo']}",
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

        # --- Barras: Shooting Chances normalizadas ---
        st.subheader("Oportunidades de tiro - Acciones (por 100 posesiones)")

        df_sc = df_teams[["Equipo", "Shooting Chances", "POSS"]].copy()
        df_sc["SC_per100"] = (df_sc["Shooting Chances"] / df_sc["POSS"]) * 100

        if show_league and df_league is not None:
            r = df_league.iloc[0]
            sc_league = (r["Shooting Chances"] / r["POSS"]) * 100
            df_sc = pd.concat([
                df_sc,
                pd.DataFrame([{"Equipo": "Media Liga", "Shooting Chances": r["Shooting Chances"], "POSS": r["POSS"], "SC_per100": sc_league}])
            ])

        df_sc["SC_fmt"] = df_sc["SC_per100"].round(2).astype(str)
        fig_sc = px.bar(df_sc, x="Equipo", y="SC_per100", text="SC_fmt", color="Equipo")
        fig_sc.update_traces(textposition="outside")
        fig_sc.update_layout(xaxis_title="SC por 100 posesiones", yaxis_title="")
        st.plotly_chart(fig_sc, use_container_width=True)

        # ----- Scatter volumen vs eficiencia -----
        st.subheader("Relación volumen de acciones vs eficiencia (eFG%)")

        scatter_rows = []
        for _, row in df_teams.iterrows():
            scatter_rows.append({
                "Equipo": row["Equipo"], "SC per 100": (row["Shooting Chances"]/row["POSS"])*100, "eFG%": row["eFG%"], "FGA": row["FGA"]
            })
        if show_league and df_league is not None:
            r = df_league.iloc[0]
            scatter_rows.append({"Equipo": "Media Liga", "SC per 100": (r["Shooting Chances"]/r["POSS"])*100, "eFG%": r["eFG%"], "FGA": r["FGA"]})
        df_ast_to = pd.DataFrame(scatter_rows)
        fig_ast_to = px.scatter(df_ast_to, x="SC per 100", y="eFG%", size="FGA", color="Equipo", symbol="Equipo")
        fig_ast_to.update_layout(xaxis_title="SC por 100 posesiones", yaxis_title="eFG%")
        st.plotly_chart(fig_ast_to, use_container_width=True)

        # ---------------- Bar Chart: Otros ----------------
        st.subheader("Otros")

        col1, col2 = st.columns(2)
        with col1:
            df_bar = df_teams[["Equipo", "BLKA"]].copy()
            if show_league and df_league is not None:
                df_bar = pd.concat([
                    df_bar,
                    pd.DataFrame({"Equipo": ["Media Liga"], "BLKA": [df_league.iloc[0]["BLKA"]]})
                ])

            df_bar['BLKA_formatted'] = df_bar['BLKA'].round(2).astype(str)
            fig_bar = px.bar(df_bar, x="Equipo", y="BLKA", text="BLKA_formatted", color="Equipo")
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(xaxis_title="BLKA", yaxis_title="")
            st.plotly_chart(fig_bar)

        with col2:
            df_bar = df_teams[["Equipo", "FT Rate"]].copy()
            if show_league and df_league is not None:
                df_bar = pd.concat([
                    df_bar,
                    pd.DataFrame({"Equipo": ["Media Liga"], "FT Rate": [df_league.iloc[0]["FT Rate"]]})
                ])

            df_bar['FT_Rate_formatted'] = df_bar['FT Rate'].round(2).astype(str)
            fig_bar = px.bar(df_bar, x="Equipo", y="FT Rate", text="FT_Rate_formatted", color="Equipo")
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(xaxis_title="FT Rate", yaxis_title="")
            st.plotly_chart(fig_bar)

            
        ##################################### TAB 3 #####################################
    with tab3:
        st.subheader("Ritmo y creación")

        # --- Barras: PACE y POSS ---
        col1, col2 = st.columns(2)
        with col1:
            stats_usg = ["Pace", "POSS"]
            df_usg = df_teams[["Equipo"] + stats_usg].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_usg]
                df_usg = pd.concat([
                    df_usg,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_usg_long = df_usg.melt(id_vars="Equipo", value_vars=stats_usg,
                                         var_name="Stat", value_name="Value")
            
            df_usg_long['Value_formatted'] = df_usg_long['Value'].round(2).astype(str)
            fig_usg = px.bar(df_usg_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_usg.update_traces(textposition="outside")
            fig_usg.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_usg, use_container_width=True)
            st.write("")

        # --- Barras: AST, TO y AST/TO ---
        with col2:
            stats_play = ["AST", "TO", "AST/TO"]
            df_play = df_teams[["Equipo"] + stats_play].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_play]
                df_play = pd.concat([
                    df_play,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_play_long = df_play.melt(id_vars="Equipo", value_vars=stats_play,
                                         var_name="Stat", value_name="Value")
            
            df_play_long['Value_formatted'] = df_play_long['Value'].round(2).astype(str)
            fig_play = px.bar(df_play_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_play.update_traces(textposition="outside")
            fig_play.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_play, use_container_width=True)

        # Barras agrupadas: OFF PPP vs DEF PPP
        st.subheader("Eficiencia por posesión (PPP)")
        ppp_stats = ["OFF PPP", "DEF PPP"]
        df_ppp = df_teams[["Equipo"] + ppp_stats].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][ppp_stats]
            df_ppp = pd.concat([df_ppp, pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])])

        df_ppp_long = df_ppp.melt(id_vars="Equipo", value_vars=ppp_stats, var_name="Métrica", value_name="Valor")
        df_ppp_long["Valor_fmt"] = df_ppp_long["Valor"].round(3).astype(str)
        fig_ppp = px.bar(df_ppp_long, x="Métrica", y="Valor", color="Equipo", barmode="group", text="Valor_fmt")
        fig_ppp.update_traces(textposition="outside")
        fig_ppp.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_ppp, use_container_width=True)

        # Scatter: Pace vs OFF PPP
        st.subheader("Relación Pace vs OFF PPP")
        scatter_rows = []
        for _, row in df_teams.iterrows():
            scatter_rows.append({
                "Equipo": row["Equipo"], "Pace": row["Pace"], "OFF PPP": row["OFF PPP"], "POSS": row["POSS"]
            })
        if show_league and df_league is not None:
            r = df_league.iloc[0]
            scatter_rows.append({"Equipo": "Media Liga", "Pace": r["Pace"], "OFF PPP": r["OFF PPP"], "POSS": r["POSS"]})
        df_ast_to = pd.DataFrame(scatter_rows)
        fig_ast_to = px.scatter(df_ast_to, x="Pace", y="OFF PPP", size="POSS", color="Equipo", symbol="Equipo")
        fig_ast_to.update_layout(xaxis_title="Pace", yaxis_title="OFF PPP")
        st.plotly_chart(fig_ast_to, use_container_width=True)

        # --- Scatter: AST% vs TO% ---
        st.subheader("Eficiencia de creación: AST% vs TO%")
        scatter_rows = []
        for _, row in df_teams.iterrows():
            scatter_rows.append({
                "Equipo": row["Equipo"], "AST%": row["AST%"], "TO%": row["TO%"], "MIN": row["MIN"]
            })
        if show_league and df_league is not None:
            r = df_league.iloc[0]
            scatter_rows.append({"Equipo": "Media Liga", "AST%": r["AST%"], "TO%": r["TO%"], "MIN": r["MIN"]})
        df_ast_to = pd.DataFrame(scatter_rows)
        fig_ast_to = px.scatter(df_ast_to, x="TO%", y="AST%", size="MIN", color="Equipo", symbol="Equipo")
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
        df_ast_parts = df_teams[["Equipo"] + parts].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][parts]
            df_ast_parts = pd.concat([
                df_ast_parts,
                pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
            ])
        df_ast_parts_long = df_ast_parts.melt(id_vars="Equipo", value_vars=parts,
                                             var_name="Tipo", value_name="Valor")
        
        df_ast_parts_long['Valor_formatted'] = df_ast_parts_long['Valor'].round(2).astype(str)
        fig_ast_parts = px.bar(df_ast_parts_long, x="Equipo", y="Valor", color="Tipo", barmode="stack", text="Valor_formatted")
        fig_ast_parts.update_traces(textposition="outside")
        fig_ast_parts.update_layout(xaxis_title="AST%", yaxis_title="")
        st.plotly_chart(fig_ast_parts, use_container_width=True)

        # --- Barras: Control de pérdidas ---
        st.subheader("Control de pérdidas")
        col1, col2 = st.columns(2)
        with col1:
            stats_to = ["TO%", "LTO%", "DTO%"]
            df_to = df_teams[["Equipo"] + stats_to].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_to]
                df_to = pd.concat([
                    df_to,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_to_long = df_to.melt(id_vars="Equipo", value_vars=stats_to,
                                         var_name="Stat", value_name="Value")
            
            df_to_long['Value_formatted'] = df_to_long['Value'].round(2).astype(str)
            fig_to = px.bar(df_to_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_to.update_traces(textposition="outside")
            fig_to.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_to, use_container_width=True)
        with col2:
            stats_ratio = ["AST Ratio", "AST/TO"]
            df_ratio = df_teams[["Equipo"] + stats_ratio].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_ratio]
                df_ratio = pd.concat([
                    df_ratio,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_ratio_long = df_ratio.melt(id_vars="Equipo", value_vars=stats_ratio,
                                             var_name="Stat", value_name="Value")
            
            df_ratio_long['Value_formatted'] = df_ratio_long['Value'].round(2).astype(str)
            fig_ratio = px.bar(df_ratio_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_ratio.update_traces(textposition="outside")
            fig_ratio.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_ratio, use_container_width=True)

    ##################################### TAB 4 #####################################
    with tab4:
        st.subheader("Rebote")

        # --- Barras: volumen de rebotes OR/DR/TR ---
        col1, col2 = st.columns(2)
        with col1:
            stats_reb = ["OR", "DR", "TR"]
            df_reb = df_teams[["Equipo"] + stats_reb].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_reb]
                df_reb = pd.concat([
                    df_reb,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_reb_long = df_reb.melt(id_vars="Equipo", value_vars=stats_reb,
                                         var_name="Stat", value_name="Value")
            
            df_reb_long['Value_formatted'] = df_reb_long['Value'].round(2).astype(str)
            fig_reb = px.bar(df_reb_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_reb.update_traces(textposition="outside")
            fig_reb.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_reb, use_container_width=True)

        # --- Barras: porcentajes de rebote OR%/DR%/TR% ---
        with col2:
            stats_reb_pct = ["OR%", "DR%", "TR%"]
            df_reb_pct = df_teams[["Equipo"] + stats_reb_pct].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_reb_pct]
                df_reb_pct = pd.concat([
                    df_reb_pct,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_reb_pct_long = df_reb_pct.melt(id_vars="Equipo", value_vars=stats_reb_pct,
                                             var_name="Stat", value_name="Value")
            
            df_reb_pct_long['Value_formatted'] = df_reb_pct_long['Value'].round(2).astype(str)
            fig_reb_pct = px.bar(df_reb_pct_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_reb_pct.update_traces(textposition="outside")
            fig_reb_pct.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_reb_pct, use_container_width=True)

        # --- Rebote ofensivo y defensivo según tipo de tiro ---
        st.subheader("Rebote por contexto de tiro")
        col1, col2 = st.columns(2)
        with col1:
            or_after = ["OR% (after 2P)", "OR% (after 3P)", "OR% (after FT)"]
            df_or_after = df_teams[["Equipo"] + or_after].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][or_after]
                df_or_after = pd.concat([
                    df_or_after,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_or_after_long = df_or_after.melt(id_vars="Equipo", value_vars=or_after,
                                                 var_name="Contexto", value_name="Valor")
            
            df_or_after_long['Valor_formatted'] = df_or_after_long['Valor'].round(2).astype(str)
            fig_or_after = px.bar(df_or_after_long, x="Contexto", y="Valor", color="Equipo", barmode="group", text="Valor_formatted")
            fig_or_after.update_traces(textposition="outside")
            fig_or_after.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_or_after, use_container_width=True)

        with col2:
            dr_after = ["DR% (after 2P)", "DR% (after 3P)", "DR% (after FT)"]
            df_dr_after = df_teams[["Equipo"] + dr_after].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][dr_after]
                df_dr_after = pd.concat([
                    df_dr_after,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_dr_after_long = df_dr_after.melt(id_vars="Equipo", value_vars=dr_after,
                                                 var_name="Contexto", value_name="Valor")
            
            df_dr_after_long['Valor_formatted'] = df_dr_after_long['Valor'].round(2).astype(str)
            fig_dr_after = px.bar(df_dr_after_long, x="Contexto", y="Valor", color="Equipo", barmode="group", text="Valor_formatted")
            fig_dr_after.update_traces(textposition="outside")
            fig_dr_after.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_dr_after, use_container_width=True)

    ##################################### TAB 5 #####################################
    with tab5:
        st.subheader("Robos, tapones y kills")

        col1, col2 = st.columns(2)
        # --- Barras: robos, tapones y kills (volumen) ---
        with col1:
            stats_def = ["ST", "BLK", "Kills"]
            df_def = df_teams[["Equipo"] + stats_def].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_def]
                df_def = pd.concat([
                    df_def,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_def_long = df_def.melt(id_vars="Equipo", value_vars=stats_def,
                                         var_name="Stat", value_name="Value")
            
            df_def_long['Value_formatted'] = df_def_long['Value'].round(2).astype(str)
            fig_def = px.bar(df_def_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_def.update_traces(textposition="outside")
            fig_def.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_def, use_container_width=True)

        # --- Barras: ST% y BLK% ---
        with col2:
            stats_def_pct = ["ST%", "BLK%"]
            df_def_pct = df_teams[["Equipo"] + stats_def_pct].copy()
            if show_league and df_league is not None:
                league_vals = df_league.iloc[0][stats_def_pct]
                df_def_pct = pd.concat([
                    df_def_pct,
                    pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
                ])
            df_def_pct_long = df_def_pct.melt(id_vars="Equipo", value_vars=stats_def_pct,
                                             var_name="Stat", value_name="Value")
            
            df_def_pct_long['Value_formatted'] = df_def_pct_long['Value'].round(2).astype(str)
            fig_def_pct = px.bar(df_def_pct_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
            fig_def_pct.update_traces(textposition="outside")
            fig_def_pct.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_def_pct, use_container_width=True)

        # --- Barras: BLK% por 2P vs 3P ---
        st.subheader("Detallando los tapones")
        stats_blk_split = ["BLK% (2P)", "BLK% (3P)"]
        df_blk_split = df_teams[["Equipo"] + stats_blk_split].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][stats_blk_split]
            df_blk_split = pd.concat([
                df_blk_split,
                pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
            ])
        df_blk_split_long = df_blk_split.melt(id_vars="Equipo", value_vars=stats_blk_split,
                                             var_name="Contexto", value_name="Valor")
        
        df_blk_split_long['Valor_formatted'] = df_blk_split_long['Valor'].round(2).astype(str)
        fig_blk_split = px.bar(df_blk_split_long, x="Contexto", y="Valor", color="Equipo", barmode="group", text="Valor_formatted")
        fig_blk_split.update_traces(textposition="outside")
        fig_blk_split.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_blk_split, use_container_width=True)

        # --- Faltas ---
        st.subheader("Disciplina defensiva")
        stats_pf = ["PF", "DF"]
        df_pf = df_teams[["Equipo"] + stats_pf].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][stats_pf]
            df_pf = pd.concat([
                df_pf,
                pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
            ])
        df_pf_long = df_pf.melt(id_vars="Equipo", value_vars=stats_pf,
                                 var_name="Stat", value_name="Value")
        
        df_pf_long['Value_formatted'] = df_pf_long['Value'].round(2).astype(str)
        fig_pf = px.bar(df_pf_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
        fig_pf.update_traces(textposition="outside")
        fig_pf.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_pf, use_container_width=True)

        st.subheader("Faltas de tiro: forzadas vs concedidas")
        stats_psf = ["PSF FREQ", "DSF FREQ"]
        df_psf = df_teams[["Equipo"] + stats_psf].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][stats_psf]
            df_psf = pd.concat([df_psf, pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])])

        df_psf_long = df_psf.melt(id_vars="Equipo", value_vars=stats_psf, var_name="Tipo", value_name="Valor")
        df_psf_long["Valor_fmt"] = df_psf_long["Valor"].round(2).astype(str)
        fig_psf = px.bar(df_psf_long, x="Tipo", y="Valor", color="Equipo", barmode="group", text="Valor_fmt")
        fig_psf.update_traces(textposition="outside")
        fig_psf.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_psf, use_container_width=True)

        # -------- Contraste con FT Rate ofensivo ---------
        st.subheader("Faltas de tiro forzadas vs FT Rate")
        df_psf_rate = df_teams[["Equipo", "PSF FREQ", "FT Rate"]].copy()
        if show_league and df_league is not None:
            r = df_league.iloc[0]
            df_psf_rate = pd.concat([df_psf_rate, pd.DataFrame([{"Equipo":"Media Liga","PSF FREQ":r["PSF FREQ"],"FT Rate":r["FT Rate"]}])])

        fig_psf_rate = px.scatter(df_psf_rate, x="PSF FREQ", y="FT Rate", color="Equipo", symbol="Equipo")
        fig_psf_rate.update_traces(marker=dict(size=14))
        fig_psf_rate.update_layout(xaxis_title="PSF FREQ (%)", yaxis_title="FT Rate (%)")
        st.plotly_chart(fig_psf_rate, use_container_width=True)


    ##################################### TAB 6 #####################################
    with tab6:
        # ----------- Cuadrante OFF vs DEF Rating ----------
        st.subheader("OFF vs DEF Ratings")
        df_rt = df_teams[["Equipo", "OFF RTG", "DEF RTG", "NET RTG"]].copy()

        # Calcular referencia
        if show_league and df_league is not None:
            r = df_league.iloc[0][["OFF RTG", "DEF RTG", "NET RTG"]]
            x_ref, y_ref = r["OFF RTG"], r["DEF RTG"]
            # Añadimos Media Liga como equipo ficticio
            df_rt = pd.concat([
                df_rt,
                pd.DataFrame([{
                    "Equipo": "Media Liga",
                    "OFF RTG": x_ref,
                    "DEF RTG": y_ref,
                    "NET RTG": r["NET RTG"]
                }])
            ])
        else:
            x_ref, y_ref = df_rt["OFF RTG"].mean(), df_rt["DEF RTG"].mean()

        # Scatter
        fig_quad = px.scatter(
            df_rt,
            x="OFF RTG",
            y="DEF RTG",
            color="Equipo",
            symbol="Equipo",
            hover_data=["NET RTG"]
        )

        fig_quad.update_traces(marker=dict(size=14))

        fig_quad.update_traces(
            marker=dict(size=14),
            selector=dict(name="Media Liga")
        )

        # Líneas de referencia
        fig_quad.add_shape(
            type="line", x0=x_ref, x1=x_ref,
            y0=df_rt["DEF RTG"].min()-5, y1=df_rt["DEF RTG"].max()+5,
            line=dict(dash="dash", color="gray")
        )
        fig_quad.add_shape(
            type="line", y0=y_ref, y1=y_ref,
            x0=df_rt["OFF RTG"].min()-5, x1=df_rt["OFF RTG"].max()+5,
            line=dict(dash="dash", color="gray")
        )

        fig_quad.update_layout(
            xaxis_title="OFF RTG (más alto, mejor)",
            yaxis_title="DEF RTG (más bajo, mejor)"
        )

        st.plotly_chart(fig_quad, use_container_width=True)


        # ---------- Waterfall: OFF -> DEF -> NET (por equipo) ----------
        st.subheader("Descomposición del Net Rating (OFF suma, DEF resta).")
        wf_figs = []
        for _, row in df_rt.iterrows():
            fig_wf = go.Figure(go.Waterfall(
                x=["OFF RTG", "DEF RTG", "NET RTG"],
                measure=["relative", "relative", "total"],
                y=[row["OFF RTG"], -row["DEF RTG"], row["NET RTG"]],
                text=[f'{row["OFF RTG"]:.1f}', f'-{row["DEF RTG"]:.1f}', f'{row["NET RTG"]:.1f}'],
                textposition="auto",
                connector={"line": {"width": 1}}
            ))

            fig_wf.update_yaxes(automargin=True)
            fig_wf.update_layout(
                title=f"{row['Equipo']}",
                yaxis_title="Rating",
                margin=dict(t=60, b=60)
            )

            wf_figs.append(fig_wf)

        # Mostrar en columnas dinámicamente
        n = len(wf_figs)
        if n == 1:
            st.plotly_chart(wf_figs[0], use_container_width=True)
        elif n == 2:
            col1, col2 = st.columns(2)
            with col1: st.plotly_chart(wf_figs[0], use_container_width=True)
            with col2: st.plotly_chart(wf_figs[1], use_container_width=True)
        elif n == 3:
            col1, col2, col3 = st.columns(3)
            with col1: st.plotly_chart(wf_figs[0], use_container_width=True)
            with col2: st.plotly_chart(wf_figs[1], use_container_width=True)
            with col3: st.plotly_chart(wf_figs[2], use_container_width=True)


        # --- Resumen rápido: VAL y +/- ---
        st.subheader("Resumen rápido")
        quick_stats = ["VAL", "+/-"]
        df_quick = df_teams[["Equipo"] + quick_stats].copy()
        if show_league and df_league is not None:
            league_vals = df_league.iloc[0][quick_stats]
            df_quick = pd.concat([
                df_quick,
                pd.DataFrame([{"Equipo": "Media Liga", **league_vals.to_dict()}])
            ])
        df_quick_long = df_quick.melt(id_vars="Equipo", value_vars=quick_stats,
                                         var_name="Stat", value_name="Value")
        
        df_quick_long['Value_formatted'] = df_quick_long['Value'].round(2).astype(str)
        fig_quick = px.bar(df_quick_long, x="Stat", y="Value", color="Equipo", barmode="group", text="Value_formatted")
        fig_quick.update_traces(textposition="outside")
        fig_quick.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_quick, use_container_width=True)