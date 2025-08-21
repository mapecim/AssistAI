import psycopg2
from config import DB_CONFIG

def connect():
    """Conecta a la base de datos PostgreSQL."""
    try:
        # Conexión sin especificar la base de datos para crear una nueva
        conn = psycopg2.connect(
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            dbname='postgres' # Conectar a la base de datos por defecto
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Crear la base de datos si no existe
        db_name = DB_CONFIG['dbname']
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"Base de datos '{db_name}' creada.")
        else:
            print(f"Base de datos '{db_name}' ya existe.")

        # Cerrar la conexión inicial
        cur.close()
        conn.close()

        # Conectar a la nueva base de datos y crear tablas
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except psycopg2.OperationalError as e:
        print(f"No se pudo conectar a la base de datos")
        return None

def create_tables():
    """Crea las tablas necesarias en la base de datos."""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS competitions (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category_id VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS seasons (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            year VARCHAR(10) NOT NULL,
            start_date DATE,
            end_date DATE,
            competition_id VARCHAR(255) REFERENCES competitions(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS teams (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            country VARCHAR(255),
            country_code VARCHAR(10),
            abbreviation VARCHAR(10)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sport_events (
            id VARCHAR(255) PRIMARY KEY,
            start_time TIMESTAMP,
            status VARCHAR(50),
            competition_id VARCHAR(255) REFERENCES competitions(id),
            season_id VARCHAR(255) REFERENCES seasons(id),
            home_team_id VARCHAR(255) REFERENCES teams(id),
            away_team_id VARCHAR(255) REFERENCES teams(id),
            home_score INTEGER,
            away_score INTEGER
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS team_statistics (
            id SERIAL PRIMARY KEY,
            sport_event_id VARCHAR(255) REFERENCES sport_events(id),
            team_id VARCHAR(255) REFERENCES teams(id),
            assists INTEGER,
            ball_possession INTEGER,
            biggest_lead INTEGER,
            defensive_rebounds INTEGER,
            fouls INTEGER,
            free_throw_attempts_successful INTEGER,
            free_throw_attempts_total INTEGER,
            offensive_rebounds INTEGER,
            rebounds INTEGER,
            shots_blocked INTEGER,
            steals INTEGER,
            team_leads INTEGER,
            team_rebounds INTEGER,
            team_turnovers INTEGER,
            three_point_attempts_successful INTEGER,
            three_point_attempts_total INTEGER,
            time_spent_in_lead INTEGER,
            timeouts INTEGER,
            turnovers INTEGER,
            two_point_attempts_successful INTEGER,
            two_point_attempts_total INTEGER,
            possessions NUMERIC,
            oreb_pct NUMERIC,
            dreb_pct NUMERIC,
            ast_to NUMERIC,
            to_pct NUMERIC,
            UNIQUE (sport_event_id, team_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS players (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            team_id VARCHAR(255) REFERENCES teams(id),
            season_id VARCHAR(255) REFERENCES seasons(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS player_statistics (
            id SERIAL PRIMARY KEY,
            player_id VARCHAR(255) REFERENCES players(id),
            sport_event_id VARCHAR(255) REFERENCES sport_events(id),
            minutes VARCHAR(10),
            points INTEGER,
            assists INTEGER,
            rebounds INTEGER,
            total_rebounds INTEGER,
            defensive_rebounds INTEGER,
            offensive_rebounds INTEGER,
            blocks INTEGER,
            steals INTEGER,
            turnovers INTEGER,
            personal_fouls INTEGER,
            technical_fouls INTEGER,
            field_goals_attempted INTEGER,
            field_goals_made INTEGER,
            three_pointers_attempted INTEGER,
            three_pointers_made INTEGER,
            free_throws_attempted INTEGER,
            free_throws_made INTEGER,
            UNIQUE (player_id, sport_event_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS season_player_statistics (
            id SERIAL PRIMARY KEY,
            player_id VARCHAR(255) REFERENCES players(id),
            season_id VARCHAR(255) REFERENCES seasons(id),
            points_total INTEGER,
            rebounds_total INTEGER,
            assists_total INTEGER,
            blocks_total INTEGER,
            steals_total INTEGER,
            minutes_total VARCHAR(10),
            games_played INTEGER,
            UNIQUE (player_id, season_id)
        )
        """
    )
    conn = connect()
    if conn:
        try:
            with conn.cursor() as cur:
                for command in commands:
                    cur.execute(command)
                conn.commit()
            print("Tablas creadas exitosamente.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error al crear las tablas: {error}")
        finally:
            conn.close()

def insert_competition(conn, comp):
    """Inserta una competición en la tabla `competitions`."""
    sql = "INSERT INTO competitions (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING"
    cur = conn.cursor()
    cur.execute(sql, (comp['id'], comp['name']))
    conn.commit()

def insert_season(conn, season_data, competition_id):
    """Inserta una temporada en la tabla `seasons`."""
    sql = "INSERT INTO seasons (id, name, year, start_date, end_date, competition_id) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING"
    cur = conn.cursor()
    cur.execute(sql, (season_data['id'], season_data['name'], season_data['year'], season_data['start_date'], season_data['end_date'], competition_id))
    conn.commit()

def insert_team(conn, team_data):
    """Inserta un equipo en la tabla `teams`."""
    sql = "INSERT INTO teams (id, name, country, country_code, abbreviation) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING"
    cur = conn.cursor()
    cur.execute(sql, (
        team_data.get('id'),
        team_data.get('name'),
        team_data.get('country'),
        team_data.get('country_code'),
        team_data.get('abbreviation')
    ))
    conn.commit()

def insert_sport_event_summary(conn, summary):
    """Inserta un resumen de evento deportivo en la tabla `sport_events`."""
    sport_event = summary.get('sport_event', {})
    status = summary.get('sport_event_status', {})
    
    competitors = sport_event.get('competitors', [])
    home_team_id = next((c['id'] for c in competitors if c.get('qualifier') == 'home'), None)
    away_team_id = next((c['id'] for c in competitors if c.get('qualifier') == 'away'), None)

    sql = """
        INSERT INTO sport_events (id, start_time, status, competition_id, season_id, home_team_id, away_team_id, home_score, away_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """
    cur = conn.cursor()
    cur.execute(sql, (
        sport_event.get('id'),
        sport_event.get('start_time'),
        status.get('status'),
        sport_event.get('sport_event_context', {}).get('competition', {}).get('id'),
        sport_event.get('sport_event_context', {}).get('season', {}).get('id'),
        home_team_id,
        away_team_id,
        status.get('home_score'),
        status.get('away_score')
    ))
    conn.commit()

def compute_advanced_team_metrics(stats, opp_stats):
    """Calcula métricas avanzadas a partir de las estadísticas del equipo y su rival."""
    fga = (stats.get('two_point_attempts_total', 0) or 0) + (stats.get('three_point_attempts_total', 0) or 0)
    fta = stats.get('free_throw_attempts_total', 0) or 0
    oreb = stats.get('offensive_rebounds', 0) or 0
    dreb = stats.get('defensive_rebounds', 0) or 0
    tov = stats.get('turnovers', 0) or 0
    ast = stats.get('assists', 0) or 0
    fgm = (stats.get('two_point_attempts_successful', 0) or 0) + (stats.get('three_point_attempts_successful', 0) or 0)

    # Datos del rival
    opp_dreb = opp_stats.get('defensive_rebounds', 0) or 0
    opp_oreb = opp_stats.get('offensive_rebounds', 0) or 0

    possessions = fga + 0.44 * fta - oreb + tov if (fga or fta or tov) else 0
    oreb_pct = oreb / (oreb + opp_dreb) if (oreb + opp_dreb) > 0 else None
    dreb_pct = dreb / (dreb + opp_oreb) if (dreb + opp_oreb) > 0 else None
    ast_to = ast / tov if (ast and tov) else None
    to_pct = 100 * tov / possessions if possessions > 0 else None

    return {
        "possessions": possessions,
        "oreb_pct": oreb_pct,
        "dreb_pct": dreb_pct,
        "ast_to": ast_to,
        "to_pct": to_pct
    }


def insert_team_statistics(conn, sport_event_id, competitor_data, opp_data=None):
    """Inserta las estadísticas de un equipo para un evento deportivo con métricas avanzadas."""
    stats = competitor_data.get('statistics', {})
    adv_stats = compute_advanced_team_metrics(stats, opp_data.get('statistics', {}) if opp_data else {})

    sql = """
        INSERT INTO team_statistics (
            sport_event_id, team_id, assists, ball_possession, biggest_lead,
            defensive_rebounds, fouls, free_throw_attempts_successful,
            free_throw_attempts_total, offensive_rebounds, rebounds,
            shots_blocked, steals, team_leads, team_rebounds, team_turnovers,
            three_point_attempts_successful, three_point_attempts_total,
            time_spent_in_lead, timeouts, turnovers, two_point_attempts_successful,
            two_point_attempts_total, possessions, oreb_pct, dreb_pct, ast_to, to_pct
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (sport_event_id, team_id) DO NOTHING
    """
    cur = conn.cursor()
    cur.execute(sql, (
        sport_event_id,
        competitor_data.get('id'),
        stats.get('assists'),
        stats.get('ball_possession'),
        stats.get('biggest_lead'),
        stats.get('defensive_rebounds'),
        stats.get('fouls'),
        stats.get('free_throw_attempts_successful'),
        stats.get('free_throw_attempts_total'),
        stats.get('offensive_rebounds'),
        stats.get('rebounds'),
        stats.get('shots_blocked'),
        stats.get('steals'),
        stats.get('team_leads'),
        stats.get('team_rebounds'),
        stats.get('team_turnovers'),
        stats.get('three_point_attempts_successful'),
        stats.get('three_point_attempts_total'),
        stats.get('time_spent_in_lead'),
        stats.get('timeouts'),
        stats.get('turnovers'),
        stats.get('two_point_attempts_successful'),
        stats.get('two_point_attempts_total'),
        adv_stats["possessions"],
        adv_stats["oreb_pct"],
        adv_stats["dreb_pct"],
        adv_stats["ast_to"],
        adv_stats["to_pct"]
    ))
    conn.commit()


def insert_player_statistics(conn, sport_event_id, player_data):
    """Inserta las estadísticas de un jugador para un evento deportivo."""
    player_id = player_data.get('id')
    stats = player_data.get('statistics', {})
    
    sql_stats = """
        INSERT INTO player_statistics (
            player_id, sport_event_id, minutes, points, assists, rebounds, total_rebounds,
            defensive_rebounds, offensive_rebounds, blocks, steals, turnovers, personal_fouls,
            technical_fouls, field_goals_attempted, field_goals_made, three_pointers_attempted,
            three_pointers_made, free_throws_attempted, free_throws_made
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (player_id, sport_event_id) DO NOTHING
    """
    cur = conn.cursor()
    cur.execute(sql_stats, (
        player_id,
        sport_event_id,
        stats.get('minutes'),
        stats.get('points'),
        stats.get('assists'),
        stats.get('rebounds'),
        stats.get('total_rebounds'),
        stats.get('defensive_rebounds'),
        stats.get('offensive_rebounds'),
        stats.get('blocks'),
        stats.get('steals'),
        stats.get('turnovers'),
        stats.get('personal_fouls'),
        stats.get('technical_fouls'),
        stats.get('field_goals_attempted'),
        stats.get('field_goals_made'),
        stats.get('three_pointers_attempted'),
        stats.get('three_pointers_made'),
        stats.get('free_throws_attempted'),
        stats.get('free_throws_made')
    ))
    conn.commit()

def insert_player(conn, player_data, team_id, season_id):
    """Inserta un jugador en la tabla `players` con su equipo y temporada."""
    sql = "INSERT INTO players (id, name, team_id, season_id) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING"
    cur = conn.cursor()
    cur.execute(sql, (player_data.get('id'), player_data.get('name'), team_id, season_id))
    conn.commit()

def update_season_player_statistics(conn, player_id, season_id):
    """Calcula y actualiza las estadísticas de temporada de un jugador."""
    sql = """
        INSERT INTO season_player_statistics (
            player_id, season_id, points_total, rebounds_total, assists_total,
            blocks_total, steals_total, games_played
        ) VALUES (%s, %s,
            (SELECT SUM(points) FROM player_statistics WHERE player_id = %s AND sport_event_id IN (SELECT id FROM sport_events WHERE season_id = %s)),
            (SELECT SUM(total_rebounds) FROM player_statistics WHERE player_id = %s AND sport_event_id IN (SELECT id FROM sport_events WHERE season_id = %s)),
            (SELECT SUM(assists) FROM player_statistics WHERE player_id = %s AND sport_event_id IN (SELECT id FROM sport_events WHERE season_id = %s)),
            (SELECT SUM(blocks) FROM player_statistics WHERE player_id = %s AND sport_event_id IN (SELECT id FROM sport_events WHERE season_id = %s)),
            (SELECT SUM(steals) FROM player_statistics WHERE player_id = %s AND sport_event_id IN (SELECT id FROM sport_events WHERE season_id = %s)),
            (SELECT COUNT(*) FROM player_statistics WHERE player_id = %s AND sport_event_id IN (SELECT id FROM sport_events WHERE season_id = %s))
        )
        ON CONFLICT (player_id, season_id) DO UPDATE SET
            points_total = EXCLUDED.points_total,
            rebounds_total = EXCLUDED.rebounds_total,
            assists_total = EXCLUDED.assists_total,
            blocks_total = EXCLUDED.blocks_total,
            steals_total = EXCLUDED.steals_total,
            games_played = EXCLUDED.games_played;
    """
    cur = conn.cursor()
    cur.execute(sql, (
        player_id, season_id, player_id, season_id, player_id, season_id,
        player_id, season_id, player_id, season_id, player_id, season_id,
        player_id, season_id
    ))
    conn.commit()