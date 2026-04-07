"""Pydantic schemas for weather API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")

class WeatherInfo(BaseModel):
    main: str = Field(..., description="Main weather condition")
    description: str = Field(..., description="Weather description")
    icon: Optional[str] = Field(None, description="Weather icon code")

class WindInfo(BaseModel):
    speed: float = Field(..., description="Wind speed in m/s")
    direction: Optional[float] = Field(None, description="Wind direction in degrees")

class WeatherData(BaseModel):
    timestamp: datetime = Field(..., description="Data timestamp")
    city: str = Field(..., description="City name")
    country: Optional[str] = Field(None, description="Country code")
    coordinates: Coordinates
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    feels_like: Optional[float] = Field(None, description="Feels like temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    weather: WeatherInfo
    wind: WindInfo
    clouds: Optional[float] = Field(None, description="Cloud coverage percentage")
    visibility: Optional[float] = Field(None, description="Visibility in meters")
    rain: Optional[float] = Field(None, description="Rain volume in last hour (mm)")
    snow: Optional[float] = Field(None, description="Snow volume in last hour (mm)")
    sunrise: Optional[datetime] = Field(None, description="Sunrise time")
    sunset: Optional[datetime] = Field(None, description="Sunset time")

class WeatherSummary(BaseModel):
    city: str
    temperature: float
    weather_main: str
    weather_description: str
    timestamp: datetime

class CityRequest(BaseModel):
    name: str = Field(..., description="City name")
    country: Optional[str] = Field(None, description="Country code (ISO 3166-1 alpha-2)")

class CoordinatesRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lon: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")

class WeatherResponse(BaseModel):
    success: bool
    data: Optional[WeatherData] = None
    message: Optional[str] = None

class WeatherListResponse(BaseModel):
    success: bool
    data: Optional[List[WeatherData]] = None
    count: Optional[int] = None
    message: Optional[str] = None

class PipelineStatusResponse(BaseModel):
    success: bool
    status: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None