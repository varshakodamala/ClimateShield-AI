from core.transform.unit_converter import kelvin_to_celsius

def clean_weather(data):
    return {
        "city": data.get("name"),
        "temperature": kelvin_to_celsius(data["main"]["temp"]),
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"]
    }
