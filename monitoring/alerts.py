"""Alerting system for the weather platform."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alerts and notifications for the weather platform."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alerts_config = config.get('alerts', {})
        self.logger = logging.getLogger(self.__class__.__name__)

    def send_email_alert(self, subject: str, message: str,
                        recipients: Optional[List[str]] = None) -> bool:
        """Send email alert."""
        try:
            if not recipients:
                recipients = [self.alerts_config.get('email', 'admin@weatherplatform.com')]

            # Email configuration
            smtp_server = self.alerts_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.alerts_config.get('smtp_port', 587)
            smtp_user = self.alerts_config.get('smtp_user')
            smtp_password = self.alerts_config.get('smtp_password')

            if not all([smtp_user, smtp_password]):
                self.logger.error("SMTP credentials not configured")
                return False

            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"Weather Platform Alert: {subject}"

            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_message = f"""
Weather Platform Alert
Timestamp: {timestamp}

{message}

---
Weather Data Platform
"""

            msg.attach(MIMEText(full_message, 'plain'))

            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_user, recipients, text)
            server.quit()

            self.logger.info(f"Email alert sent to {recipients}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False

    def alert_pipeline_failure(self, pipeline_type: str, error_message: str) -> bool:
        """Alert on pipeline failure."""
        subject = f"Pipeline Failure: {pipeline_type}"
        message = f"""
Pipeline Type: {pipeline_type}
Error: {error_message}
Status: FAILED

Please check the logs and resolve the issue.
"""
        return self.send_email_alert(subject, message)

    def alert_data_quality_issue(self, table_name: str, issues: List[str]) -> bool:
        """Alert on data quality issues."""
        subject = f"Data Quality Issue: {table_name}"
        message = f"""
Data Quality Issues Detected in {table_name}:

{chr(10).join(f"- {issue}" for issue in issues)}

Please review and clean the data.
"""
        return self.send_email_alert(subject, message)

    def alert_system_health(self, component: str, status: str, details: str = "") -> bool:
        """Alert on system health issues."""
        subject = f"System Health Alert: {component}"
        message = f"""
Component: {component}
Status: {status}
Details: {details}

Please investigate the system health.
"""
        return self.send_email_alert(subject, message)

    def alert_weather_threshold(self, city: str, metric: str, value: float,
                               threshold: float, condition: str) -> bool:
        """Alert on weather threshold breaches."""
        subject = f"Weather Threshold Alert: {city}"
        message = f"""
City: {city}
Metric: {metric}
Current Value: {value}
Threshold: {threshold}
Condition: {condition}

Weather conditions have exceeded the configured threshold.
"""
        return self.send_email_alert(subject, message)

class AlertRule:
    """Represents an alert rule."""

    def __init__(self, name: str, condition: str, threshold: float,
                 alert_type: str, enabled: bool = True):
        self.name = name
        self.condition = condition  # 'above', 'below', 'equals'
        self.threshold = threshold
        self.alert_type = alert_type  # 'email', 'log', 'both'
        self.enabled = enabled

    def check_condition(self, value: float) -> bool:
        """Check if the rule condition is met."""
        if not self.enabled:
            return False

        if self.condition == 'above':
            return value > self.threshold
        elif self.condition == 'below':
            return value < self.threshold
        elif self.condition == 'equals':
            return abs(value - self.threshold) < 0.01  # Small tolerance for floats
        else:
            return False

class WeatherAlertSystem:
    """Weather-specific alerting system."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_manager = AlertManager(config)
        self.rules: Dict[str, AlertRule] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load default weather alert rules
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default weather alert rules."""
        default_rules = [
            AlertRule("high_temperature", "above", 35.0, "email"),
            AlertRule("low_temperature", "below", -10.0, "email"),
            AlertRule("high_wind_speed", "above", 20.0, "email"),
            AlertRule("low_visibility", "below", 1000.0, "log"),
            AlertRule("high_humidity", "above", 90.0, "log"),
            AlertRule("low_pressure", "below", 980.0, "email")
        ]

        for rule in default_rules:
            self.rules[rule.name] = rule

    def add_rule(self, rule: AlertRule):
        """Add a custom alert rule."""
        self.rules[rule.name] = rule
        self.logger.info(f"Added alert rule: {rule.name}")

    def remove_rule(self, rule_name: str):
        """Remove an alert rule."""
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"Removed alert rule: {rule_name}")

    def check_weather_alerts(self, weather_data: Dict[str, Any]) -> List[str]:
        """Check weather data against alert rules."""
        triggered_alerts = []

        # Extract relevant metrics
        metrics = {
            'temperature': weather_data.get('temperature'),
            'wind_speed': weather_data.get('wind', {}).get('speed'),
            'visibility': weather_data.get('visibility'),
            'humidity': weather_data.get('humidity'),
            'pressure': weather_data.get('pressure')
        }

        city = weather_data.get('city', 'Unknown')

        # Check each rule
        for rule_name, rule in self.rules.items():
            if rule_name in metrics and metrics[rule_name] is not None:
                if rule.check_condition(metrics[rule_name]):
                    alert_message = (
                        f"Weather alert for {city}: {rule_name} is {rule.condition} "
                        f"threshold ({metrics[rule_name]} {rule.condition} {rule.threshold})"
                    )

                    triggered_alerts.append(alert_message)

                    # Send alert based on type
                    if rule.alert_type in ['email', 'both']:
                        self.alert_manager.alert_weather_threshold(
                            city, rule_name, metrics[rule_name],
                            rule.threshold, rule.condition
                        )

                    if rule.alert_type in ['log', 'both']:
                        self.logger.warning(alert_message)

        return triggered_alerts

    def check_system_alerts(self, system_metrics: Dict[str, Any]):
        """Check system health and performance metrics."""
        # Check database connection
        if not system_metrics.get('database_connected', True):
            self.alert_manager.alert_system_health(
                'Database', 'DISCONNECTED',
                'Unable to connect to the database'
            )

        # Check API response times
        avg_response_time = system_metrics.get('avg_api_response_time', 0)
        if avg_response_time > 5.0:  # 5 seconds threshold
            self.alert_manager.alert_system_health(
                'API Performance', 'SLOW',
                f'Average response time: {avg_response_time:.2f}s'
            )

        # Check data freshness
        last_update = system_metrics.get('last_data_update')
        if last_update:
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
            if hours_since_update > 24:  # 24 hours threshold
                self.alert_manager.alert_system_health(
                    'Data Freshness', 'STALE',
                    f'Last update was {hours_since_update:.1f} hours ago'
                )

    def log_alert_history(self, alert_type: str, message: str, severity: str = 'INFO'):
        """Log alert to history file."""
        try:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)

            alert_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': alert_type,
                'message': message,
                'severity': severity
            }

            alert_file = log_dir / 'alerts.log'
            with open(alert_file, 'a') as f:
                f.write(json.dumps(alert_entry) + '\n')

        except Exception as e:
            self.logger.error(f"Failed to log alert history: {e}")

class AlertDashboard:
    """Dashboard for viewing and managing alerts."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_file = Path('logs/alerts.log')
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts from the log file."""
        try:
            if not self.alert_file.exists():
                return []

            alerts = []
            cutoff_time = datetime.now() - timedelta(hours=hours)

            with open(self.alert_file, 'r') as f:
                for line in f:
                    try:
                        alert = json.loads(line.strip())
                        alert_time = datetime.fromisoformat(alert['timestamp'])

                        if alert_time >= cutoff_time:
                            alerts.append(alert)
                    except json.JSONDecodeError:
                        continue

            return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)

        except Exception as e:
            self.logger.error(f"Failed to get recent alerts: {e}")
            return []

    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of alerts."""
        alerts = self.get_recent_alerts(hours)

        summary = {
            'total_alerts': len(alerts),
            'by_type': {},
            'by_severity': {},
            'time_range': f"Last {hours} hours"
        }

        for alert in alerts:
            alert_type = alert.get('type', 'unknown')
            severity = alert.get('severity', 'INFO')

            summary['by_type'][alert_type] = summary['by_type'].get(alert_type, 0) + 1
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1

        return summary
