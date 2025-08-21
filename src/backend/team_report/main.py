from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .database import get_team_stats, avg_team_stats

router = APIRouter()

@router.get("/report_stats")
async def get_team_report_stats(
    team1: str = Query(..., description="Nombre del primer equipo"),
    season1: str = Query(..., description="Temporada del primer equipo"),
    team2: Optional[str] = Query(None, description="Nombre del segundo equipo"),
    season2: Optional[str] = Query(None, description="Temporada del segundo equipo"),
):
    """
    Endpoint para obtener estadísticas de temporada de uno o dos equipos, 
    cada uno con su temporada correspondiente.
    """
    team_season_pairs = [(team1, season1)]

    if team2 and season2:
        team_season_pairs.append((team2, season2))
    elif team2 or season2:
        raise HTTPException(
            status_code=400,
            detail="Si proporcionas team2 o season2, debes proporcionar ambos."
        )

    stats = get_team_stats(team_season_pairs)

    if not stats:
        raise HTTPException(status_code=404, detail="No se encontraron estadísticas para los equipos o temporadas especificadas.")

    return {"team_stats": stats}

@router.get("/season_avg_stats")
async def get_season_average_stats(
    season: str = Query(..., description="Temporada para la que se desean las estadísticas promedio")
):
    """
    Endpoint para obtener estadísticas promedio de una temporada específica.
    """
    avg_stats = avg_team_stats(season)

    if not avg_stats:
        raise HTTPException(status_code=404, detail="No se encontraron estadísticas para la temporada especificada.")

    return {"average_stats": avg_stats}