import requests
import time

class SportRadarClient:
    def __init__(self, api_key, base_url, locale):
        self.api_key = api_key
        self.base_url = base_url
        self.locale = locale
        self.session = requests.Session()

    def _get_request(self, endpoint, params=None):
        """Método privado para manejar las solicitudes GET, errores y reintentos."""
        url = f"{self.base_url}/{self.locale}/{endpoint}"
        
        full_params = {"api_key": self.api_key}
        if params:
            full_params.update(params)

        retries = 5
        delay = 30

        for i in range(retries):
            try:
                response = self.session.get(url, params=full_params, headers={"accept": "application/json"})
                
                if response.status_code == 429:
                    print(f"Error 429: Too Many Requests. Reintentando en {delay} segundos...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"Error al llamar a la API para el endpoint {endpoint}")
                return None
        
        print(f"Fallo en la solicitud después de {retries} reintentos.")
        return None


    def get_competition_seasons(self, urn_competition):
        """Obtiene todas las temporadas para una competición."""
        endpoint = f"competitions/{urn_competition}/seasons"
        return self._get_request(endpoint)

    def get_season_summaries(self, urn_season, limit=200, offset=0):
        """Obtiene resúmenes de eventos deportivos para una temporada con paginación."""
        endpoint = f"seasons/{urn_season}/summaries"
        params = {"limit": limit, "offset": offset}
        return self._get_request(endpoint, params)

    def get_sport_event_summary(self, urn_sport_event):
        """Obtiene el resumen detallado de un evento deportivo."""
        endpoint = f"sport_events/{urn_sport_event}/summary"
        return self._get_request(endpoint)

    def get_season_competitor_statistics(self, urn_season, urn_competitor):
        """Obtiene las estadísticas de un equipo y sus jugadores para una temporada."""
        endpoint = f"seasons/{urn_season}/competitors/{urn_competitor}/statistics"
        return self._get_request(endpoint)

    def get_season_standings(self, urn_season, live=False):
        """Obtiene la clasificación de una temporada."""
        endpoint = f"seasons/{urn_season}/standings"
        params = {"live": live}
        return self._get_request(endpoint, params)