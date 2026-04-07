# 🌤️ Weather Data Platform - Quick Start

## Running the Platform

### Option 1: PowerShell (Windows)
```powershell
# Start API Server
.\run.ps1 api

# Start Dashboard (in another terminal)
.\run.ps1 dashboard

# Run Pipeline
.\run.ps1 pipeline

# Validate Setup
.\run.ps1 validate
```

### Option 2: Command Prompt (Windows)
```cmd
# Start API Server
run.bat api

# Start Dashboard (in another terminal)
run.bat dashboard

# Run Pipeline
run.bat pipeline

# Validate Setup
run.bat validate
```

### Option 3: Bash/Linux/Mac
```bash
# Make script executable
chmod +x run.sh

# Start API Server
./run.sh api

# Start Dashboard (in another terminal)
./run.sh dashboard

# Run Pipeline
./run.sh pipeline

# Validate Setup
./run.sh validate
```

### Option 4: Direct Python (if venv is activated)
```bash
python main.py api        # Start API
python main.py dashboard  # Start Dashboard
python main.py pipeline   # Run ETL Pipeline
python main.py validate   # Validate Setup
```

## Accessing the Services

- **Weather API Documentation**: http://localhost:8000/docs
- **Weather API ReDoc**: http://localhost:8000/redoc
- **Dashboard**: http://localhost:8501

## Features

✅ **Real-time Weather Data**: Fetch current weather data from OpenWeatherMap API
✅ **Data Pipeline**: Automated ETL pipeline for weather data extraction, transformation, and loading
✅ **Interactive Dashboard**: Streamlit dashboard with visualizations
✅ **REST API**: FastAPI with comprehensive endpoints
✅ **Database Support**: PostgreSQL, CSV, and AWS S3 storage
✅ **Monitoring & Alerts**: Email notifications and logging
✅ **Airflow Orchestration**: Automated data pipelines with Apache Airflow
✅ **Docker Support**: Containerized deployment

## Configuration

Edit `config/settings.yaml` to configure:
- Weather API settings (API key, units, cities)
- Database connection (PostgreSQL)
- S3 bucket details
- Email alerts
- Logging levels

## Environment Variables

Create `.env` file:
```bash
OPENWEATHER_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost/weather_db
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Troubleshooting

**Port already in use**:
- API uses port 8000
- Dashboard uses port 8501
- Change ports in `config/settings.yaml` if needed

**Database connection fails**:
- Ensure PostgreSQL is running
- Check credentials in config/settings.yaml
- Create database: `createdb weather_db`

**API key errors**:
- Get free API key from: https://openweathermap.org/api
- Set it in environment or config file

## Architecture

```
Weather Platform
├── Extract (OpenWeatherMap API)
├── Transform (Cleaning, Unit Conversion, Feature Engineering)
├── Load (CSV, Database, S3)
├── API (FastAPI)
├── Dashboard (Streamlit)
├── Monitoring (Logging, Alerts)
└── Orchestration (Airflow DAGs)
```

## Testing

Run tests:
```bash
pytest tests/test_pipeline.py -v
```

All 18 tests should pass ✓

## Notes

- Virtual environment is located in `.venv`
- Logs are stored in `logs/` directory
- Raw data in `data/raw/`, processed data in `data/processed/`
- Ensure all parent directories in paths exist before running
