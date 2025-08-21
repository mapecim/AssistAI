import time
from etl.basic.api.sportradar_client import SportRadarClient
from etl.basic.database.database import (
    connect, create_tables, insert_competition, insert_season,
    insert_team, insert_sport_event_summary, insert_team_statistics,
    insert_player_statistics, insert_player, update_season_player_statistics
)
from config import API_KEY, BASE_URL, LOCALE, LEAGUE_URNS

def fetch_and_store_data():
    """Función principal para orquestar la obtención y almacenamiento de datos."""
    if not API_KEY:
        print("Error: La clave de API no está definida en el archivo .env")
        return
    
    client = SportRadarClient(API_KEY, BASE_URL, LOCALE)
    db_conn = connect()

    if not db_conn:
        print("No se pudo conectar a la base de datos. Saliendo.")
        return

    create_tables()

    for league_name, competition_urn in LEAGUE_URNS.items():
        print(f"🔄 Procesando la liga: {league_name} ({competition_urn})...")

        insert_competition(db_conn, {'id': competition_urn, 'name': league_name})

        seasons_data = client.get_competition_seasons(competition_urn)
        if not seasons_data:
            continue

        for season in seasons_data.get('seasons', []):
            print(f"  > Procesando temporada: {season.get('name')}")
            insert_season(db_conn, season, competition_urn)

            offset = 0
            limit = 200
            while True:
                summaries_data = client.get_season_summaries(season.get('id'), limit=limit, offset=offset)
                if not summaries_data or not summaries_data.get('summaries'):
                    break

                for summary in summaries_data['summaries']:
                    sport_event_urn = summary['sport_event']['id']
                    print(f"    - Obteniendo resumen detallado para el partido: {sport_event_urn}")

                    competitors = summary.get('sport_event', {}).get('competitors', [])
                    for competitor in competitors:
                        insert_team(db_conn, competitor)
                    
                    insert_sport_event_summary(db_conn, summary)

                    detailed_summary = client.get_sport_event_summary(sport_event_urn)
                    if detailed_summary and 'statistics' in detailed_summary:
                        competitors_stats = detailed_summary['statistics']['totals']['competitors']
                        if len(competitors_stats) == 2:
                            home, away = competitors_stats
                            insert_team_statistics(db_conn, sport_event_urn, home, away)
                            insert_team_statistics(db_conn, sport_event_urn, away, home)

                            if 'players' in home:
                                for player_stats in home['players']:
                                    player_id = player_stats.get('id')
                                    insert_player(db_conn, player_stats, home['id'], season.get('id'))
                                    insert_player_statistics(db_conn, sport_event_urn, player_stats)

                                    update_season_player_statistics(db_conn, player_id, season.get('id'))

                    time.sleep(1)

                offset += limit

    db_conn.close()
    print("✅ Proceso de recolección de datos completado.")

if __name__ == '__main__':
    fetch_and_store_data()