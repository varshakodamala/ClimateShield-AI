import yaml
from core.extract.weather_api import WeatherAPIExtractor
from core.transform.cleaner import clean_weather
from core.transform.feature_engineering import add_features
from core.load.csv_loader import save_to_csv

def run_pipeline():
    settings = yaml.safe_load(open("config/settings.yaml"))
    cities = yaml.safe_load(open("config/cities.yaml"))["cities"]

    extractor = WeatherAPIExtractor(settings["api"]["key"])
    results = []

    for city in cities:
        raw = extractor.fetch(city)
        results.append(clean_weather(raw))

    results = add_features(results)
    save_to_csv(results)
    print("DONE")
