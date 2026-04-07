def check_alerts(data):
    return [f"🔥 Heat alert {r['city']}" for r in data if r["temperature"] > 40]
