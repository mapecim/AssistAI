from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict
import psycopg2
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from config import ADVANCED_DB_CONFIG

router = APIRouter()

@router.get("/compare-player")
def compare_player(
    player_name: str = Query(..., description="Nombre del jugador a comparar"),
    season_id: str = Query(..., description="Temporada del jugador a comparar"),
    same_role: bool = Query(False, description="Comparar solo con jugadores del mismo rol"),
    weights: Optional[Dict[str, float]] = None
):
    """
    Compara las estadísticas de un jugador con otros jugadores buscando similitudes.
    """
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)

        # Obtener jugador base
        base_stats_query = """
            SELECT * FROM player_stats
            WHERE name = %s AND season_id = %s
            LIMIT 1
        """
        base_df = pd.read_sql(base_stats_query, conn, params=(player_name, season_id))
        if base_df.empty:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Jugador '{player_name}' no encontrado en la temporada '{season_id}'.")

        base_role = base_df.iloc[0]['role']

        # Query dinámico
        query_parts = ["(s.name != %s OR s.season_id != %s)"]
        params = [player_name, season_id]
        if same_role:
            query_parts.append("s.role = %s")
            params.append(base_role)

        base_query = f"""
        SELECT * FROM player_stats s
        WHERE {' AND '.join(query_parts)}
        """
        df = pd.read_sql(base_query, conn, params=params)

        conn.close()
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron jugadores para comparar.")

        # Detectar columnas numéricas
        numeric_cols = base_df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['id', 'name', 'tm_name', 'season_id', 'nat', 'gp', 'w', 'l', 'w_pct']
        metrics = [col for col in numeric_cols if col not in exclude_cols]

        full_df = pd.concat([base_df[metrics], df[metrics]], ignore_index=True)

        # Estandarizar
        scaler = StandardScaler()
        scaled = scaler.fit_transform(full_df)

        # Aplicar pesos
        if weights:
            weight_array = np.array([weights.get(col, 1.0) for col in metrics])
            scaled = scaled * weight_array

        # Calcular similitud coseno
        sim_matrix = cosine_similarity(scaled)
        base_similarities = sim_matrix[0, 1:]

        # Construir resultado
        similarities = []
        for i, sim in enumerate(base_similarities):
            similarities.append({
                "name": df.iloc[i]['name'],
                "season_id": df.iloc[i]['season_id'],
                "team_name": df.iloc[i]['tm_name'],
                "similarity_score": round(sim * 100, 2)
            })

        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

        return {
            "jugador_base": {"name": player_name, "season_id": season_id, "role": base_role},
            "mismo_rol": same_role,
            "resultados_similares": similarities[:10]
        }

    except psycopg2.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {db_error}")
    except Exception:
        raise HTTPException(status_code=500, detail="Error inesperado")
