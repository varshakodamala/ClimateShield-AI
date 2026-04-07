"""Airflow DAG for weather alerts and monitoring."""

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
from airflow.operators.email import EmailOperator  # type: ignore[reportMissingImports]

from monitoring.alerts import WeatherAlertSystem, AlertDashboard
from core.extract.weather_api import WeatherAPIExtractor

default_args = {
    'owner': 'weather_platform',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}

dag = DAG(
    'weather_alert_pipeline',
    default_args=default_args,
    description='Weather monitoring and alerting pipeline',
    schedule_interval=timedelta(minutes=30),  # Run every 30 minutes
    max_active_runs=1,
    tags=['weather', 'alerts', 'monitoring'],
)

def check_weather_alerts(**context):
    """Check weather conditions and trigger alerts."""
    config = {}  # Load from config file in production
    alert_system = WeatherAlertSystem(config)
    extractor = WeatherAPIExtractor(config)

    # Cities to monitor
    cities = ['New York', 'London', 'Tokyo', 'Sydney', 'Paris']

    alerts_triggered = []

    for city in cities:
        try:
            weather_data = extractor.extract(city=city)
            if weather_data:
                city_alerts = alert_system.check_weather_alerts(weather_data)
                alerts_triggered.extend(city_alerts)

        except Exception as e:
            print(f"Error checking alerts for {city}: {e}")

    # Store alerts in XCom for next task
    context['ti'].xcom_push(key='alerts_triggered', value=alerts_triggered)

    return f"Checked alerts for {len(cities)} cities, {len(alerts_triggered)} alerts triggered"

def send_alert_summary(**context):
    """Send summary of triggered alerts."""
    ti = context['ti']
    alerts = ti.xcom_pull(key='alerts_triggered', task_ids='check_alerts')

    if not alerts:
        return "No alerts to send"

    # Create email content
    subject = f"Weather Alert Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    body = f"""
Weather Alert Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Alerts: {len(alerts)}

Alert Details:
{chr(10).join(f"- {alert}" for alert in alerts)}

---
Weather Data Platform
Automatic Alert System
"""

    # Send email (you would configure this with actual email settings)
    print(f"Would send email with subject: {subject}")
    print(f"Email body: {body}")

    return f"Alert summary sent for {len(alerts)} alerts"

def monitor_system_health(**context):
    """Monitor system health and performance."""
    # This would check database connections, API response times, etc.
    # For now, just a placeholder

    health_metrics = {
        'database_connected': True,  # Check actual DB connection
        'api_response_time': 1.2,    # Check actual API response
        'last_data_update': datetime.now() - timedelta(hours=1)
    }

    # Check for issues
    issues = []
    if not health_metrics['database_connected']:
        issues.append("Database connection failed")

    if health_metrics['api_response_time'] > 5.0:
        issues.append(f"Average response time: {health_metrics['api_response_time']:.2f}s")

    if (datetime.now() - health_metrics['last_data_update']).total_seconds() > 3600:
        issues.append("Data is stale (>1 hour old)")

    if issues:
        context['ti'].xcom_push(key='health_issues', value=issues)
        raise Exception(f"System health issues detected: {', '.join(issues)}")

    return "System health check passed"

# Tasks
check_alerts_task = PythonOperator(
    task_id='check_alerts',
    python_callable=check_weather_alerts,
    dag=dag,
)

send_alert_summary_task = PythonOperator(
    task_id='send_alert_summary',
    python_callable=send_alert_summary,
    dag=dag,
)

monitor_health_task = PythonOperator(
    task_id='monitor_system_health',
    python_callable=monitor_system_health,
    dag=dag,
)

# Email alert task (conditional)
alert_email_task = EmailOperator(
    task_id='send_health_alert',
    to='admin@weatherplatform.com',
    subject='Weather Platform Health Alert',
    html_content="""
    <h2>Weather Platform Health Alert</h2>
    <p>System health issues have been detected. Please check the Airflow logs for details.</p>
    <p>Timestamp: {{ ts }}</p>
    """,
    dag=dag,
    trigger_rule='one_failed',  # Only run if previous task failed
)

# Set dependencies
check_alerts_task >> send_alert_summary_task
monitor_health_task >> alert_email_task
