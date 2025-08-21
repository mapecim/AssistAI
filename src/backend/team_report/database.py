import psycopg2
import psycopg2.extras
from typing import List, Dict, Tuple, Union
from config import ADVANCED_DB_CONFIG

def get_team_stats(team_season_pairs: List[Tuple[str, str]]) -> Union[List[Dict], None]:
    """
    Recupera las estadísticas de temporada para uno o dos equipos, 
    cada uno con su propia temporada.
    
    Args:
        team_season_pairs: Lista de tuplas (nombre_equipo, season_id)
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        results = []

        for team_name, season_id in team_season_pairs:
            sql_get_stats = """
                SELECT *
                FROM team_stats ts
                WHERE ts.tm_name = %s AND ts.season_id = %s;
            """
            cur.execute(sql_get_stats, (team_name, season_id))
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

def avg_team_stats(season_id):
    """
    Calcula las medias de todas las columnas numéricas de team_stats para una temporada dada.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'team_stats'
              AND data_type IN ('integer', 'double precision', 'real', 'numeric')
              AND column_name NOT IN ('id', 'name', 'tm_name', 'role', 'nat', 'season_id');
        """)
        numeric_cols = [row[0] for row in cur.fetchall()]

        avg_exprs = [f"AVG({col}) AS avg_{col}" for col in numeric_cols]
        sql = f"""
            SELECT season_id, {', '.join(avg_exprs)}
            FROM team_stats
            WHERE season_id = %s
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