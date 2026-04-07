from fastapi import FastAPI
from services.api.routes.weather_routes import router

app = FastAPI()
app.include_router(router)
