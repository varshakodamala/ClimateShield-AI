"""Weather API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from pathlib import Path
import yaml
from dotenv import load_dotenv

from core.extract.weather_api import WeatherAPIExtractor
from core.pipeline.weather_pipeline import WeatherPipeline
from services.api.schemas import (
    WeatherData, WeatherResponse, WeatherListResponse,
    CityRequest, CoordinatesRequest, PipelineStatusResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Load config on startup
def expand_env_vars(value):
    if isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env_vars(v) for v in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def load_config() -> dict:
    env_path = Path(__file__).parents[3] / '.env'
    load_dotenv(dotenv_path=env_path)
    config_path = Path(__file__).parents[3] / 'config' / 'settings.yaml'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        return expand_env_vars(config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

config = load_config()
extractor = WeatherAPIExtractor(config)
pipeline = WeatherPipeline(config_path=str(Path(__file__).parents[3] / 'config' / 'settings.yaml'))

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "weather-api"}

@router.post("/weather/city", response_model=WeatherResponse)
async def get_weather_by_city(request: CityRequest):
    """Get current weather data for a city."""
    try:
        data = extractor.extract(city=request.name, country=request.country)

        if data:
            return WeatherResponse(success=True, data=WeatherData(**data))
        else:
            raise HTTPException(status_code=404, detail="Weather data not found")

    except Exception as e:
        logger.error(f"Error getting weather for city {request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/city/{city_name}", response_model=WeatherResponse)
async def get_weather_by_city_name(
    city_name: str,
    country: Optional[str] = Query(None, description="Country code (ISO 3166-1 alpha-2)")
):
    """Get current weather data for a city by URL path."""
    try:
        data = extractor.extract(city=city_name, country=country)

        if data:
            return WeatherResponse(success=True, data=WeatherData(**data))
        else:
            raise HTTPException(status_code=404, detail="Weather data not found")

    except Exception as e:
        logger.error(f"Error getting weather for city {city_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weather/coordinates", response_model=WeatherResponse)
async def get_weather_by_coordinates(request: CoordinatesRequest):
    """Get current weather data for coordinates."""
    try:
        data = extractor.extract(lat=request.lat, lon=request.lon)

        if data:
            return WeatherResponse(success=True, data=WeatherData(**data))
        else:
            raise HTTPException(status_code=404, detail="Weather data not found")

    except Exception as e:
        logger.error(f"Error getting weather for coordinates ({request.lat}, {request.lon}): {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/coordinates", response_model=WeatherResponse)
async def get_weather_by_coords_query(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude")
):
    """Get current weather data for coordinates via query parameters."""
    try:
        data = extractor.extract(lat=lat, lon=lon)

        if data:
            return WeatherResponse(success=True, data=WeatherData(**data))
        else:
            raise HTTPException(status_code=404, detail="Weather data not found")

    except Exception as e:
        logger.error(f"Error getting weather for coordinates ({lat}, {lon}): {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast/city", response_model=WeatherListResponse)
async def get_forecast_by_city(request: CityRequest):
    """Get weather forecast for a city."""
    try:
        data = extractor.extract(city=request.name, country=request.country, type='forecast')

        if data and isinstance(data, list):
            weather_data = [WeatherData(**item) for item in data]
            return WeatherListResponse(success=True, data=weather_data, count=len(weather_data))
        else:
            raise HTTPException(status_code=404, detail="Forecast data not found")

    except Exception as e:
        logger.error(f"Error getting forecast for city {request.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/city/{city_name}", response_model=WeatherListResponse)
async def get_forecast_by_city_name(
    city_name: str,
    country: Optional[str] = Query(None, description="Country code")
):
    """Get weather forecast for a city by URL path."""
    try:
        data = extractor.extract(city=city_name, country=country, type='forecast')

        if data and isinstance(data, list):
            weather_data = [WeatherData(**item) for item in data]
            return WeatherListResponse(success=True, data=weather_data, count=len(weather_data))
        else:
            raise HTTPException(status_code=404, detail="Forecast data not found")

    except Exception as e:
        logger.error(f"Error getting forecast for city {city_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/run")
async def run_pipeline(
    cities: Optional[List[str]] = None,
    pipeline_type: str = Query("full", description="Pipeline type: full, incremental, forecast")
):
    """Run the weather data pipeline."""
    try:
        if pipeline_type == "full":
            success = pipeline.run_full_pipeline(cities)
        elif pipeline_type == "incremental":
            success = pipeline.run_incremental_pipeline(cities)
        elif pipeline_type == "forecast":
            success = pipeline.run_forecast_pipeline(cities)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown pipeline type: {pipeline_type}")

        if success:
            return {"success": True, "message": f"{pipeline_type.capitalize()} pipeline completed successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"{pipeline_type.capitalize()} pipeline failed")

    except Exception as e:
        logger.error(f"Error running {pipeline_type} pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipeline/status", response_model=PipelineStatusResponse)
async def get_pipeline_status():
    """Get current pipeline status."""
    try:
        status = pipeline.get_pipeline_status()
        return PipelineStatusResponse(success=True, status=status)

    except Exception as e:
        logger.error(f"Error getting pipeline status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/validate")
async def validate_pipeline():
    """Validate pipeline components."""
    try:
        validation = pipeline.validate_pipeline()
        return {
            "success": True,
            "validation": validation,
            "message": "Pipeline validation completed"
        }

    except Exception as e:
        logger.error(f"Error validating pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cities")
async def get_available_cities():
    """Get list of available cities from configuration."""
    try:
        # This would typically come from the config
        cities = [
            {"name": "New York", "country": "US"},
            {"name": "London", "country": "GB"},
            {"name": "Tokyo", "country": "JP"},
            {"name": "Sydney", "country": "AU"},
            {"name": "Paris", "country": "FR"}
        ]
        return {"success": True, "cities": cities, "count": len(cities)}

    except Exception as e:
        logger.error(f"Error getting cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
