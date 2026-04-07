"""Airflow DAG for weather data pipeline."""

from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add project root to path for Airflow context
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

from airflow import DAG  # type: ignore[reportMissingImports]
from airflow.operators.python import PythonOperator  # type: ignore[reportMissingImports]
from airflow.operators.bash import BashOperator  # type: ignore[reportMissingImports]

from core.pipeline.weather_pipeline import WeatherPipeline

default_args = {
    'owner': 'weather_platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

dag = DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='Weather data extraction, transformation, and loading pipeline',
    schedule_interval=timedelta(hours=1),  # Run every hour
    max_active_runs=1,
    tags=['weather', 'etl'],
)

def run_weather_pipeline(**context):
    """Run the weather data pipeline."""
    pipeline = WeatherPipeline()

    # Get cities from DAG config or use defaults
    cities = context['dag_run'].conf.get('cities', None)

    success = pipeline.run_full_pipeline(cities)

    if not success:
        raise Exception("Weather pipeline failed")

    return "Pipeline completed successfully"

def validate_pipeline(**context):
    """Validate pipeline components."""
    pipeline = WeatherPipeline()
    validation = pipeline.validate_pipeline()

    if not validation.get('overall_success', False):
        failed_components = [
            component for component, success in validation.items()
            if component != 'overall_success' and not success
        ]
        raise Exception(f"Pipeline validation failed for: {', '.join(failed_components)}")

    return "Pipeline validation passed"

# Tasks
validate_task = PythonOperator(
    task_id='validate_pipeline',
    python_callable=validate_pipeline,
    dag=dag,
)

extract_transform_load_task = PythonOperator(
    task_id='extract_transform_load',
    python_callable=run_weather_pipeline,
    dag=dag,
)

# Data quality check task
data_quality_check = BashOperator(
    task_id='data_quality_check',
    bash_command='cd /app && python -m pytest tests/test_pipeline.py::TestDataCleaner -v',
    dag=dag,
)

# Set task dependencies
validate_task >> extract_transform_load_task >> data_quality_check
