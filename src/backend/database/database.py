import psycopg2
import psycopg2.extras
from config import ADVANCED_DB_CONFIG
from typing import List, Dict

def get_all_players() -> List[Dict]:
    """
    Recupera una lista de todos los jugadores de la base de datos.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT name FROM players ORDER BY name;")
        players = [row['name'] for row in cur.fetchall()]
        return players
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al obtener los jugadores: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()

def get_players_stats_names() -> List[str]:
    """
    Recupera una lista de todos los nombres de las estadísticas de los jugadores.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'player_stats';")
        stats_names = [row['column_name'] for row in cur.fetchall()]
        return stats_names
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al obtener los nombres de las estadísticas de los jugadores: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()

def get_all_teams() -> List[Dict]:
    """
    Recupera una lista de todos los equipos de la base de datos.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT tm_name FROM teams ORDER BY tm_name;")
        teams = [row['tm_name'] for row in cur.fetchall()]
        return teams
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al obtener los equipos: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()

def get_all_seasons() -> List[Dict]:
    """
    Recupera una lista de todas las temporadas de la base de datos.
    """
    conn = None
    try:
        conn = psycopg2.connect(**ADVANCED_DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT season_id, season_name FROM seasons ORDER BY season_name;")
        seasons = [{"id": row['season_id'], "name": row['season_name']} for row in cur.fetchall()]
        return seasons
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error al obtener las temporadas: {error}")
        return []
    finally:
        if conn is not None:
            conn.close()