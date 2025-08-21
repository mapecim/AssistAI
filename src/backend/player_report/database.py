import psycopg2
import psycopg2.extras
from typing import List, Dict, Tuple, Union
from config import ADVANCED_DB_CONFIG

def get_player_stats(player_season_pairs: List[Tuple[str, str]]) -> Union[List[Dict], None]:
    """
    Recupera las estadísticas de temporada para uno o dos jugadores, 
    cada uno con su propia temporada.
    
    Args:
        player_season_pairs: Lista de tuplas (nombre_jugador, season_id)
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        results = []

        for player_name, season_id in player_season_pairs:
            sql_get_stats = """
                SELECT *
                FROM player_stats ps
                WHERE ps.name = %s AND ps.season_id = %s;
            """
            cur.execute(sql_get_stats, (player_name, season_id))
            stats_rows = cur.fetchall()

            for stats in stats_rows:
                results.append(dict(stats))

        return results if results else None

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al consultar la base de datos: {error}")
        return None
    finally:
        if conn is not None:
            conn.close()

def avg_player_stats(season_id):
    """
    Calcula las medias de todas las columnas numéricas de player_stats para una temporada dada.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'player_stats'
              AND data_type IN ('integer', 'double precision', 'real', 'numeric')
              AND column_name NOT IN ('id', 'name', 'tm_name', 'role', 'nat', 'season_id');
        """)
        numeric_cols = [row[0] for row in cur.fetchall()]

        avg_exprs = [f"AVG({col}) AS avg_{col}" for col in numeric_cols]
        # min > 5 para eliminar outliers
        sql = f"""
            SELECT season_id, {', '.join(avg_exprs)}
            FROM player_stats
            WHERE season_id = %s AND min > 5
            GROUP BY season_id
        """

        cur.execute(sql, (season_id,))
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        if rows:
            return dict(zip(cols, rows[0]))
        return None

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al consultar la base de datos: {error}")
        return None
    finally:
        if conn is not None:
            conn.close()
