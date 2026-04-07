import requests
from core.extract.base_extractor import BaseExtractor

class WeatherAPIExtractor(BaseExtractor):
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch(self, city):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"
        return requests.get(url).json()
