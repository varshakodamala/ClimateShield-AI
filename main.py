"""Main entry point for the Weather Data Platform."""

import argparse
import logging
import sys
import os
from pathlib import Path
import yaml

# Add project root to Python path ONCE at entry point
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from core.pipeline.weather_pipeline import WeatherPipeline
from monitoring.logger import initialize_logging
from services.api.main import app as api_app
import uvicorn

def load_config(config_path: str = 'config/settings.yaml') -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def setup_logging(config: dict):
    """Initialize logging system."""
    initialize_logging(config)

def run_pipeline(config: dict, pipeline_type: str = 'full', cities: list = None):
    """Run the weather data pipeline."""
    logger = logging.getLogger(__name__)

    try:
        pipeline = WeatherPipeline()

        logger.info(f"Starting {pipeline_type} pipeline")

        if pipeline_type == 'full':
            success = pipeline.run_full_pipeline(cities)
        elif pipeline_type == 'incremental':
            success = pipeline.run_incremental_pipeline(cities)
        elif pipeline_type == 'forecast':
            success = pipeline.run_forecast_pipeline(cities)
        else:
            logger.error(f"Unknown pipeline type: {pipeline_type}")
            return False

        if success:
            logger.info(f"{pipeline_type.capitalize()} pipeline completed successfully")
            return True
        else:
            logger.error(f"{pipeline_type.capitalize()} pipeline failed")
            return False

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return False

def run_api_server(config: dict):
    """Run the FastAPI server."""
    logger = logging.getLogger(__name__)

    try:
        host = config.get('api', {}).get('host', '0.0.0.0')
        port = config.get('api', {}).get('port', 8000)

        logger.info(f"Starting API server on {host}:{port}")
        uvicorn.run(
            api_app,
            host=host,
            port=port,
            log_level="info"
        )

    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)

def run_dashboard(config: dict):
    """Run the Streamlit dashboard."""
    logger = logging.getLogger(__name__)

    try:
        import subprocess
        import os

        dashboard_path = Path(__file__).parent / 'services' / 'dashboard' / 'streamlit_app.py'

        logger.info("Starting Streamlit dashboard")

        # Run streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', str(dashboard_path)]
        subprocess.run(cmd)

    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")
        sys.exit(1)

def validate_setup(config: dict) -> bool:
    """Validate the platform setup."""
    logger = logging.getLogger(__name__)

    logger.info("Validating platform setup...")

    pipeline = WeatherPipeline()
    validation = pipeline.validate_pipeline()

    if validation.get('overall_success'):
        logger.info("✅ Platform setup validation passed")
        return True
    else:
        logger.error("❌ Platform setup validation failed")
        failed_components = [
            component for component, success in validation.items()
            if component != 'overall_success' and not success
        ]
        logger.error(f"Failed components: {', '.join(failed_components)}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Weather Data Platform')
    parser.add_argument(
        'command',
        choices=['pipeline', 'api', 'dashboard', 'validate'],
        help='Command to run'
    )
    parser.add_argument(
        '--config',
        default='config/settings.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--pipeline-type',
        choices=['full', 'incremental', 'forecast'],
        default='full',
        help='Type of pipeline to run'
    )
    parser.add_argument(
        '--cities',
        nargs='*',
        help='List of cities to process'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Setup logging
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("Weather Data Platform starting...")

    # Execute command
    if args.command == 'pipeline':
        success = run_pipeline(config, args.pipeline_type, args.cities)
        sys.exit(0 if success else 1)

    elif args.command == 'api':
        run_api_server(config)

    elif args.command == 'dashboard':
        run_dashboard(config)

    elif args.command == 'validate':
        success = validate_setup(config)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
