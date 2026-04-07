import requests
urls = [
    'http://localhost:8000/api/v1/health',
    'http://localhost:8000/api/v1/weather/city/New York?country=US',
    'http://localhost:8000/api/v1/forecast/city/New York?country=US',
    'http://localhost:8000/api/v1/pipeline/status',
]
for u in urls:
    try:
        r = requests.get(u, timeout=10)
        print(u, r.status_code)
        print(r.text[:500])
    except Exception as e:
        print(u, 'ERROR', e)
