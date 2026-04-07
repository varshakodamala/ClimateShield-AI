def add_features(data):
    for r in data:
        r["temp_category"] = "Hot" if r["temperature"] > 30 else "Normal"
    return data
