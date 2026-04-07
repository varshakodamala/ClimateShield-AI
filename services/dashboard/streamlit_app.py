"""Weather Dashboard using Streamlit."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, List, Optional
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Weather Data Platform",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
@st.cache_data
def expand_env_vars(value):
    if isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env_vars(v) for v in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


@st.cache_data
def load_config():
    """Load configuration from settings.yaml and expand environment variables."""
    try:
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        return expand_env_vars(config)
    except Exception as e:
        logger.warning(f"Could not load config: {e}")
        return {}

# API client class
class WeatherAPIClient:
    """Client for interacting with the Weather API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def get_weather_by_city(self, city: str, country: Optional[str] = None) -> Optional[Dict]:
        """Get weather data for a city."""
        try:
            params = {"country": country} if country else {}
            response = requests.get(f"{self.base_url}/api/v1/weather/city/{city}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting weather for {city}: {e}")
            return None

    def get_forecast_by_city(self, city: str, country: Optional[str] = None) -> Optional[List[Dict]]:
        """Get forecast data for a city."""
        try:
            params = {"country": country} if country else {}
            response = requests.get(f"{self.base_url}/api/v1/forecast/city/{city}", params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except Exception as e:
            logger.error(f"Error getting forecast for {city}: {e}")
            return None

    def get_pipeline_status(self) -> Optional[Dict]:
        """Get pipeline status."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/pipeline/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")
            return None

    def run_pipeline(self, pipeline_type: str = "full") -> bool:
        """Run the data pipeline."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/pipeline/run",
                params={"pipeline_type": pipeline_type}
            )
            response.raise_for_status()
            return response.json().get('success', False)
        except Exception as e:
            logger.error(f"Error running pipeline: {e}")
            return False

# Initialize API client
config = load_config()
api_base_url = config.get('api', {}).get('base_url', 'http://localhost:8000')
api_client = WeatherAPIClient(api_base_url)

# Sidebar
st.sidebar.title("🌤️ Weather Dashboard")

# City selection
st.sidebar.subheader("City Selection")
cities = [
    "New York", "London", "Tokyo", "Sydney", "Paris",
    "Berlin", "Moscow", "Beijing", "Mumbai", "São Paulo"
]

selected_city = st.sidebar.selectbox("Select City", cities)

# Country mapping (simplified)
country_codes = {
    "New York": "US",
    "London": "GB",
    "Tokyo": "JP",
    "Sydney": "AU",
    "Paris": "FR",
    "Berlin": "DE",
    "Moscow": "RU",
    "Beijing": "CN",
    "Mumbai": "IN",
    "São Paulo": "BR"
}

# Pipeline controls
st.sidebar.subheader("Data Pipeline")
if st.sidebar.button("🔄 Run Full Pipeline"):
    with st.spinner("Running pipeline..."):
        success = api_client.run_pipeline("full")
        if success:
            st.sidebar.success("Pipeline completed successfully!")
        else:
            st.sidebar.error("Pipeline failed!")

if st.sidebar.button("📊 Update Current Data"):
    with st.spinner("Updating current data..."):
        success = api_client.run_pipeline("incremental")
        if success:
            st.sidebar.success("Data updated!")
        else:
            st.sidebar.error("Update failed!")

# Pipeline status
st.sidebar.subheader("Pipeline Status")
status_data = api_client.get_pipeline_status()
if status_data and status_data.get('success'):
    status = status_data.get('status', {})
    st.sidebar.metric("Database Records", status.get('database_records', 0))
    st.sidebar.metric("S3 Objects", status.get('s3_objects', 0))

# Main content
st.title("🌤️ Weather Data Platform Dashboard")

# Current weather section
st.header("Current Weather")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 Get Current Weather", key="current_weather"):
        with st.spinner(f"Fetching weather for {selected_city}..."):
            weather_data = api_client.get_weather_by_city(selected_city, country_codes.get(selected_city))

            if weather_data and weather_data.get('success'):
                data = weather_data['data']

                if not isinstance(data, dict):
                    st.error("Weather API returned an unexpected data format.")
                else:
                    # Temperature card
                    st.metric(
                        "Temperature",
                        f"{data.get('temperature', 'N/A')}°C",
                        f"Feels like {data.get('feels_like', 'N/A')}°C"
                    )

                    # Weather condition
                    weather_info = data.get('weather', {})
                    st.write(f"**{weather_info.get('main', 'N/A')}**")
                    st.write(f"*{weather_info.get('description', 'N/A')}*")

                    # Additional metrics
                    col_temp, col_humid, col_wind = st.columns(3)
                    with col_temp:
                        st.metric("Humidity", f"{data.get('humidity', 'N/A')}%")
                    with col_humid:
                        st.metric("Pressure", f"{data.get('pressure', 'N/A')} hPa")
                    with col_wind:
                        st.metric("Wind Speed", f"{data.get('wind', {}).get('speed', 'N/A')} m/s")

                    # Store data for charts
                    st.session_state.current_weather = data
            else:
                st.error("Failed to fetch weather data")

with col2:
    st.subheader("Weather Details")
    if 'current_weather' in st.session_state:
        data = st.session_state.current_weather
        
        # Type check to ensure data is a dictionary
        if not isinstance(data, dict):
            st.error("Invalid weather data format. Please fetch weather data first.")
        else:
            # Create a nice info display
            info_items = {
                "City": data.get('city', 'N/A'),
                "Country": data.get('country', 'N/A'),
                "Coordinates": ".2f",
                "Visibility": ".0f",
                "Cloud Coverage": ".0f",
                "Sunrise": data.get('sunrise', 'N/A'),
                "Sunset": data.get('sunset', 'N/A')
            }

            for key, value in info_items.items():
                if key == "Coordinates" and 'coordinates' in data:
                    st.write(f"**{key}:** {data['coordinates']['lat']:.2f}, {data['coordinates']['lon']:.2f}")
                elif key in ["Sunrise", "Sunset"] and value != 'N/A':
                    st.write(f"**{key}:** {pd.to_datetime(value).strftime('%H:%M')}")
                else:
                    st.write(f"**{key}:** {value}")
    else:
        st.info("Click 'Get Current Weather' button to fetch data")

with col3:
    st.subheader("Weather Map")
    # Placeholder for weather map
    st.info("Interactive weather map would be displayed here")

# Forecast section
st.header("5-Day Weather Forecast")

if st.button("📅 Get Forecast", key="forecast"):
    with st.spinner(f"Fetching forecast for {selected_city}..."):
        forecast_data = api_client.get_forecast_by_city(selected_city, country_codes.get(selected_city))

        if forecast_data:
            # Convert to DataFrame for easier plotting
            df = pd.DataFrame(forecast_data)

            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Temperature chart
            fig_temp = px.line(
                df,
                x='timestamp',
                y='temperature',
                title='Temperature Forecast',
                labels={'temperature': 'Temperature (°C)', 'timestamp': 'Time'}
            )
            fig_temp.add_scatter(x=df['timestamp'], y=df['feels_like'], mode='lines', name='Feels Like')
            st.plotly_chart(fig_temp, use_container_width=True)

            # Humidity and Pressure
            col1, col2 = st.columns(2)

            with col1:
                fig_humidity = px.line(
                    df,
                    x='timestamp',
                    y='humidity',
                    title='Humidity Forecast',
                    labels={'humidity': 'Humidity (%)', 'timestamp': 'Time'}
                )
                st.plotly_chart(fig_humidity, use_container_width=True)

            with col2:
                fig_pressure = px.line(
                    df,
                    x='timestamp',
                    y='pressure',
                    title='Pressure Forecast',
                    labels={'pressure': 'Pressure (hPa)', 'timestamp': 'Time'}
                )
                st.plotly_chart(fig_pressure, use_container_width=True)

            # Wind speed
            fig_wind = px.line(
                df,
                x='timestamp',
                y=df['wind'].apply(lambda x: x['speed'] if isinstance(x, dict) else 0),
                title='Wind Speed Forecast',
                labels={'y': 'Wind Speed (m/s)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_wind, use_container_width=True)

            # Store forecast data
            st.session_state.forecast_data = df
        else:
            st.error("Failed to fetch forecast data")

# Data Analysis section
st.header("Data Analysis")

if 'forecast_data' in st.session_state:
    df = st.session_state.forecast_data

    # Summary statistics
    st.subheader("Forecast Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Temperature", ".1f")
    with col2:
        st.metric("Max Temperature", ".1f")
    with col3:
        st.metric("Min Temperature", ".1f")
    with col4:
        st.metric("Avg Humidity", ".1f")

    # Weather conditions distribution
    st.subheader("Weather Conditions Distribution")

    weather_counts = df['weather'].apply(lambda x: x['main'] if isinstance(x, dict) else 'Unknown').value_counts()

    fig_pie = px.pie(
        values=weather_counts.values,
        names=weather_counts.index,
        title='Weather Conditions Distribution'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*Weather Data Platform Dashboard - Powered by Streamlit*")

# Auto-refresh (optional)
if st.sidebar.checkbox("Auto-refresh every 5 minutes"):
    time_to_refresh = 300  # 5 minutes
    st.empty()
    st.info(f"Dashboard will refresh in {time_to_refresh} seconds")

    # In a real implementation, you'd use st.rerun() with a timer
    # For now, just show the countdown
    import time
    countdown_placeholder = st.empty()

    for i in range(time_to_refresh, 0, -1):
        countdown_placeholder.text(f"Next refresh in {i} seconds...")
        time.sleep(1)

    st.rerun()
