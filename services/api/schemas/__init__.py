"""Pydantic schemas for Weather API."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CoordinatesRequest(BaseModel):
    """Request model for coordinates-based weather queries."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")

class CityRequest(BaseModel):
    """Request model for city-based weather queries."""
    name: str = Field(..., min_length=1, max_length=100, description="City name")
    country: Optional[str] = Field(None, min_length=2, max_length=3, description="Country code (ISO 3166-1 alpha-2)")

class WeatherData(BaseModel):
    """Weather data model."""
    timestamp: Optional[datetime] = Field(None, description="Data timestamp")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country code")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Geographic coordinates")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    feels_like: Optional[float] = Field(None, description="Feels like temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    weather_main: Optional[str] = Field(None, description="Main weather condition")
    weather_description: Optional[str] = Field(None, description="Detailed weather description")
    weather_icon: Optional[str] = Field(None, description="Weather icon code")
    wind_speed: Optional[float] = Field(None, description="Wind speed in m/s")
    wind_direction: Optional[float] = Field(None, description="Wind direction in degrees")
    clouds: Optional[float] = Field(None, description="Cloudiness percentage")
    visibility: Optional[float] = Field(None, description="Visibility in meters")
    rain_1h: Optional[float] = Field(None, description="Rain volume for last hour in mm")
    snow_1h: Optional[float] = Field(None, description="Snow volume for last hour in mm")
    sunrise: Optional[datetime] = Field(None, description="Sunrise time")
    sunset: Optional[datetime] = Field(None, description="Sunset time")

    # Additional computed fields
    hour: Optional[int] = Field(None, description="Hour of the day")
    day_of_week: Optional[int] = Field(None, description="Day of week (0=Monday)")
    season: Optional[str] = Field(None, description="Season")
    temperature_category: Optional[str] = Field(None, description="Temperature category")

    class Config:
        from_attributes = True

class WeatherResponse(BaseModel):
    """Response model for single weather data."""
    success: bool = Field(..., description="Request success status")
    data: Optional[WeatherData] = Field(None, description="Weather data")
    message: Optional[str] = Field(None, description="Response message")

class WeatherListResponse(BaseModel):
    """Response model for multiple weather data records."""
    success: bool = Field(..., description="Request success status")
    data: List[WeatherData] = Field(default_factory=list, description="List of weather data")
    count: int = Field(0, description="Number of records")
    message: Optional[str] = Field(None, description="Response message")

class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status."""
    success: bool = Field(..., description="Pipeline success status")
    status: str = Field(..., description="Pipeline status")
    message: Optional[str] = Field(None, description="Status message")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    records_processed: Optional[int] = Field(None, description="Number of records processed")

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")