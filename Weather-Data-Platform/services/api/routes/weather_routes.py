from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/weather")
def get_weather():
    return pd.read_csv("data/processed/weather.csv").to_dict(orient="records")
