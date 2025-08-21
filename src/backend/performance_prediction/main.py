import os
import json
import pandas as pd
import psycopg2
import psycopg2.extras
import joblib
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import numpy as np
from config import ADVANCED_DB_CONFIG, FEATURE_TO_DB

router = APIRouter()

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "performance_model.pkl")
FEATURE_COLUMNS_JSON = os.path.join(BASE_DIR, "feature_columns.json")


def load_feature_columns() -> List[str]:
    if not os.path.exists(FEATURE_COLUMNS_JSON):
        raise FileNotFoundError(f"feature_columns.json no encontrado en: {FEATURE_COLUMNS_JSON}")
    with open(FEATURE_COLUMNS_JSON, "r", encoding="utf-8") as f:
        payload = json.load(f)
    cols = payload.get("feature_columns")
    if not isinstance(cols, list) or not cols:
        raise ValueError("feature_columns.json no contiene una lista 'feature_columns' válida.")
    return cols

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    print("Modelo cargado correctamente.")
    return model

def safe_num(x) -> float:
    """
    Convierte a float y sustituye None/NaN por 0.0
    """
    try:
        v = float(x)
        if np.isnan(v):
            return 0.0
        return v
    except Exception:
        return 0.0

try:
    predictor_model = load_model()
    print("Modelo de predicción cargado correctamente.")
except Exception as e:
    print("Error loading model")
    predictor_model = None

try:
    FEATURE_COLUMNS = load_feature_columns()
    print(f"feature_columns.json cargado ({len(FEATURE_COLUMNS)} columnas).")
except Exception as e:
    print("Error loading feature columns")
    FEATURE_COLUMNS = None

def get_player_stats_from_db(player_name: str, season_id: str) -> Dict:
    """
    Recupera las estadísticas de un jugador de la base de datos avanzada.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        sql_query = """
            SELECT *
            FROM player_stats
            WHERE name = %s AND season_id = %s;
        """
        cur.execute(sql_query, (player_name, season_id))
        stats_row = cur.fetchone()

        if stats_row:
            return dict(stats_row)
        else:
            return None
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al consultar la base de datos: {error}")
        return None
    finally:
        if conn is not None:
            conn.close()

@router.get("/predict")
def predict_lineup_performance(
    player1_name: str,
    season1_id: str,
    player2_name: str,
    season2_id: str,
    player3_name: str,
    season3_id: str,
    player4_name: str,
    season4_id: str,
    player5_name: str,
    season5_id: str
):
    """
    Endpoint para predecir el rendimiento (Net Rating) de un quinteto usando
    el nuevo modelo que requiere features agregadas (_sum y _mean).
    """
    if predictor_model is None:
        raise HTTPException(status_code=503, detail="El modelo de predicción no está disponible.")
    if FEATURE_COLUMNS is None:
        raise HTTPException(status_code=503, detail="Las columnas de features no están disponibles.")

    players_data = [
        get_player_stats_from_db(player1_name, season1_id),
        get_player_stats_from_db(player2_name, season2_id),
        get_player_stats_from_db(player3_name, season3_id),
        get_player_stats_from_db(player4_name, season4_id),
        get_player_stats_from_db(player5_name, season5_id),
    ]

    if any(p is None for p in players_data):
        raise HTTPException(
            status_code=404,
            detail="No se encontraron datos para uno o más jugadores y temporadas seleccionadas."
        )

    data_for_prediction = {col: 0.0 for col in FEATURE_COLUMNS}

    for base_name, db_col in FEATURE_TO_DB.items():
        sum_key = f"{base_name}_sum"
        mean_key = f"{base_name}_mean"
        if sum_key not in data_for_prediction and mean_key not in data_for_prediction:
            continue

        if db_col is None:
            if sum_key in data_for_prediction:
                data_for_prediction[sum_key] = 0.0
            if mean_key in data_for_prediction:
                data_for_prediction[mean_key] = 0.0
            continue

        values = [safe_num(p.get(db_col, 0.0)) for p in players_data]
        s = float(np.nansum(values))
        m = s / 5.0 

        if sum_key in data_for_prediction:
            data_for_prediction[sum_key] = s
        if mean_key in data_for_prediction:
            data_for_prediction[mean_key] = m

    df_for_prediction = pd.DataFrame([data_for_prediction], columns=FEATURE_COLUMNS)

    for col in df_for_prediction.columns:
        df_for_prediction[col] = pd.to_numeric(df_for_prediction[col], errors='coerce')
    df_for_prediction = df_for_prediction.fillna(0.0)

    try:
        prediction = predictor_model.predict(df_for_prediction)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al realizar la predicción")

    return {
        "predicted_net_rating": float(prediction[0]),
        "lineup": [p['name'] for p in players_data]
    }
