import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000"

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.sportradar.com/basketball/trial/v2"
LOCALE = "en"
LLM_MODEL = os.getenv("LLM_MODEL")

LEAGUE_URNS = {
    "Euroleague": "sr:competition:138",
    # "Eurocup": "sr:competition:141",
    # "Champions League": "sr:competition:14051",
    # "Liga ACB": "sr:competition:264",
    # "Copa del Rey": "sr:competition:396",
    # "Supercopa": "sr:competition:581",
    # "Primera FEB": "sr:competition:1514",
    # "Segunda FEB": "sr:competition:44949",
}

DB_CONFIG = {
    "dbname": "basketball_db",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost"
}

ADVANCED_DB_CONFIG = {
    "dbname": "advanced_basketball_db",
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost"
}

CSV_FILES = {
    '24_25_teams': os.path.join(os.path.dirname(__file__), 'etl/advanced/data/24-25_Teams.csv'),
    '24_25_players': os.path.join(os.path.dirname(__file__), 'etl/advanced/data/24-25_Players.csv'),
    '23_24_teams': os.path.join(os.path.dirname(__file__), 'etl/advanced/data/23-24_Teams.csv'),
    '23_24_players': os.path.join(os.path.dirname(__file__), 'etl/advanced/data/23-24_Players.csv'),
}

PLAYER_MAP = {
    # Perfil / básicas
   "name":"Nombre",
   "role":"ROLE",
   "nat":"NAT",
   "height":"HEIGHT",
   "age":"AGE",
   "tm_name":"TEAM NAME",
   "season_id":"SEASON",

   # Record temporada / minutos
   "gp":"GP",
   "min":"MIN",
   "w":"W",
   "l":"L",
   "w_pct":"W%",

   # Puntos + tiro
   "pts":"PTS",
   "two_ptm":"2PTM",
   "two_pta":"2PTA",
   "two_pt_pct":"2PT%",
   "three_ptm":"3PTM",
   "three_pta":"3PTA",
   "three_pt_pct":"3PT%",
   "fgm":"FGM",
   "fga":"FGA",
   "fg_pct":"FG%",
   "ftm":"FTM",
   "fta":"FTA",
   "ft_pct":"FT%",
   "blka":"BLKA",

   # Rebotes
   "or_rebounds":"OR",
   "dr_rebounds":"DR",
   "tr_rebounds":"TR",

   # Playmaking
   "ast":"AST",
   "tovers":"TO",

   # Defensa
   "st":"ST",
   "blk":"BLK",

   # Faltas
   "pf":"PF",
   "df":"DF",

   # General
   "val":"VAL",
   "plus_minus":"+/-",

   # AVANZADAS - Ritmo, uso y eficiencia
   "poss":"POSS",
   "usg_pct":"USG%",
   "ppp":"PPP",
   "off_rtg_on":"OFF RTG (ON)",
   "def_rtg_on":"DEF RTG (ON)",
   "net_rtg_on":"NET RTG (ON)",
   "ind_off_rtg":"IND OFF RTG",
   "ind_def_rtg":"IND DEF RTG",
   "ind_net_rtg":"IND NET RTG",
   "efg_pct":"eFG%",
   "ts_pct":"TS%",

   # AVANZADAS - Tiro (frecuencias y eficiencia)
   "rim_freq":"RIM FREQ",
   "rim_pps":"RIM PPT",
   "paint_freq":"PAINT FREQ",
   "paint_pps":"PAINT PPT",
   "mid_freq":"MID FREQ",
   "mid_pps":"MID PPT",
   "c3_freq":"C3 FREQ",
   "c3_pps":"C3 PPT",
   "l3_freq":"L3 FREQ",
   "l3_pps":"L3 PPT",
   "ft_ratio":"FT Rate",

   # AVANZADAS - Playmaking
   "to_pct":"TO%",
   "lto_pct":"LTO%",
   "dto_pct":"DTO%",
   "ast_pct":"AST%",
   "ast_pct_2p":"AST% (2P)",
   "ast_pct_3p":"AST% (3P)",
   "ast_pct_ft":"AST% (FT)",
   "ast_ratio":"AST Ratio",
   "ast_to_ratio":"AST/TO",

   # AVANZADAS - Rebotes
   "or_pct":"OR%",
   "or_pct_after_2p":"OR% (after 2P)",
   "or_pct_after_3p":"OR% (after 3P)",
   "or_pct_after_ft":"OR% (after FT)",
   "dr_pct":"DR%",
   "dr_pct_after_2p":"DR% (after 2P)",
   "dr_pct_after_3p":"DR% (after 3P)",
   "dr_pct_after_ft":"DR% (after FT)",
   "tr_pct":"TR%",

   # AVANZADAS - Defensa
   "st_pct":"ST%",
   "blk_pct":"BLK%",
   "blk_pct_2p":"BLK% (2P)",
   "blk_pct_3p":"BLK% (3P)",

   # AVANZADAS - Faltas
   "pf_100_poss":"PF 100 Poss",
   "df_100_poss":"DF 100 Poss",

   # AVANZADAS - Métricas avanzadas
   "per":"PER",
   "off_win_share":"OFF WIN SHARE",
   "def_win_share":"DEF WIN SHARE",
   "win_share":"WIN SHARE",
   "win_share_per_40":"WIN Share per 40",
   "obpm":"OBPM",
   "dbpm":"DBPM",
   "bpm":"BPM",
   "vorp":"VORP",

   # Equipo/Oponente - Jugador ON
   "tm_pace_on":"TM PACE (ON)",
   "tm_off_rtg_on":"TM OFF RTG (ON)",
   "tm_def_rtg_on":"TM DEF RTG (ON)",
   "tm_net_rtg_on":"TM NET RTG (ON)",
   "tm_ts_pct_on":"TM TS% (ON)",
   "tm_or_pct_on":"TM OR% (ON)",
   "tm_to_pct_on":"TM TO% (ON)",
   "tm_ft_ratio_on":"TM FT Rate (ON)",
   "opp_ts_pct_on":"OPP TS% (ON)",
   "opp_or_pct_on":"OPP OR% (ON)",
   "opp_to_pct_on":"OPP TO% (ON)",
   "opp_ft_ratio_on":"OPP FT Rate (ON)",

   # Equipo/Oponente - Jugador OFF
   "tm_pace_off":"TM PACE (OFF)",
   "tm_off_rtg_off":"TM OFF RTG (OFF)",
   "tm_def_rtg_off":"TM DEF RTG (OFF)",
   "tm_net_rtg_off":"TM NET RTG (OFF)",
   "tm_ts_pct_off":"TM TS% (OFF)",
   "tm_or_pct_off":"TM OR% (OFF)",
   "tm_to_pct_off":"TM TO% (OFF)",
   "tm_ft_ratio_off":"TM FT Rate (OFF)",
   "opp_ts_pct_off":"OPP TS% (OFF)",
   "opp_or_pct_off":"OPP OR% (OFF)",
   "opp_to_pct_off":"OPP TO% (OFF)",
   "opp_ft_ratio_off":"OPP FT Rate (OFF)",

   # Equipo/Oponente - Diferencia ON-OFF (NET)
   "tm_pace_net":"TM PACE (NET)",
   "tm_off_rtg_net":"TM OFF RTG (NET)",
   "tm_def_rtg_net":"TM DEF RTG (NET)",
   "tm_net_rtg_net":"TM NET RTG (NET)",
   "tm_ts_pct_net":"TM TS% (NET)",
   "tm_or_pct_net":"TM OR% (NET)",
   "tm_to_pct_net":"TM TO% (NET)",
   "tm_ft_ratio_net":"TM FT Rate (NET)",
   "opp_ts_pct_net":"OPP TS% (NET)",
   "opp_or_pct_net":"OPP OR% (NET)",
   "opp_to_pct_net":"OPP TO% (NET)",
   "opp_ft_ratio_net":"OPP FT Rate (NET)"
}

PLAYER_AVG_MAP = {
    # Perfil / básicas
   "avg_height":"HEIGHT",
   "avg_age":"AGE",

   # Record temporada / minutos
   "avg_gp":"GP",
   "avg_min":"MIN",
   "avg_w":"W",
   "avg_l":"L",
   "avg_w_pct":"W%",

   # Puntos + tiro
   "avg_pts":"PTS",
   "avg_two_ptm":"2PTM",
   "avg_two_pta":"2PTA",
   "avg_two_pt_pct":"2PT%",
   "avg_three_ptm":"3PTM",
   "avg_three_pta":"3PTA",
   "avg_three_pt_pct":"3PT%",
   "avg_fgm":"FGM",
   "avg_fga":"FGA",
   "avg_fg_pct":"FG%",
   "avg_ftm":"FTM",
   "avg_fta":"FTA",
   "avg_ft_pct":"FT%",
   "avg_blka":"BLKA",

   # Rebotes
   "avg_or_rebounds":"OR",
   "avg_dr_rebounds":"DR",
   "avg_tr_rebounds":"TR",

   # Playmaking
   "avg_ast":"AST",
   "avg_tovers":"TO",

   # Defensa
   "avg_st":"ST",
   "avg_blk":"BLK",

   # Faltas
   "avg_df":"DF",
   "avg_pf":"PF",

   # General
   "avg_val":"VAL",
   "avg_plus_minus":"+/-",

   # AVANZADAS - Ritmo, uso y eficiencia
   "avg_poss":"POSS",
   "avg_usg_pct":"USG%",
   "avg_ppp":"PPP",
   "avg_off_rtg_on":"OFF RTG (ON)",
   "avg_def_rtg_on":"DEF RTG (ON)",
   "avg_net_rtg_on":"NET RTG (ON)",
   "avg_ind_off_rtg":"IND OFF RTG",
   "avg_ind_def_rtg":"IND DEF RTG",
   "avg_ind_net_rtg":"IND NET RTG",
   "avg_efg_pct":"eFG%",
   "avg_ts_pct":"TS%",

   # AVANZADAS - Tiro (frecuencias y eficiencia)
   "avg_rim_freq":"RIM FREQ",
   "avg_rim_pps":"RIM PPT",
   "avg_paint_freq":"PAINT FREQ",
   "avg_paint_pps":"PAINT PPT",
   "avg_mid_freq":"MID FREQ",
   "avg_mid_pps":"MID PPT",
   "avg_c3_freq":"C3 FREQ",
   "avg_c3_pps":"C3 PPT",
   "avg_l3_freq":"L3 FREQ",
   "avg_l3_pps":"L3 PPT",
   "avg_ft_ratio":"FT Rate",

   # AVANZADAS - Playmaking
   "avg_to_pct":"TO%",
   "avg_lto_pct":"LTO%",
   "avg_dto_pct":"DTO%",
   "avg_ast_pct":"AST%",
   "avg_ast_pct_2p":"AST% (2P)",
   "avg_ast_pct_3p":"AST% (3P)",
   "avg_ast_pct_ft":"AST% (FT)",
   "avg_ast_ratio":"AST Ratio",
   "avg_ast_to_ratio":"AST/TO",

   # AVANZADAS - Rebotes
   "avg_or_pct":"OR%",
   "avg_or_pct_after_2p":"OR% (after 2P)",
   "avg_or_pct_after_3p":"OR% (after 3P)",
   "avg_or_pct_after_ft":"OR% (after FT)",
   "avg_dr_pct":"DR%",
   "avg_dr_pct_after_2p":"DR% (after 2P)",
   "avg_dr_pct_after_3p":"DR% (after 3P)",
   "avg_dr_pct_after_ft":"DR% (after FT)",
   "avg_tr_pct":"TR%",

   # AVANZADAS - Defensa
   "avg_st_pct":"ST%",
   "avg_blk_pct":"BLK%",
   "avg_blk_pct_2p":"BLK% (2P)",
   "avg_blk_pct_3p":"BLK% (3P)",

   # AVANZADAS - Faltas
   "avg_pf_100_poss":"PF 100 Poss",
   "avg_df_100_poss":"DF 100 Poss",

   # AVANZADAS - Métricas avanzadas
   "avg_per":"PER",
   "avg_off_win_share":"OFF WIN SHARE",
   "avg_def_win_share":"DEF WIN SHARE",
   "avg_win_share":"WIN SHARE",
   "avg_win_share_per_40":"WIN Share per 40",
   "avg_obpm":"OBPM",
   "avg_dbpm":"DBPM",
   "avg_bpm":"BPM",
   "avg_vorp":"VORP",

   # Equipo/Oponente - Jugador ON
   "avg_tm_pace_on":"TM PACE (ON)",
   "avg_tm_off_rtg_on":"TM OFF RTG (ON)",
   "avg_tm_def_rtg_on":"TM DEF RTG (ON)",
   "avg_tm_net_rtg_on":"TM NET RTG (ON)",
   "avg_tm_ts_pct_on":"TM TS% (ON)",
   "avg_tm_or_pct_on":"TM OR% (ON)",
   "avg_tm_to_pct_on":"TM TO% (ON)",
   "avg_tm_ft_ratio_on":"TM FT Rate (ON)",
   "avg_opp_ts_pct_on":"OPP TS% (ON)",
   "avg_opp_or_pct_on":"OPP OR% (ON)",
   "avg_opp_to_pct_on":"OPP TO% (ON)",
   "avg_opp_ft_ratio_on":"OPP FT Rate (ON)",

   # Equipo/Oponente - Jugador OFF
   "avg_tm_pace_off":"TM PACE (OFF)",
   "avg_tm_off_rtg_off":"TM OFF RTG (OFF)",
   "avg_tm_def_rtg_off":"TM DEF RTG (OFF)",
   "avg_tm_net_rtg_off":"TM NET RTG (OFF)",
   "avg_tm_ts_pct_off":"TM TS% (OFF)",
   "avg_tm_or_pct_off":"TM OR% (OFF)",
   "avg_tm_to_pct_off":"TM TO% (OFF)",
   "avg_tm_ft_ratio_off":"TM FT Rate (OFF)",
   "avg_opp_ts_pct_off":"OPP TS% (OFF)",
   "avg_opp_or_pct_off":"OPP OR% (OFF)",
   "avg_opp_to_pct_off":"OPP TO% (OFF)",
   "avg_opp_ft_ratio_off":"OPP FT Rate (OFF)",

   # Equipo/Oponente - NET
   "avg_tm_pace_net":"TM PACE (NET)",
   "avg_tm_off_rtg_net":"TM OFF RTG (NET)",
   "avg_tm_def_rtg_net":"TM DEF RTG (NET)",
   "avg_tm_net_rtg_net":"TM NET RTG (NET)",
   "avg_tm_ts_pct_net":"TM TS% (NET)",
   "avg_tm_or_pct_net":"TM OR% (NET)",
   "avg_tm_to_pct_net":"TM TO% (NET)",
   "avg_tm_ft_ratio_net":"TM FT Rate (NET)",
   "avg_opp_ts_pct_net":"OPP TS% (NET)",
   "avg_opp_or_pct_net":"OPP OR% (NET)",
   "avg_opp_to_pct_net":"OPP TO% (NET)",
   "avg_opp_ft_ratio_net":"OPP FT Rate (NET)",
}

TEAM_MAP = {
    # Perfil / básicas
    "tm_name": "Equipo",
    "season_id": "SEASON",

    # Record temporada / minutos
    "gp": "GP",
    "w": "W",
    "l": "L",
    "min": "MIN",

    # Puntos + tiro
    "pts": "PTS",
    "two_ptm": "2PTM",
    "two_pta": "2PTA",
    "two_pt_pct": "2PT%",
    "three_ptm": "3PTM",
    "three_pta": "3PTA",
    "three_pt_pct": "3PT%",
    "fgm": "FGM",
    "fga": "FGA",
    "fg_pct": "FG%",
    "ftm": "FTM",
    "fta": "FTA",
    "ft_pct": "FT%",
    "blka": "BLKA",

    # Rebotes
    "or_rebounds": "OR",
    "dr_rebounds": "DR",
    "tr_rebounds": "TR",

    # Playmaking
    "ast": "AST",
    "tovers": "TO",

    # Defensa
    "st": "ST",
    "blk": "BLK",

    # Faltas
    "pf": "PF",
    "df": "DF",

    # General
    "val": "VAL",
    "plus_minus": "+/-",

    # AVANZADAS - Pace, uso y eficiencia
    "pace": "Pace",
    "poss": "POSS",
    "shooting_chances": "Shooting Chances",
    "off_ppp": "OFF PPP",
    "def_ppp": "DEF PPP",
    "off_rtg": "OFF RTG",
    "def_rtg": "DEF RTG",
    "net_rtg": "NET RTG",
    "efg_pct": "eFG%",
    "ts_pct": "TS%",

    # AVANZADAS - Tiro (frecuencias y eficiencia)
    "rim_freq": "RIM FREQ",
    "rim_pps": "RIM PPT",
    "paint_freq": "PAINT FREQ",
    "paint_pps": "PAINT PPT",
    "mid_freq": "MID FREQ",
    "mid_pps": "MID PPT",
    "c3_freq": "C3 FREQ",
    "c3_pps": "C3 PPT",
    "l3_freq": "L3 FREQ",
    "l3_pps": "L3 PPT",
    "ft_ratio": "FT Rate",

    # AVANZADAS - Playmaking
    "to_pct": "TO%",
    "lto_pct": "LTO%",
    "dto_pct": "DTO%",
    "ast_pct": "AST%",
    "ast_pct_2p": "AST% (2P)",
    "ast_pct_3p": "AST% (3P)",
    "ast_pct_ft": "AST% (FT)",
    "ast_ratio": "AST Ratio",
    "ast_to_ratio": "AST/TO",

    # AVANZADAS - Rebotes
    "or_pct": "OR%",
    "or_pct_after_2p": "OR% (after 2P)",
    "or_pct_after_3p": "OR% (after 3P)",
    "or_pct_after_ft": "OR% (after FT)",
    "dr_pct": "DR%",
    "dr_pct_after_2p": "DR% (after 2P)",
    "dr_pct_after_3p": "DR% (after 3P)",
    "dr_pct_after_ft": "DR% (after FT)",
    "tr_pct": "TR%",

    # AVANZADAS - Defensa
    "st_pct": "ST%",
    "blk_pct": "BLK%",
    "blk_pct_2p": "BLK% (2P)",
    "blk_pct_3p": "BLK% (3P)",
    "kills": "Kills",

    # AVANZADAS - Faltas
    "psf_freq": "PSF FREQ",
    "dsf_freq": "DSF FREQ",

    # Calendario
    "sos": "SoS"
}

TEAM_AVG_MAP = {
    # Perfil / básicas
    "season_id": "SEASON",

    # Record temporada / minutos
    "avg_gp": "GP",
    "avg_w": "W",
    "avg_l": "L",
    "avg_min": "MIN",

    # Puntos + tiro
    "avg_pts": "PTS",
    "avg_two_ptm": "2PTM",
    "avg_two_pta": "2PTA",
    "avg_two_pt_pct": "2PT%",
    "avg_three_ptm": "3PTM",
    "avg_three_pta": "3PTA",
    "avg_three_pt_pct": "3PT%",
    "avg_fgm": "FGM",
    "avg_fga": "FGA",
    "avg_fg_pct": "FG%",
    "avg_ftm": "FTM",
    "avg_fta": "FTA",
    "avg_ft_pct": "FT%",
    "avg_blka": "BLKA",

    # Rebotes
    "avg_or_rebounds": "OR",
    "avg_dr_rebounds": "DR",
    "avg_tr_rebounds": "TR",

    # Playmaking
    "avg_ast": "AST",
    "avg_tovers": "TO",

    # Defensa
    "avg_st": "ST",
    "avg_blk": "BLK",

    # Faltas
    "avg_pf": "PF",
    "avg_df": "DF",

    # General
    "avg_val": "VAL",
    "avg_plus_minus": "+/-",

    # AVANZADAS - Pace, uso y eficiencia
    "avg_pace": "Pace",
    "avg_poss": "POSS",
    "avg_shooting_chances": "Shooting Chances",
    "avg_off_ppp": "OFF PPP",
    "avg_def_ppp": "DEF PPP",
    "avg_off_rtg": "OFF RTG",
    "avg_def_rtg": "DEF RTG",
    "avg_net_rtg": "NET RTG",
    "avg_efg_pct": "eFG%",
    "avg_ts_pct": "TS%",

    # AVANZADAS - Tiro (frecuencias y eficiencia)
    "avg_rim_freq": "RIM FREQ",
    "avg_rim_pps": "RIM PPT",
    "avg_paint_freq": "PAINT FREQ",
    "avg_paint_pps": "PAINT PPT",
    "avg_mid_freq": "MID FREQ",
    "avg_mid_pps": "MID PPT",
    "avg_c3_freq": "C3 FREQ",
    "avg_c3_pps": "C3 PPT",
    "avg_l3_freq": "L3 FREQ",
    "avg_l3_pps": "L3 PPT",
    "avg_ft_ratio": "FT Rate",

    # AVANZADAS - Playmaking
    "avg_to_pct": "TO%",
    "avg_lto_pct": "LTO%",
    "avg_dto_pct": "DTO%",
    "avg_ast_pct": "AST%",
    "avg_ast_pct_2p": "AST% (2P)",
    "avg_ast_pct_3p": "AST% (3P)",
    "avg_ast_pct_ft": "AST% (FT)",
    "avg_ast_ratio": "AST Ratio",
    "avg_ast_to_ratio": "AST/TO",

    # AVANZADAS - Rebotes
    "avg_or_pct": "OR%",
    "avg_or_pct_after_2p": "OR% (after 2P)",
    "avg_or_pct_after_3p": "OR% (after 3P)",
    "avg_or_pct_after_ft": "OR% (after FT)",
    "avg_dr_pct": "DR%",
    "avg_dr_pct_after_2p": "DR% (after 2P)",
    "avg_dr_pct_after_3p": "DR% (after 3P)",
    "avg_dr_pct_after_ft": "DR% (after FT)",
    "avg_tr_pct": "TR%",

    # AVANZADAS - Defensa
    "avg_st_pct": "ST%",
    "avg_blk_pct": "BLK%",
    "avg_blk_pct_2p": "BLK% (2P)",
    "avg_blk_pct_3p": "BLK% (3P)",
    "avg_kills": "Kills",

    # AVANZADAS - Faltas
    "avg_psf_freq": "PSF FREQ",
    "avg_dsf_freq": "DSF FREQ",

    # Calendario
    "avg_sos": "SoS",
}

FEATURE_TO_DB = {
    "+ / -": "plus_minus",
    "2PT%": "two_pt_pct",
    "2PTA": "two_pta",
    "2PTM": "two_ptm",
    "3PT%": "three_pt_pct",
    "3PTA": "three_pta",
    "3PTM": "three_ptm",
    "AGE": "age",
    "AST": "ast",
    "AST Ratio": "ast_ratio",
    "AST%": "ast_pct",
    "AST% (2P)": "ast_pct_2p",
    "AST% (3P)": "ast_pct_3p",
    "AST% (FT)": "ast_pct_ft",
    "AST/TO": "ast_to_ratio",
    "BLK": "blk",
    "BLK%": "blk_pct",
    "BLK% (2P)": "blk_pct_2p",
    "BLK% (3P)": "blk_pct_3p",
    "BLKA": "blka",
    "BPM": "bpm",
    "C3 FREQ": "c3_freq",
    "C3 PPS": "c3_pps",
    "DBPM": "dbpm",
    "DEF RTG (ON)": "def_rtg_on",
    "DEF WIN SHARE": "def_win_share",
    "DF": "df",
    "DF 100 Poss": "df_100_poss",
    "DR": "dr_rebounds",
    "DR%": "dr_pct",
    "DR% (after 2P)": "dr_pct_after_2p",
    "DR% (after 3P)": "dr_pct_after_3p",
    "DR% (after FT)": "dr_pct_after_ft",
    "DTO%": "dto_pct",
    "FG%": "fg_pct",
    "FGA": "fga",
    "FGM": "fgm",
    "FT Ratio": "ft_ratio",
    "FT%": "ft_pct",
    "FTA": "fta",
    "FTM": "ftm",
    "GP": "gp",
    "HEIGHT": "height",
    "IND DEF RTG": "ind_def_rtg",
    "IND NET RTG": "ind_net_rtg",
    "IND OFF RTG": "ind_off_rtg",
    "L": "l",
    "L3 FREQ": "l3_freq",
    "L3 PPS": "l3_pps",
    "LTO%": "lto_pct",
    "MID FREQ": "mid_freq",
    "MID PPS": "mid_pps",
    "MIN": "min",
    "NET RTG (ON)": "net_rtg_on",
    "OBPM": "obpm",
    "OFF RTG (ON)": "off_rtg_on",
    "OFF WIN SHARE": "off_win_share",
    "OPP FT Ratio (NET)": "opp_ft_ratio_net",
    "OPP FT Ratio (OFF)": "opp_ft_ratio_off",
    "OPP FT Ratio (ON)": "opp_ft_ratio_on",
    "OPP OR% (NET)": "opp_or_pct_net",
    "OPP OR% (OFF)": "opp_or_pct_off",
    "OPP OR% (ON)": "opp_or_pct_on",
    "OPP TO% (NET)": "opp_to_pct_net",
    "OPP TO% (OFF)": "opp_to_pct_off",
    "OPP TO% (ON)": "opp_to_pct_on",
    "OPP TS% (NET)": "opp_ts_pct_net",
    "OPP TS% (OFF)": "opp_ts_pct_off",
    "OPP TS% (ON)": "opp_ts_pct_on",
    "OR": "or_rebounds",
    "OR%": "or_pct",
    "OR% (after 2P)": "or_pct_after_2p",
    "OR% (after 3P)": "or_pct_after_3p",
    "OR% (after FT)": "or_pct_after_ft",
    "PAINT FREQ": "paint_freq",
    "PAINT PPS": "paint_pps",
    "PER": "per",
    "PF": "pf",
    "PF 100 Poss": "pf_100_poss",
    "POSS": "poss",
    "PPP": "ppp",
    "PTS": "pts",
    "RIM FREQ": "rim_freq",
    "RIM PPS": "rim_pps",
    "RNK": None,  # No existe en la tabla; dejar en 0
    "ST": "st",
    "ST%": "st_pct",
    "TM DEF RTG (NET)": "tm_def_rtg_net",
    "TM DEF RTG (OFF)": "tm_def_rtg_off",
    "TM DEF RTG (ON)": "tm_def_rtg_on",
    "TM FT Ratio (NET)": "tm_ft_ratio_net",
    "TM FT Ratio (OFF)": "tm_ft_ratio_off",
    "TM FT Ratio (ON)": "tm_ft_ratio_on",
    "TM NET RTG (NET)": "tm_net_rtg_net",
    "TM NET RTG (OFF)": "tm_net_rtg_off",
    "TM NET RTG (ON)": "tm_net_rtg_on",
    "TM OFF RTG (NET)": "tm_off_rtg_net",
    "TM OFF RTG (OFF)": "tm_off_rtg_off",
    "TM OFF RTG (ON)": "tm_off_rtg_on",
    "TM OR% (NET)": "tm_or_pct_net",
    "TM OR% (OFF)": "tm_or_pct_off",
    "TM OR% (ON)": "tm_or_pct_on",
    "TM PACE (NET)": "tm_pace_net",
    "TM PACE (OFF)": "tm_pace_off",
    "TM PACE (ON)": "tm_pace_on",
    "TM TO% (NET)": "tm_to_pct_net",
    "TM TO% (OFF)": "tm_to_pct_off",
    "TM TO% (ON)": "tm_to_pct_on",
    "TM TS% (NET)": "tm_ts_pct_net",
    "TM TS% (OFF)": "tm_ts_pct_off",
    "TM TS% (ON)": "tm_ts_pct_on",
    "TO": "tovers",
    "TO%": "to_pct",
    "TR": "tr_rebounds",
    "TR%": "tr_pct",
    "TS%": "ts_pct",
    "USG%": "usg_pct",
    "VAL": "val",
    "VORP": "vorp",
    "W": "w",
    "W%": "w_pct",
    "WIN SHARE": "win_share",
    "WIN Share per 40": "win_share_per_40",
    "eFG%": "efg_pct",
}