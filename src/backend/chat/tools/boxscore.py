import re
import pandas as pd
from euroleague_api.boxscore_data import BoxScoreData
from crewai.tools import BaseTool

COL_MAP = {
    "Points": "PTS",
    "FieldGoalsMade2": "2PTM",
    "FieldGoalsAttempted2": "2PTA",
    "FieldGoalsMade3": "3PTM",
    "FieldGoalsAttempted3": "3PTA",
    "FreeThrowsMade": "FTM",
    "FreeThrowsAttempted": "FTA",
    "OffensiveRebounds": "OR",
    "DefensiveRebounds": "DR",
    "TotalRebounds": "TR",
    "Assistances": "AST",
    "Steals": "ST",
    "Turnovers": "TO",
    "BlocksFavour": "BLK",
    "BlocksAgainst": "BLKA",
    "FoulsCommited": "PF",
    "FoulsReceived": "DF",
    "Valuation": "VAL",
    "Plusminus": "+/-",
    "Minutes": "MIN"
}

def parse_url(url: str):
    """
    Extrae season y gamecode desde la URL de Euroleague.
    Ejemplo:
    https://www.euroleaguebasketball.net/es/euroleague/game-center/2023-24/real-madrid-panathinaikos-aktor-athens/E2023/333/
    -> season=2023, gamecode=333
    """
    match = re.search(r'/E(\d{4})/(\d{1,3})', url)
    if not match:
        raise ValueError(f"No se pudo parsear season y gamecode de la URL: {url}")
    season = int(match.group(1))
    gamecode = int(match.group(2))
    return season, gamecode

def compute_advanced_stats(row: pd.Series, opp_totals: pd.Series) -> pd.Series:
    """
    Calcula estadísticas avanzadas para una fila (jugador o totales).
    """
    try:
        # Extraer básicos
        pts = float(row.get("Points", row.get("PTS", 0)))
        fgm2 = float(row.get("FieldGoalsMade2", row.get("2PTM", 0))); fga2 = float(row.get("FieldGoalsAttempted2", row.get("2PTA", 0)))
        fgm3 = float(row.get("FieldGoalsMade3", row.get("3PTM", 0))); fga3 = float(row.get("FieldGoalsAttempted3", row.get("3PTA", 0)))
        ftm = float(row.get("FreeThrowsMade", row.get("FTM", 0))); fta = float(row.get("FreeThrowsAttempted", row.get("FTA", 0)))
        orb = float(row.get("OffensiveRebounds", row.get("OR", 0))); drb = float(row.get("DefensiveRebounds", row.get("DR", 0))); trb = float(row.get("TotalRebounds", row.get("TR", 0)))
        ast = float(row.get("Assistances", row.get("AST", 0))); tov = float(row.get("Turnovers", row.get("TO", 0))); stl = float(row.get("Steals", row.get("ST", 0)))
        blk = float(row.get("BlocksFavour", row.get("BLK", 0))); pf = float(row.get("FoulsCommited", row.get("PF", 0)))

        # Del rival (totales)
        opp_pts = float(opp_totals.get("Points", opp_totals.get("PTS", 0)))
        opp_fga2 = float(opp_totals.get("FieldGoalsAttempted2", opp_totals.get("2PTA", 0)))
        opp_fga3 = float(opp_totals.get("FieldGoalsAttempted3", opp_totals.get("3PTA", 0)))
        opp_fta = float(opp_totals.get("FreeThrowsAttempted", opp_totals.get("FTA", 0)))
        opp_to = float(opp_totals.get("Turnovers", opp_totals.get("TO", 0)))
        opp_or = float(opp_totals.get("OffensiveRebounds", opp_totals.get("OR", 0))); opp_dr = float(opp_totals.get("DefensiveRebounds", opp_totals.get("DR", 0))); opp_tr = float(opp_totals.get("TotalRebounds", opp_totals.get("TR", 0)))
        opp_tpa = float(opp_totals.get("FieldGoalsAttempted3", opp_totals.get("3PTA", 0))); opp_2pa = float(opp_totals.get("FieldGoalsAttempted2", opp_totals.get("2PTA", 0)))

        # Calcular fgm y fga
        fgm = fgm2 + fgm3
        fga = fga2 + fga3
        opp_fga = opp_fga2 + opp_fga3

        # Posesiones estimadas
        poss = fga + 0.44*fta - orb + tov
        opp_poss = opp_fga + 0.44*opp_fta - opp_or + opp_to
        poss = max(poss, 1)
        opp_poss = max(opp_poss, 1)

        # Advanced stats
        stats = {
            "2PT%": fgm2/fga2 if fga2 else 0,
            "3PT%": fgm3/fga3 if fga3 else 0,
            "FGM": fgm,
            "FGA": fga,
            "FG%": fgm/fga if fga else 0,
            "FT%": ftm/fta if fta else 0,
            "POSS": poss,
            "PPP": pts/poss,
            "ORTG": 100*pts/poss,
            "DRTG": 100*opp_pts/opp_poss if row["Player"] in ["TOTALS", "TEAM ADVANCED"] else float('NaN'),
            "NetRTG": (100*pts/poss) - (100*opp_pts/opp_poss) if row["Player"] in ["TOTALS", "TEAM ADVANCED"] else float('NaN'),
            "eFG%": (fgm + 0.5*fgm3)/fga if fga else 0,
            "TS%": pts / (2*(fga + 0.44*fta)) if (fga+0.44*fta) else 0,
            "FT Ratio": fta/fga if fga else 0,
            "TO%": tov/poss,
            "AST%": ast/fgm if fgm else 0,
            "AST/TO": ast/tov if tov else ast,
            "OR%": orb / (orb + opp_dr) if (orb+opp_dr) else 0,
            "DR%": drb / (drb + opp_or) if (drb+opp_or) else 0,
            "TR%": trb / (trb + opp_tr) if (trb+opp_tr) else 0,
            "ST%": stl/poss,
            "BLK%": blk / opp_2pa if opp_2pa else 0,
            "PF per 100 Poss": 100*pf/poss
        }
        return pd.Series(stats)
    except (TypeError, ValueError):
        # Manejar filas con datos no numéricos (e.g., 'DNP')
        return pd.Series({
            "POSS": float('NaN'),
            "PPP": float('NaN'),
            "ORTG": float('NaN'),
            "DRTG": float('NaN'),
            "NetRTG": float('NaN'),
            "eFG%": float('NaN'),
            "TS%": float('NaN'),
            "FT Ratio": float('NaN'),
            "TO%": float('NaN'),
            "AST%": float('NaN'),
            "AST/TO": float('NaN'),
            "OR%": float('NaN'),
            "DR%": float('NaN'),
            "TR%": float('NaN'),
            "ST%": float('NaN'),
            "BLK%": float('NaN'),
            "PF per 100 Poss": float('NaN')
        })


def get_boxscore_from_url(url: str):
    """
    A partir de una URL de Game Center, devuelve un DataFrame completo con
    estadísticas individuales y las estadísticas avanzadas del equipo.
    """
    season, gamecode = parse_url(url)
    raw = BoxScoreData().get_boxscore_data(season, gamecode, "Stats")

    if not isinstance(raw, list) or len(raw) < 2:
        raise ValueError("El boxscore no tiene el formato esperado (lista con dos equipos).")

    dfs = {}
    for item in raw:
        team_name = item.get("Team", "UNKNOWN").strip().upper()
        players = pd.DataFrame(item.get("PlayersStats", []))
        totals = pd.DataFrame([item.get("totr", {})])
        
        # Concatenar jugadores + fila de totales para un único DataFrame
        df_team = pd.concat([players, totals.assign(Player="TOTALS")], ignore_index=True)
        dfs[team_name] = df_team

    teams = list(dfs.keys())
    
    # Calcular totales del oponente
    opp_totals = {teams[i]: dfs[teams[1-i]][dfs[teams[1-i]]["Player"] == "TOTALS"].iloc[0] for i in range(2)}
    
    result_dfs = []
    for team_name, df_team in dfs.items():
        opp_total_row = opp_totals[team_name]
        
        advanced_stats_df = df_team.apply(lambda row: compute_advanced_stats(row, opp_total_row), axis=1)
        df_team = pd.concat([df_team, advanced_stats_df], axis=1)

        totals_row = df_team[df_team["Player"] == "TOTALS"].index[0]
        df_team = df_team[df_team["Minutes"] != "DNP"].reset_index(drop=True)
        
        df_team.insert(0, "TEAM TOTAL", team_name)
        result_dfs.append(df_team)

    final_df = pd.concat(result_dfs, ignore_index=True)

    final_df = final_df.rename(columns=COL_MAP)

    final_df = final_df.rename(columns={
        "TEAM TOTAL": "Team",
        "Team": "TeamCode",
        "Player_ID": "PlayerID"
    })

    # Convertir IsStarter a bool
    if "IsStarter" in final_df.columns:
        final_df["IsStarter"] = final_df["IsStarter"].astype(bool)

    final_df = final_df.drop(columns=["IsPlaying"], errors="ignore")

    # Reordenar columnas para que empiecen con el orden deseado
    column_order = [
        'Team', 'TeamCode', 'Dorsal', 'Player', 'IsStarter', 'MIN', 'PTS', '2PTM', '2PTA', '2PT%', '3PTM', '3PTA',
        '3PT%', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'OR', 'DR', 'TR', 'AST', 'TO', 'ST', 'BLK', 'BLKA',
        'PF', 'DF', 'VAL', '+/-', 'POSS', 'PPP', 'ORTG', 'DRTG', 'NetRTG', 'eFG%', 'TS%', 'FT Ratio', 'TO%',
        'AST%', 'AST/TO', 'OR%', 'DR%', 'TR%', 'ST%', 'BLK%', 'PF per 100 Poss'
    ]

    # Reordenar las columnas del DataFrame
    final_df = final_df.reindex(columns=column_order)

    return final_df.to_json()

class BoxScoreTool(BaseTool):
    name: str = "BoxScoreTool"
    description: str = "Returns advanced team boxscore stats given a Euroleague URL"

    def _run(self, url: str):
        return get_boxscore_from_url(url)