"""Weather data pipeline orchestration."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import yaml
import os
from dotenv import load_dotenv

from core.extract.weather_api import WeatherAPIExtractor
from core.transform.cleaner import DataCleaner
from core.transform.unit_converter import UnitConverter
from core.transform.feature_engineering import FeatureEngineer
from core.load.csv_loader import CSVLoader
from core.load.db_loader import DatabaseLoader
from core.load.s3_loader import S3Loader

logger = logging.getLogger(__name__)

class WeatherPipeline:
    """Orchestrates the complete weather data pipeline."""

    def __init__(self, config_path: str = 'config/settings.yaml'):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize components
        self.extractor = WeatherAPIExtractor(self.config)
        self.cleaner = DataCleaner()
        self.unit_converter = UnitConverter()
        self.feature_engineer = FeatureEngineer()

        # Initialize loaders
        self.csv_loader = CSVLoader(self.config)
        self.db_loader = DatabaseLoader(self.config)
        self.s3_loader = S3Loader(self.config)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file and expand environment variables."""
        load_dotenv()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            return self._expand_env_vars(config)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

    def _expand_env_vars(self, value: Any) -> Any:
        """Expand environment variables in config values."""
        if isinstance(value, dict):
            return {k: self._expand_env_vars(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._expand_env_vars(v) for v in value]
        if isinstance(value, str):
            return os.path.expandvars(value)
        return value

    def run_full_pipeline(self, cities: Optional[List[str]] = None,
                         extraction_type: str = 'current') -> bool:
        """Run the complete weather data pipeline.

        Args:
            cities: List of city names to process (uses config cities if None)
            extraction_type: 'current' or 'forecast'

        Returns:
            True if pipeline completed successfully, False otherwise
        """
        try:
            self.logger.info("Starting weather data pipeline")

            # Step 1: Extract data
            raw_data = self._extract_data(cities, extraction_type)
            if not raw_data:
                self.logger.error("No data extracted, stopping pipeline")
                return False

            # Step 2: Clean data
            cleaned_data = self._clean_data(raw_data)

            # Step 3: Transform data (units and features)
            transformed_data = self._transform_data(cleaned_data)

            # Step 4: Load data
            success = self._load_data(transformed_data)

            if success:
                self.logger.info("Weather data pipeline completed successfully")
            else:
                self.logger.error("Weather data pipeline failed during loading")

            return success

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            return False

    def _extract_data(self, cities: Optional[List[str]],
                     extraction_type: str) -> List[Dict[str, Any]]:
        """Extract weather data from API."""
        self.logger.info("Starting data extraction")

        if not cities:
            cities_config = self.config.get('cities', [])
            cities = [city['name'] for city in cities_config]

        extracted_data = []

        for city in cities:
            try:
                if extraction_type == 'current':
                    data = self.extractor.extract(city=city)
                elif extraction_type == 'forecast':
                    data = self.extractor.extract(city=city, type='forecast')
                else:
                    self.logger.warning(f"Unknown extraction type: {extraction_type}")
                    continue

                if data:
                    if isinstance(data, list):
                        extracted_data.extend(data)
                    else:
                        extracted_data.append(data)

                    self.logger.info(f"Extracted data for {city}")
                else:
                    self.logger.warning(f"No data extracted for {city}")

            except Exception as e:
                self.logger.error(f"Failed to extract data for {city}: {e}")

        self.logger.info(f"Extracted {len(extracted_data)} total records")
        return extracted_data

    def _clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate weather data."""
        self.logger.info("Starting data cleaning")

        cleaned_data = self.cleaner.clean_weather_data(data)

        # Remove outliers
        cleaned_data = self.cleaner.remove_outliers(cleaned_data, 'temperature')
        cleaned_data = self.cleaner.remove_outliers(cleaned_data, 'humidity')

        # Fill missing values
        cleaned_data = self.cleaner.fill_missing_values(cleaned_data, method='mean')

        self.logger.info(f"Cleaned data: {len(cleaned_data)} records")
        return cleaned_data

    def _transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform weather data (units and features)."""
        self.logger.info("Starting data transformation")

        # Convert units if needed (API returns metric by default)
        target_units = {'temperature': 'celsius', 'wind_speed': 'm/s', 'pressure': 'hPa'}
        transformed_data = []

        for record in data:
            # Unit conversion
            converted_record = self.unit_converter.convert_weather_data(record, target_units)

            # Feature engineering
            engineered_record = self.feature_engineer.engineer_features(converted_record)

            transformed_data.append(engineered_record)

        self.logger.info(f"Transformed data: {len(transformed_data)} records")
        return transformed_data

    def _load_data(self, data: List[Dict[str, Any]]) -> bool:
        """Load transformed data to various destinations."""
        self.logger.info("Starting data loading")

        success = True

        # Load to CSV
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = f"data/processed/weather_data_{timestamp}.csv"
            csv_success = self.csv_loader.load(data, csv_path)
            if csv_success:
                self.logger.info(f"Data loaded to CSV: {csv_path}")
            else:
                self.logger.error("Failed to load data to CSV")
                success = False
        except Exception as e:
            self.logger.error(f"CSV loading failed: {e}")
            success = False

        # Load to database
        try:
            db_success = self.db_loader.load(data, 'weather_data')
            if db_success:
                self.logger.info("Data loaded to database")
            else:
                self.logger.error("Failed to load data to database")
                success = False
        except Exception as e:
            self.logger.error(f"Database loading failed: {e}")
            success = False

        # Load to S3
        try:
            s3_key = f"weather-data/{datetime.now().strftime('%Y/%m/%d')}/weather_data_{datetime.now().strftime('%H%M%S')}.parquet"
            s3_success = self.s3_loader.load_parquet(data, s3_key)
            if s3_success:
                self.logger.info(f"Data loaded to S3: {s3_key}")
            else:
                self.logger.error("Failed to load data to S3")
                success = False
        except Exception as e:
            self.logger.error(f"S3 loading failed: {e}")
            success = False

        return success

    def run_incremental_pipeline(self, cities: Optional[List[str]] = None,
                                hours_back: int = 24) -> bool:
        """Run incremental pipeline for recent data.

        Args:
            cities: List of city names to process
            hours_back: Hours of historical data to process

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Starting incremental pipeline for last {hours_back} hours")

            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)

            # For incremental loads, we might want to check existing data
            # and only process cities that haven't been updated recently

            return self.run_full_pipeline(cities, 'current')

        except Exception as e:
            self.logger.error(f"Incremental pipeline failed: {e}")
            return False

    def run_forecast_pipeline(self, cities: Optional[List[str]] = None) -> bool:
        """Run pipeline specifically for weather forecasts.

        Args:
            cities: List of city names to process

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting forecast pipeline")

            return self.run_full_pipeline(cities, 'forecast')

        except Exception as e:
            self.logger.error(f"Forecast pipeline failed: {e}")
            return False

    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate pipeline components and connections.

        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'extractor': self.extractor.validate_connection(),
            'database': self.db_loader.connect(),
            's3': self.s3_loader.connect(),
            'config': bool(self.config)
        }

        # Close connections
        self.db_loader.disconnect()

        success_count = sum(validation_results.values())
        total_count = len(validation_results)

        validation_results['overall_success'] = success_count == total_count
        validation_results['success_rate'] = success_count / total_count

        self.logger.info(f"Pipeline validation: {success_count}/{total_count} components successful")

        return validation_results

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and statistics.

        Returns:
            Dictionary with pipeline status information
        """
        try:
            status = {
                'timestamp': datetime.now(),
                'config_loaded': bool(self.config),
                'extractor_ready': hasattr(self.extractor, 'api_key') and self.extractor.api_key,
                'database_connected': self.db_loader.engine is not None,
                's3_connected': self.s3_loader.s3_client is not None
            }

            # Get data statistics
            try:
                db_info = self.db_loader.get_table_info('weather_data')
                if db_info:
                    status['database_records'] = db_info.get('row_count', 0)
            except:
                status['database_records'] = 0

            # Get S3 statistics
            try:
                s3_objects = self.s3_loader.list_objects('weather-data/')
                status['s3_objects'] = len(s3_objects) if s3_objects else 0
            except:
                status['s3_objects'] = 0

            return status

        except Exception as e:
            self.logger.error(f"Failed to get pipeline status: {e}")
            return {'error': str(e)}
