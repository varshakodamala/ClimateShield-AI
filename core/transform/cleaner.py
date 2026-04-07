"""Data cleaning utilities for weather data."""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataCleaner:
    """Handles data cleaning and validation for weather data."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def clean_weather_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Clean weather data by handling missing values, outliers, and inconsistencies."""
        if isinstance(data, dict):
            return self._clean_single_record(data)
        elif isinstance(data, list):
            return [self._clean_single_record(record) for record in data if record]
        else:
            self.logger.warning(f"Unsupported data type: {type(data)}")
            return data

    def _clean_single_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single weather data record."""
        cleaned = record.copy()

        try:
            # Handle missing values
            cleaned = self._handle_missing_values(cleaned)

            # Validate and correct data ranges
            cleaned = self._validate_data_ranges(cleaned)

            # Standardize data types
            cleaned = self._standardize_data_types(cleaned)

            # Remove duplicate or redundant information
            cleaned = self._remove_redundancies(cleaned)

        except Exception as e:
            self.logger.error(f"Error cleaning record: {e}")
            return record  # Return original if cleaning fails

        return cleaned

    def _handle_missing_values(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missing or null values in weather data."""
        # Define default values for missing data
        defaults = {
            'temperature': None,
            'feels_like': None,
            'humidity': 0,
            'pressure': None,
            'wind': {'speed': 0, 'direction': None},
            'clouds': 0,
            'visibility': None,
            'rain': 0,
            'snow': 0
        }

        cleaned = record.copy()

        # Replace None, NaN, or empty strings with defaults
        for key, default in defaults.items():
            if key not in cleaned or cleaned[key] is None or (isinstance(cleaned[key], str) and cleaned[key].strip() == ''):
                if isinstance(default, dict):
                    cleaned[key] = default.copy()
                else:
                    cleaned[key] = default
            elif isinstance(cleaned[key], float) and np.isnan(cleaned[key]):
                cleaned[key] = default

        # Handle nested wind data
        if 'wind' in cleaned and isinstance(cleaned['wind'], dict):
            wind_defaults = {'speed': 0, 'direction': None}
            for wind_key, wind_default in wind_defaults.items():
                if wind_key not in cleaned['wind'] or cleaned['wind'][wind_key] is None:
                    cleaned['wind'][wind_key] = wind_default
                elif isinstance(cleaned['wind'][wind_key], float) and np.isnan(cleaned['wind'][wind_key]):
                    cleaned['wind'][wind_key] = wind_default

        return cleaned

    def _validate_data_ranges(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and correct data ranges."""
        cleaned = record.copy()

        # Temperature range validation (-100°C to 60°C)
        if 'temperature' in cleaned and cleaned['temperature'] is not None:
            if not (-100 <= cleaned['temperature'] <= 60):
                self.logger.warning(f"Invalid temperature: {cleaned['temperature']}")
                cleaned['temperature'] = None

        if 'feels_like' in cleaned and cleaned['feels_like'] is not None:
            if not (-100 <= cleaned['feels_like'] <= 60):
                self.logger.warning(f"Invalid feels_like: {cleaned['feels_like']}")
                cleaned['feels_like'] = None

        # Humidity range (0-100%)
        if 'humidity' in cleaned and cleaned['humidity'] is not None:
            if not (0 <= cleaned['humidity'] <= 100):
                self.logger.warning(f"Invalid humidity: {cleaned['humidity']}")
                cleaned['humidity'] = None

        # Pressure range (800-1200 hPa)
        if 'pressure' in cleaned and cleaned['pressure'] is not None:
            if not (800 <= cleaned['pressure'] <= 1200):
                self.logger.warning(f"Invalid pressure: {cleaned['pressure']}")
                cleaned['pressure'] = None

        # Wind speed (0-150 m/s)
        if 'wind' in cleaned and isinstance(cleaned['wind'], dict):
            if 'speed' in cleaned['wind'] and cleaned['wind']['speed'] is not None:
                if not (0 <= cleaned['wind']['speed'] <= 150):
                    self.logger.warning(f"Invalid wind speed: {cleaned['wind']['speed']}")
                    cleaned['wind']['speed'] = 0

            # Wind direction (0-360 degrees)
            if 'direction' in cleaned['wind'] and cleaned['wind']['direction'] is not None:
                if not (0 <= cleaned['wind']['direction'] <= 360):
                    self.logger.warning(f"Invalid wind direction: {cleaned['wind']['direction']}")
                    cleaned['wind']['direction'] = None

        # Cloud coverage (0-100%)
        if 'clouds' in cleaned and cleaned['clouds'] is not None:
            if not (0 <= cleaned['clouds'] <= 100):
                self.logger.warning(f"Invalid cloud coverage: {cleaned['clouds']}")
                cleaned['clouds'] = 0

        # Visibility (0-50000 meters)
        if 'visibility' in cleaned and cleaned['visibility'] is not None:
            if not (0 <= cleaned['visibility'] <= 50000):
                self.logger.warning(f"Invalid visibility: {cleaned['visibility']}")
                cleaned['visibility'] = None

        return cleaned

    def _standardize_data_types(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize data types."""
        cleaned = record.copy()

        # Ensure numeric fields are floats
        numeric_fields = ['temperature', 'feels_like', 'humidity', 'pressure', 'clouds', 'visibility', 'rain', 'snow']
        for field in numeric_fields:
            if field in cleaned and cleaned[field] is not None:
                try:
                    cleaned[field] = float(cleaned[field])
                except (ValueError, TypeError):
                    self.logger.warning(f"Could not convert {field} to float: {cleaned[field]}")
                    cleaned[field] = None

        # Ensure wind speed is float
        if 'wind' in cleaned and isinstance(cleaned['wind'], dict):
            if 'speed' in cleaned['wind'] and cleaned['wind']['speed'] is not None:
                try:
                    cleaned['wind']['speed'] = float(cleaned['wind']['speed'])
                except (ValueError, TypeError):
                    cleaned['wind']['speed'] = 0.0

            if 'direction' in cleaned['wind'] and cleaned['wind']['direction'] is not None:
                try:
                    cleaned['wind']['direction'] = float(cleaned['wind']['direction'])
                except (ValueError, TypeError):
                    cleaned['wind']['direction'] = None

        # Ensure coordinates are floats
        if 'coordinates' in cleaned and isinstance(cleaned['coordinates'], dict):
            for coord in ['lat', 'lon']:
                if coord in cleaned['coordinates'] and cleaned['coordinates'][coord] is not None:
                    try:
                        cleaned['coordinates'][coord] = float(cleaned['coordinates'][coord])
                    except (ValueError, TypeError):
                        cleaned['coordinates'][coord] = None

        return cleaned

    def _remove_redundancies(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate or redundant information."""
        cleaned = record.copy()

        # If temperature and feels_like are the same, feels_like might be redundant
        # But we'll keep it as it's useful information

        # Ensure weather description is not empty if weather main exists
        if 'weather' in cleaned and isinstance(cleaned['weather'], dict):
            if 'main' in cleaned['weather'] and not cleaned['weather'].get('description'):
                # Set a default description based on main weather
                main_weather = cleaned['weather']['main'].lower()
                default_descriptions = {
                    'clear': 'clear sky',
                    'clouds': 'scattered clouds',
                    'rain': 'moderate rain',
                    'snow': 'light snow',
                    'thunderstorm': 'thunderstorm',
                    'drizzle': 'light drizzle',
                    'mist': 'mist',
                    'fog': 'fog'
                }
                cleaned['weather']['description'] = default_descriptions.get(main_weather, main_weather)

        return cleaned

    def remove_outliers(self, data: List[Dict[str, Any]], field: str, method: str = 'iqr', threshold: float = 1.5) -> List[Dict[str, Any]]:
        """Remove outliers from data based on specified field."""
        if not data:
            return data

        try:
            values = [record.get(field) for record in data if record.get(field) is not None]
            if not values:
                return data

            if method == 'iqr':
                # Interquartile range method
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_bound = q1 - (threshold * iqr)
                upper_bound = q3 + (threshold * iqr)

                filtered_data = [
                    record for record in data
                    if record.get(field) is None or (lower_bound <= record[field] <= upper_bound)
                ]
            elif method == 'zscore':
                # Z-score method
                mean_val = np.mean(values)
                std_val = np.std(values)
                z_scores = [(val - mean_val) / std_val for val in values]

                filtered_data = [
                    record for record, z_score in zip(data, z_scores)
                    if abs(z_score) <= threshold
                ]
            else:
                self.logger.warning(f"Unknown outlier detection method: {method}")
                return data

            removed_count = len(data) - len(filtered_data)
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} outliers from {field}")

            return filtered_data

        except Exception as e:
            self.logger.error(f"Error removing outliers: {e}")
            return data

    def fill_missing_values(self, data: List[Dict[str, Any]], method: str = 'mean') -> List[Dict[str, Any]]:
        """Fill missing values in weather data."""
        if not data:
            return data

        try:
            df = pd.DataFrame(data)

            if method == 'mean':
                filled_df = df.fillna(df.mean(numeric_only=True))
            elif method == 'median':
                filled_df = df.fillna(df.median(numeric_only=True))
            elif method == 'forward_fill':
                filled_df = df.fillna(method='ffill')
            elif method == 'backward_fill':
                filled_df = df.fillna(method='bfill')
            else:
                self.logger.warning(f"Unknown fill method: {method}")
                return data

            return filled_df.to_dict('records')

        except Exception as e:
            self.logger.error(f"Error filling missing values: {e}")
            return data
