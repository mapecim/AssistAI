from fastapi import APIRouter
from .database import get_all_players, get_players_stats_names, get_all_seasons, get_all_teams

router = APIRouter()

@router.get("/players")
def get_players():
    """
    Endpoint para obtener una lista de todos los nombres de jugadores.
    """
    players = get_all_players()
    return {"players": players}

@router.get("/player-stats-names")
def get_player_stats_names():
    """
    Endpoint para obtener una lista de todos los nombres de las estadísticas de los jugadores.
    """
    stats_names = get_players_stats_names()
    return {"player_stats_names": stats_names}

@router.get("/teams")
def get_teams():
    """
    Endpoint para obtener una lista de todos los nombres de equipos.
    """
    teams = get_all_teams()
    return {"teams": teams}

@router.get("/seasons")
def get_seasons():
    """
    Endpoint para obtener una lista de todas las temporadas.
    """
    seasons = get_all_seasons()
    return {"seasons": seasons}