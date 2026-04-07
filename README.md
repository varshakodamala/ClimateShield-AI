# Weather Data Platform

A comprehensive weather data platform that extracts, transforms, and loads weather data from various sources, provides APIs and dashboards for data access, and includes monitoring and alerting capabilities.

## Features

- **Data Extraction**: Collect weather data from OpenWeatherMap API
- **Data Transformation**: Clean, validate, and engineer features from raw weather data
- **Data Loading**: Store data in CSV, database (PostgreSQL), and cloud storage (S3)
- **REST API**: FastAPI-based API for accessing weather data
- **Dashboard**: Streamlit-based interactive dashboard
- **Monitoring**: Comprehensive logging and alerting system
- **Orchestration**: Apache Airflow for workflow automation
- **Containerization**: Docker and Docker Compose support

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Extract &      │───▶│   Transform &   │
│                 │    │  Validate       │    │   Clean Data    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   REST API      │◀───│   Dashboard     │             │
│   (FastAPI)     │    │  (Streamlit)    │             │
└─────────────────┘    └─────────────────┘             │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CSV Files     │    │   PostgreSQL    │    │   AWS S3        │
│                 │    │   Database      │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
weather-data-platform/
├── config/
│   ├── settings.yaml          # Application configuration
│   └── cities.yaml            # City definitions
├── core/
│   ├── extract/
│   │   ├── base_extractor.py  # Abstract extractor class
│   │   └── weather_api.py     # OpenWeatherMap API extractor
│   ├── transform/
│   │   ├── cleaner.py         # Data cleaning utilities
│   │   ├── unit_converter.py  # Unit conversion utilities
│   │   └── feature_engineering.py # Feature engineering
│   ├── load/
│   │   ├── csv_loader.py      # CSV data loader
│   │   ├── db_loader.py       # Database loader
│   │   └── s3_loader.py       # S3 loader
│   └── pipeline/
│       └── weather_pipeline.py # Main ETL pipeline
├── services/
│   ├── api/
│   │   ├── main.py            # FastAPI application
│   │   ├── routes/
│   │   │   └── weather_routes.py # API routes
│   │   └── schemas.py         # Pydantic schemas
│   └── dashboard/
│       └── streamlit_app.py   # Streamlit dashboard
├── monitoring/
│   ├── logger.py              # Logging configuration
│   └── alerts.py              # Alerting system
├── orchestration/
│   └── airflow/
│       ├── dags/
│       │   ├── weather_pipeline.py     # ETL DAG
│       │   ├── alert_pipeline.py       # Monitoring DAG
│       │   └── weather_aggregation.py  # Analytics DAG
│       └── plugins/           # Airflow plugins
├── tests/
│   └── test_pipeline.py       # Unit tests
├── docker/
│   ├── Dockerfile             # Docker image
│   └── docker-compose.yml     # Docker Compose
├── data/                      # Data directories
├── logs/                      # Log files
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, for database storage)
- AWS account (optional, for S3 storage)
- OpenWeatherMap API key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd weather-data-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy and edit configuration files
   cp config/settings.yaml config/settings.local.yaml
   # Edit settings.local.yaml with your API keys and database credentials
   ```

5. **Set environment variables**
   ```bash
   export OPENWEATHER_API_KEY="your_api_key_here"
   export DB_PASSWORD="your_db_password"
   # Add other required environment variables
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   cd docker
   docker-compose up --build
   ```

## Usage

### Running the Pipeline

```bash
# Run full pipeline
python main.py pipeline --pipeline-type full

# Run incremental pipeline
python main.py pipeline --pipeline-type incremental

# Run forecast pipeline
python main.py pipeline --pipeline-type forecast

# Specify cities
python main.py pipeline --cities "New York" "London" "Tokyo"
```

### Running the API

```bash
python main.py api
```

The API will be available at `http://localhost:8000`

### Running the Dashboard

```bash
python main.py dashboard
```

The dashboard will be available at `http://localhost:8501`

### Running Tests

```bash
python -m pytest tests/
```

### Validation

```bash
python main.py validate
```

## API Documentation

### Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/weather/city/{city_name}` - Get weather by city
- `POST /api/v1/weather/city` - Get weather by city (POST)
- `GET /api/v1/forecast/city/{city_name}` - Get forecast by city
- `POST /api/v1/pipeline/run` - Run data pipeline
- `GET /api/v1/pipeline/status` - Get pipeline status

### Example API Usage

```python
import requests

# Get current weather
response = requests.get("http://localhost:8000/api/v1/weather/city/London")
weather_data = response.json()

# Get forecast
response = requests.get("http://localhost:8000/api/v1/forecast/city/London")
forecast_data = response.json()
```

## Configuration

### settings.yaml

```yaml
weather_api:
  base_url: "https://api.openweathermap.org/data/2.5"
  api_key: "${OPENWEATHER_API_KEY}"
  units: "metric"

database:
  host: "localhost"
  port: 5432
  name: "weather_db"
  user: "weather_user"
  password: "${DB_PASSWORD}"

# ... other configurations
```

### cities.yaml

```yaml
cities:
  - name: "New York"
    country: "US"
    lat: 40.7128
    lon: -74.0060
  # ... more cities
```

## Monitoring and Alerting

The platform includes comprehensive monitoring:

- **Logging**: Structured logging with file rotation
- **Metrics**: Performance and data quality metrics
- **Alerts**: Email alerts for system issues and weather thresholds
- **Health Checks**: Automated health monitoring

## Orchestration with Airflow

The platform uses Apache Airflow for workflow orchestration:

- **weather_pipeline**: Hourly ETL pipeline
- **alert_pipeline**: 30-minute monitoring and alerting
- **weather_aggregation**: Daily analytics and reporting

## Data Model

### Weather Data Schema

```sql
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    temperature FLOAT,
    feels_like FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    weather_main VARCHAR(50),
    weather_description TEXT,
    wind_speed FLOAT,
    wind_direction FLOAT,
    clouds FLOAT,
    visibility FLOAT,
    rain_1h FLOAT,
    snow_1h FLOAT,
    sunrise TIMESTAMP,
    sunset TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Check the logs in the `logs/` directory
- Review the API documentation at `http://localhost:8000/docs`
- Check the dashboard for system status
- Review the test results for any issues

## Roadmap

- [ ] Add support for additional weather APIs
- [ ] Implement machine learning models for weather prediction
- [ ] Add real-time weather streaming
- [ ] Enhance dashboard with more visualizations
- [ ] Add support for weather alerts and notifications
- [ ] Implement data archiving and retention policies
