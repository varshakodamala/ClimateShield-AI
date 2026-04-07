"""Feature engineering utilities for weather data."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

class FeatureEngineer:
    """Adds derived features to weather dataset records."""

    def engineer_features(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Engineer features on a single record or a list of records."""
        if isinstance(data, list):
            return [self._engineer_single_record(record) for record in data]
        return self._engineer_single_record(data)

    def _engineer_single_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add features to a single weather record."""
        record = dict(record) if record is not None else {}
        record = self._normalize_timestamp(record)
        record = self._add_time_features(record)
        record = self._add_weather_features(record)
        record = self._add_temperature_category(record)
        return record

    def _normalize_timestamp(self, record: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = record.get('timestamp')
        if isinstance(timestamp, str):
            try:
                record['timestamp'] = datetime.fromisoformat(timestamp)
            except ValueError:
                try:
                    record['timestamp'] = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    record['timestamp'] = None
        return record

    def _add_time_features(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add time-based features to a weather record."""
        ts = record.get('timestamp')
        if not isinstance(ts, datetime):
            return record

        record['year'] = ts.year
        record['month'] = ts.month
        record['day'] = ts.day
        record['hour'] = ts.hour
        record['minute'] = ts.minute
        record['day_of_week'] = ts.weekday()
        record['day_of_year'] = ts.timetuple().tm_yday
        record['is_weekend'] = 1 if ts.weekday() >= 5 else 0
        record['is_business_hours'] = 1 if 9 <= ts.hour < 18 else 0
        record['season'] = self._get_season(ts)
        return record

    def _add_weather_features(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add derived weather indicator features."""
        weather = record.get('weather') or {}
        if isinstance(weather, dict):
            main = (weather.get('main') or '').lower()
        else:
            main = str(weather).lower()

        record['is_clear'] = 1 if 'clear' in main else 0
        record['is_rainy'] = 1 if 'rain' in main else 0
        record['is_snowy'] = 1 if 'snow' in main else 0
        record['is_cloudy'] = 1 if 'cloud' in main else 0
        return record

    def _add_temperature_category(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add a simple temperature category feature."""
        temperature = record.get('temperature')
        if isinstance(temperature, (int, float)):
            if temperature >= 30:
                record['temperature_category'] = 'Hot'
            elif temperature <= 10:
                record['temperature_category'] = 'Cold'
            else:
                record['temperature_category'] = 'Normal'
        return record

    def _get_season(self, timestamp: datetime) -> str:
        month = timestamp.month
        if month in (12, 1, 2):
            return 'winter'
        if month in (3, 4, 5):
            return 'spring'
        if month in (6, 7, 8):
            return 'summer'
        return 'autumn'

