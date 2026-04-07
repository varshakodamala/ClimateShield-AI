"""Airflow DAG for weather data aggregation and analytics."""

from datetime import datetime, timedelta
from airflow import DAG  # type: ignore[reportMissingImports]
from airflow.operators.python import PythonOperator  # type: ignore[reportMissingImports]
from airflow.operators.bash import BashOperator  # type: ignore[reportMissingImports]
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

default_args = {
    'owner': 'weather_platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
}

dag = DAG(
    'weather_aggregation_pipeline',
    default_args=default_args,
    description='Weather data aggregation and analytics pipeline',
    schedule_interval='@daily',  # Run daily
    max_active_runs=1,
    tags=['weather', 'analytics', 'aggregation'],
)

def aggregate_daily_weather(**context):
    """Aggregate weather data for the previous day."""
    # This would typically read from database and create daily aggregations
    # For now, create sample aggregations

    execution_date = context['execution_date']
    target_date = execution_date - timedelta(days=1)

    print(f"Aggregating weather data for {target_date.strftime('%Y-%m-%d')}")

    # Sample aggregation logic
    aggregations = {
        'date': target_date.strftime('%Y-%m-%d'),
        'cities_covered': 5,
        'avg_temperature_global': 22.5,
        'max_temperature': 35.2,
        'min_temperature': 5.8,
        'total_records': 120,
        'data_quality_score': 0.95
    }

    # Save aggregations (would save to database in production)
    context['ti'].xcom_push(key='daily_aggregations', value=aggregations)

    return f"Daily aggregation completed for {target_date.strftime('%Y-%m-%d')}"

def generate_weather_insights(**context):
    """Generate weather insights and trends."""
    ti = context['ti']
    daily_agg = ti.xcom_pull(key='daily_aggregations', task_ids='aggregate_daily')

    insights = []

    if daily_agg:
        # Generate sample insights
        insights = [
            f"Average global temperature: {daily_agg['avg_temperature_global']}°C",
            f"Temperature range: {daily_agg['min_temperature']}°C to {daily_agg['max_temperature']}°C",
            f"Data coverage: {daily_agg['cities_covered']} cities",
            f"Data quality: {daily_agg['data_quality_score']:.1%}"
        ]

        # Weather trend analysis (simplified)
        if daily_agg['avg_temperature_global'] > 25:
            insights.append("🌡️ Warm day globally")
        elif daily_agg['avg_temperature_global'] < 15:
            insights.append("❄️ Cool day globally")

    context['ti'].xcom_push(key='weather_insights', value=insights)

    return f"Generated {len(insights)} weather insights"

def create_analytics_report(**context):
    """Create comprehensive analytics report."""
    ti = context['ti']
    daily_agg = ti.xcom_pull(key='daily_aggregations', task_ids='aggregate_daily')
    insights = ti.xcom_pull(key='weather_insights', task_ids='generate_insights')

    report = {
        'report_date': context['execution_date'].strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'daily_aggregations': daily_agg,
        'insights': insights,
        'recommendations': [
            "Monitor temperature trends for climate analysis",
            "Check data quality metrics regularly",
            "Consider expanding city coverage"
        ]
    }

    # Save report (would save to file/database in production)
    context['ti'].xcom_push(key='analytics_report', value=report)

    return "Analytics report created"

def export_analytics_data(**context):
    """Export analytics data for external consumption."""
    ti = context['ti']
    report = ti.xcom_pull(key='analytics_report', task_ids='create_report')

    if report:
        # Export to CSV or JSON (simplified)
        export_path = f"/app/data/analytics/daily_report_{report['report_date']}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        # Save report
        import json
        with open(export_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Analytics report exported to {export_path}")

    return "Analytics data exported"

# Tasks
aggregate_task = PythonOperator(
    task_id='aggregate_daily',
    python_callable=aggregate_daily_weather,
    dag=dag,
)

insights_task = PythonOperator(
    task_id='generate_insights',
    python_callable=generate_weather_insights,
    dag=dag,
)

report_task = PythonOperator(
    task_id='create_report',
    python_callable=create_analytics_report,
    dag=dag,
)

export_task = PythonOperator(
    task_id='export_analytics',
    python_callable=export_analytics_data,
    dag=dag,
)

# Data validation task
validate_analytics = BashOperator(
    task_id='validate_analytics',
    bash_command='echo "Analytics validation would check data integrity here"',
    dag=dag,
)

# Set dependencies
aggregate_task >> insights_task >> report_task >> export_task >> validate_analytics
