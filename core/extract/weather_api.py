import requests
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import time

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class WeatherAPIExtractor(BaseExtractor):
    """Extractor for OpenWeatherMap API."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('weather_api', {}).get('base_url', 'https://api.openweathermap.org/data/2.5')
        self.api_key = config.get('weather_api', {}).get('api_key')
        self.units = config.get('weather_api', {}).get('units', 'metric')

    def validate_connection(self) -> bool:
        """Validate API connection by making a test request."""
        if not self.api_key:
            self.logger.error("Missing OpenWeatherMap API key. Set OPENWEATHER_API_KEY in the environment or config file.")
            return False

        try:
            # Test with a simple city
            test_params = {
                'q': 'London',
                'appid': self.api_key,
                'units': self.units
            }
            response = requests.get(f"{self.base_url}/weather", params=test_params, timeout=10)
            response.raise_for_status()
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False

    def extract_weather_by_city(self, city_name: str, country_code: str = None) -> Optional[Dict[str, Any]]:
        """Extract current weather data for a specific city."""
        try:
            params = {
                'q': f"{city_name},{country_code}" if country_code else city_name,
                'appid': self.api_key,
                'units': self.units
            }

            response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self._transform_weather_data(data)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to extract weather for {city_name}: {e}")
            return None

    def extract_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Extract current weather data for coordinates."""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units
            }

            response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self._transform_weather_data(data)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to extract weather for coordinates ({lat}, {lon}): {e}")
            return None

    def extract_forecast_by_city(self, city_name: str, country_code: str = None) -> Optional[List[Dict[str, Any]]]:
        """Extract 5-day weather forecast for a specific city."""
        try:
            params = {
                'q': f"{city_name},{country_code}" if country_code else city_name,
                'appid': self.api_key,
                'units': self.units
            }

            response = requests.get(f"{self.base_url}/forecast", params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return [self._transform_weather_data(item) for item in data.get('list', [])]

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to extract forecast for {city_name}: {e}")
            return None

    def extract(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Main extract method - supports different extraction modes."""
        extraction_type = kwargs.get('type', 'current')
        city = kwargs.get('city')
        country = kwargs.get('country')
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')

        if extraction_type == 'current':
            if city:
                return self.extract_weather_by_city(city, country)
            elif lat is not None and lon is not None:
                return self.extract_weather_by_coordinates(lat, lon)
        elif extraction_type == 'forecast':
            if city:
                return self.extract_forecast_by_city(city, country)

        self.logger.error("Invalid extraction parameters")
        return None

    def _transform_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw API response to standardized format."""
        try:
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0] if data.get('weather') else {}
            wind = data.get('wind', {})
            clouds = data.get('clouds', {})
            sys = data.get('sys', {})

            transformed = {
                'timestamp': datetime.fromtimestamp(data.get('dt', time.time())),
                'city': data.get('name'),
                'country': sys.get('country'),
                'coordinates': {
                    'lat': data.get('coord', {}).get('lat'),
                    'lon': data.get('coord', {}).get('lon')
                },
                'temperature': main.get('temp'),
                'feels_like': main.get('feels_like'),
                'humidity': main.get('humidity'),
                'pressure': main.get('pressure'),
                'weather': {
                    'main': weather.get('main'),
                    'description': weather.get('description'),
                    'icon': weather.get('icon')
                },
                'wind': {
                    'speed': wind.get('speed'),
                    'direction': wind.get('deg')
                },
                'clouds': clouds.get('all'),
                'visibility': data.get('visibility'),
                'rain': data.get('rain', {}).get('1h'),
                'snow': data.get('snow', {}).get('1h'),
                'sunrise': datetime.fromtimestamp(sys.get('sunrise', 0)) if sys.get('sunrise') else None,
                'sunset': datetime.fromtimestamp(sys.get('sunset', 0)) if sys.get('sunset') else None
            }

            return transformed

        except Exception as e:
            self.logger.error(f"Failed to transform weather data: {e}")
            return {}
