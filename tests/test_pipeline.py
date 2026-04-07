"""Tests for the weather data pipeline."""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch
import tempfile
import os

from core.extract.weather_api import WeatherAPIExtractor
from core.transform.cleaner import DataCleaner
from core.transform.unit_converter import UnitConverter
from core.transform.feature_engineering import FeatureEngineer
from core.load.csv_loader import CSVLoader
from core.pipeline.weather_pipeline import WeatherPipeline

class TestWeatherAPIExtractor:
    """Test cases for WeatherAPIExtractor."""

    @pytest.fixture
    def extractor(self):
        """Create a test extractor instance."""
        config = {
            'weather_api': {
                'base_url': 'https://api.openweathermap.org/data/2.5',
                'api_key': 'test_key',
                'units': 'metric'
            }
        }
        return WeatherAPIExtractor(config)

    def test_initialization(self, extractor):
        """Test extractor initialization."""
        assert extractor.base_url == 'https://api.openweathermap.org/data/2.5'
        assert extractor.api_key == 'test_key'
        assert extractor.units == 'metric'

    @patch('core.extract.weather_api.requests.get')
    def test_validate_connection_success(self, mock_get, extractor):
        """Test successful connection validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert extractor.validate_connection() == True

    @patch('core.extract.weather_api.requests.get')
    def test_validate_connection_failure(self, mock_get, extractor):
        """Test failed connection validation."""
        mock_get.side_effect = Exception("Connection failed")

        assert extractor.validate_connection() == False

class TestDataCleaner:
    """Test cases for DataCleaner."""

    @pytest.fixture
    def cleaner(self):
        """Create a test cleaner instance."""
        return DataCleaner()

    def test_clean_weather_data_dict(self, cleaner):
        """Test cleaning a single weather data record."""
        test_data = {
            'temperature': 25.5,
            'humidity': 65,
            'pressure': 1013.25,
            'wind': {'speed': 5.2, 'direction': 180},
            'timestamp': datetime.now()
        }

        result = cleaner.clean_weather_data(test_data)

        assert isinstance(result, dict)
        assert 'temperature' in result
        assert 'humidity' in result

    def test_clean_weather_data_list(self, cleaner):
        """Test cleaning a list of weather data records."""
        test_data = [
            {
                'temperature': 25.5,
                'humidity': 65,
                'invalid_field': 'should_be_removed'
            },
            {
                'temperature': None,
                'humidity': 70
            }
        ]

        result = cleaner.clean_weather_data(test_data)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[1]['temperature'] is None  # Should handle None values

    def test_validate_data_ranges(self, cleaner):
        """Test data range validation."""
        test_data = {
            'temperature': 150,  # Invalid: too high
            'humidity': 50,      # Valid
            'pressure': 500,     # Invalid: too low
            'wind': {'speed': 200, 'direction': 400}  # Invalid wind
        }

        result = cleaner._validate_data_ranges(test_data)

        assert result['temperature'] is None  # Should be set to None
        assert result['humidity'] == 50       # Should remain valid
        assert result['pressure'] is None     # Should be set to None
        assert result['wind']['speed'] == 0   # Should be reset

class TestUnitConverter:
    """Test cases for UnitConverter."""

    @pytest.fixture
    def converter(self):
        """Create a test converter instance."""
        return UnitConverter()

    def test_celsius_to_fahrenheit(self, converter):
        """Test Celsius to Fahrenheit conversion."""
        assert converter.celsius_to_fahrenheit(0) == 32
        assert converter.celsius_to_fahrenheit(100) == 212
        assert converter.celsius_to_fahrenheit(25) == 77

    def test_fahrenheit_to_celsius(self, converter):
        """Test Fahrenheit to Celsius conversion."""
        assert converter.fahrenheit_to_celsius(32) == 0
        assert converter.fahrenheit_to_celsius(212) == 100
        assert converter.fahrenheit_to_celsius(77) == 25

    def test_temperature_conversion(self, converter):
        """Test temperature conversion between units."""
        # Celsius to Fahrenheit
        assert converter.convert_temperature(25, 'celsius', 'fahrenheit') == 77

        # Fahrenheit to Celsius
        assert converter.convert_temperature(77, 'fahrenheit', 'celsius') == 25

        # Celsius to Kelvin
        result = converter.convert_temperature(0, 'celsius', 'kelvin')
        assert abs(result - 273.15) < 0.01

    def test_wind_speed_conversion(self, converter):
        """Test wind speed conversion between units."""
        # m/s to km/h
        assert converter.convert_wind_speed(10, 'm/s', 'km/h') == 36

        # km/h to m/s
        assert converter.convert_wind_speed(36, 'km/h', 'm/s') == 10

    def test_pressure_conversion(self, converter):
        """Test pressure conversion between units."""
        # hPa to mmHg
        result = converter.convert_pressure(1013.25, 'hPa', 'mmHg')
        assert abs(result - 760) < 0.1  # Standard atmospheric pressure

class TestFeatureEngineer:
    """Test cases for FeatureEngineer."""

    @pytest.fixture
    def engineer(self):
        """Create a test feature engineer instance."""
        return FeatureEngineer()

    def test_engineer_features_basic(self, engineer):
        """Test basic feature engineering."""
        test_data = {
            'timestamp': datetime(2023, 6, 15, 14, 30),
            'temperature': 25.5,
            'humidity': 65,
            'weather': {'main': 'Clear'},
            'wind': {'speed': 5.2}
        }

        result = engineer._engineer_single_record(test_data)

        # Check time-based features
        assert 'hour' in result
        assert result['hour'] == 14
        assert 'day_of_week' in result
        assert 'season' in result

        # Check weather features
        assert 'is_clear' in result
        assert result['is_clear'] == 1

    def test_add_time_features(self, engineer):
        """Test time-based feature addition."""
        test_data = {
            'timestamp': datetime(2023, 12, 25, 10, 0)  # Christmas morning
        }

        result = engineer._add_time_features(test_data)

        assert result['month'] == 12
        assert result['day_of_year'] == 359  # Dec 25
        assert result['season'] == 'winter'
        assert result['is_weekend'] == 0  # Monday
        assert result['is_business_hours'] == 1  # 10 AM

class TestCSVLoader:
    """Test cases for CSVLoader."""

    @pytest.fixture
    def loader(self):
        """Create a test CSV loader instance."""
        config = {}
        return CSVLoader(config)

    def test_load_data(self, loader):
        """Test loading data to CSV."""
        test_data = [
            {
                'timestamp': datetime.now(),
                'city': 'Test City',
                'temperature': 25.5,
                'humidity': 65
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'test.csv')

            success = loader.load(test_data, file_path)
            assert success == True

            # Verify file was created and contains data
            assert os.path.exists(file_path)

            df = pd.read_csv(file_path)
            assert len(df) == 1
            assert df['city'].iloc[0] == 'Test City'

    def test_validate_csv_structure(self, loader):
        """Test CSV structure validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'test.csv')

            # Create test CSV
            df = pd.DataFrame({
                'timestamp': [datetime.now()],
                'city': ['Test City'],
                'temperature': [25.5]
            })
            df.to_csv(file_path, index=False)

            # Test validation
            required_columns = ['timestamp', 'city', 'temperature']
            assert loader.validate_csv_structure(file_path, required_columns) == True

            # Test with missing column
            assert loader.validate_csv_structure(file_path, ['missing_column']) == False

class TestWeatherPipeline:
    """Test cases for WeatherPipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create a test pipeline instance."""
        return WeatherPipeline()

    @patch('core.pipeline.weather_pipeline.WeatherAPIExtractor')
    @patch('core.pipeline.weather_pipeline.DataCleaner')
    @patch('core.pipeline.weather_pipeline.CSVLoader')
    def test_pipeline_initialization(self, mock_csv_loader, mock_cleaner, mock_extractor, pipeline):
        """Test pipeline initialization."""
        assert hasattr(pipeline, 'extractor')
        assert hasattr(pipeline, 'cleaner')
        assert hasattr(pipeline, 'csv_loader')

    def test_validate_pipeline(self, pipeline):
        """Test pipeline validation."""
        # This will fail in test environment due to missing connections
        # but should return a validation dictionary
        result = pipeline.validate_pipeline()

        assert isinstance(result, dict)
        assert 'overall_success' in result
        assert 'extractor' in result

# Integration test
class TestIntegration:
    """Integration tests for the weather platform."""

    def test_data_flow(self):
        """Test the complete data flow from extraction to loading."""
        # Create test data
        test_weather_data = {
            'timestamp': datetime.now(),
            'city': 'Test City',
            'country': 'TC',
            'coordinates': {'lat': 40.7128, 'lon': -74.0060},
            'temperature': 25.5,
            'feels_like': 27.0,
            'humidity': 65,
            'pressure': 1013.25,
            'weather': {'main': 'Clear', 'description': 'clear sky', 'icon': '01d'},
            'wind': {'speed': 5.2, 'direction': 180},
            'clouds': 20,
            'visibility': 10000
        }

        # Test data cleaning
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_weather_data(test_weather_data)
        assert cleaned_data is not None
        assert 'temperature' in cleaned_data

        # Test unit conversion
        converter = UnitConverter()
        converted_data = converter.convert_weather_data(cleaned_data, {'temperature': 'fahrenheit'})
        assert converted_data is not None

        # Test feature engineering
        engineer = FeatureEngineer()
        engineered_data = engineer.engineer_features(converted_data)
        assert engineered_data is not None
        assert 'hour' in engineered_data

if __name__ == '__main__':
    pytest.main([__file__])
