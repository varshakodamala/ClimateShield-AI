"""Logging configuration for the weather platform."""

import logging
import logging.handlers
from pathlib import Path
import sys
from typing import Dict, Any
import json
from datetime import datetime

class WeatherLogger:
    """Centralized logging configuration for the weather platform."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO').upper())
        self.log_file = config.get('logging', {}).get('file', 'logs/weather_platform.log')

        # Create logs directory
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

        # Initialize logger
        self.logger = logging.getLogger('weather_platform')
        self.logger.setLevel(self.log_level)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )

        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(console_formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Log initialization
        self.logger.info("Weather platform logging initialized")

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for a specific module."""
        return self.logger.getChild(name)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry['extra_data'] = record.extra_data

        return json.dumps(log_entry)

class MetricsLogger:
    """Logger for performance metrics and monitoring."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_file = config.get('logging', {}).get('metrics_file', 'logs/metrics.log')

        # Create logs directory
        Path(self.metrics_file).parent.mkdir(parents=True, exist_ok=True)

        # Initialize metrics logger
        self.metrics_logger = logging.getLogger('weather_platform.metrics')
        self.metrics_logger.setLevel(logging.INFO)

        # JSON formatter for metrics
        json_formatter = JSONFormatter()

        # File handler for metrics
        metrics_handler = logging.handlers.RotatingFileHandler(
            self.metrics_file,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=3
        )
        metrics_handler.setFormatter(json_formatter)

        self.metrics_logger.addHandler(metrics_handler)
        self.metrics_logger.propagate = False  # Don't propagate to root logger

    def log_pipeline_start(self, pipeline_type: str, cities: list = None):
        """Log pipeline execution start."""
        self.metrics_logger.info(
            f"Pipeline {pipeline_type} started",
            extra={
                'extra_data': {
                    'event_type': 'pipeline_start',
                    'pipeline_type': pipeline_type,
                    'cities': cities or [],
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

    def log_pipeline_end(self, pipeline_type: str, success: bool, duration: float, records_processed: int = 0):
        """Log pipeline execution end."""
        self.metrics_logger.info(
            f"Pipeline {pipeline_type} completed",
            extra={
                'extra_data': {
                    'event_type': 'pipeline_end',
                    'pipeline_type': pipeline_type,
                    'success': success,
                    'duration_seconds': duration,
                    'records_processed': records_processed,
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

    def log_api_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Log API request metrics."""
        self.metrics_logger.info(
            f"API request to {endpoint}",
            extra={
                'extra_data': {
                    'event_type': 'api_request',
                    'endpoint': endpoint,
                    'method': method,
                    'response_time_seconds': response_time,
                    'status_code': status_code,
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

    def log_data_quality(self, table_name: str, record_count: int, null_percentage: Dict[str, float]):
        """Log data quality metrics."""
        self.metrics_logger.info(
            f"Data quality check for {table_name}",
            extra={
                'extra_data': {
                    'event_type': 'data_quality',
                    'table_name': table_name,
                    'record_count': record_count,
                    'null_percentages': null_percentage,
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

    def log_error(self, error_type: str, error_message: str, component: str):
        """Log application errors."""
        self.metrics_logger.error(
            f"Error in {component}: {error_message}",
            extra={
                'extra_data': {
                    'event_type': 'error',
                    'error_type': error_type,
                    'error_message': error_message,
                    'component': component,
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

# Global logger instances
_weather_logger = None
_metrics_logger = None

def get_logger(name: str = 'weather_platform') -> logging.Logger:
    """Get the main application logger."""
    global _weather_logger
    if _weather_logger is None:
        # Default config if not initialized
        config = {'logging': {'level': 'INFO', 'file': 'logs/weather_platform.log'}}
        _weather_logger = WeatherLogger(config)
    return _weather_logger.get_logger(name)

def get_metrics_logger() -> MetricsLogger:
    """Get the metrics logger."""
    global _metrics_logger
    if _metrics_logger is None:
        # Default config if not initialized
        config = {'logging': {'metrics_file': 'logs/metrics.log'}}
        _metrics_logger = MetricsLogger(config)
    return _metrics_logger

def initialize_logging(config: Dict[str, Any]):
    """Initialize logging with configuration."""
    global _weather_logger, _metrics_logger

    _weather_logger = WeatherLogger(config)
    _metrics_logger = MetricsLogger(config)

    # Set up logging for external libraries
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Convenience functions for common logging patterns
def log_pipeline_execution(pipeline_func):
    """Decorator to log pipeline execution."""
    def wrapper(*args, **kwargs):
        metrics_logger = get_metrics_logger()
        pipeline_type = getattr(pipeline_func, '__name__', 'unknown')

        start_time = datetime.now()
        metrics_logger.log_pipeline_start(pipeline_type)

        try:
            result = pipeline_func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            success = result if isinstance(result, bool) else True
            records_processed = kwargs.get('records_processed', 0)

            metrics_logger.log_pipeline_end(pipeline_type, success, duration, records_processed)
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            metrics_logger.log_pipeline_end(pipeline_type, False, duration)
            raise

    return wrapper
