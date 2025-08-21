from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .database import get_player_stats, avg_player_stats

router = APIRouter()

@router.get("/report_stats")
async def get_player_report_stats(
    player1: str = Query(..., description="Nombre del primer jugador"),
    season1: str = Query(..., description="Temporada del primer jugador"),
    player2: Optional[str] = Query(None, description="Nombre del segundo jugador"),
    season2: Optional[str] = Query(None, description="Temporada del segundo jugador"),
):
    """
    Endpoint para obtener estadísticas de temporada de uno o dos jugadores, 
    cada uno con su temporada correspondiente.
    """
    player_season_pairs = [(player1, season1)]

    if player2 and season2:
        player_season_pairs.append((player2, season2))
    elif player2 or season2:
        raise HTTPException(
            status_code=400,
            detail="Si proporcionas player2 o season2, debes proporcionar ambos."
        )

    stats = get_player_stats(player_season_pairs)

    if not stats:
        raise HTTPException(status_code=404, detail="No se encontraron estadísticas para los jugadores o temporadas especificadas.")

    return {"player_stats": stats}

@router.get("/season_avg_stats")
async def get_season_average_stats(
    season: str = Query(..., description="Temporada para la que se desean las estadísticas promedio")
):
    """
    Endpoint para obtener estadísticas promedio de una temporada específica.
    """
    avg_stats = avg_player_stats(season)

    if not avg_stats:
        raise HTTPException(status_code=404, detail="No se encontraron estadísticas para la temporada especificada.")

    return {"average_stats": avg_stats}