"""CSV data loader for weather data."""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CSVLoader:
    """Handles loading weather data to CSV files."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def load(self, data: Union[Dict[str, Any], List[Dict[str, Any]]],
             file_path: str, mode: str = 'append') -> bool:
        """Load weather data to CSV file.

        Args:
            data: Weather data to load
            file_path: Path to CSV file
            mode: 'append' or 'overwrite'

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert data to DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                self.logger.error(f"Unsupported data type: {type(data)}")
                return False

            if df.empty:
                self.logger.warning("No data to load")
                return False

            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Handle different modes
            if mode == 'append' and os.path.exists(file_path):
                try:
                    # Read existing data and append
                    existing_df = pd.read_csv(file_path)
                    combined_df = pd.concat([existing_df, df], ignore_index=True)

                    # Remove duplicates based on timestamp and city if they exist
                    if 'timestamp' in combined_df.columns and 'city' in combined_df.columns:
                        combined_df = combined_df.drop_duplicates(subset=['timestamp', 'city'], keep='last')

                    combined_df.to_csv(file_path, index=False)
                except pd.errors.EmptyDataError:
                    # File exists but is empty, just write the new data
                    df.to_csv(file_path, index=False)
            else:
                # Overwrite or create new file
                df.to_csv(file_path, index=False)

            self.logger.info(f"Successfully loaded {len(df)} records to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load data to CSV: {e}")
            return False

    def load_batch(self, data_list: List[List[Dict[str, Any]]],
                   file_paths: List[str], mode: str = 'append') -> List[bool]:
        """Load multiple batches of data to different CSV files.

        Args:
            data_list: List of data batches
            file_paths: Corresponding file paths
            mode: 'append' or 'overwrite'

        Returns:
            List of success flags
        """
        if len(data_list) != len(file_paths):
            self.logger.error("Data list and file paths must have the same length")
            return [False] * len(data_list)

        results = []
        for data, file_path in zip(data_list, file_paths):
            success = self.load(data, file_path, mode)
            results.append(success)

        return results

    def load_with_partitioning(self, data: List[Dict[str, Any]],
                              base_path: str, partition_key: str = 'date') -> bool:
        """Load data with partitioning (e.g., by date).

        Args:
            data: Weather data to load
            base_path: Base directory path
            partition_key: Key to partition by ('date', 'city', etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                self.logger.warning("No data to load")
                return False

            df = pd.DataFrame(data)

            # Create partition column if needed
            if partition_key == 'date' and 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp']).dt.date.astype(str)
            elif partition_key not in df.columns:
                self.logger.error(f"Partition key '{partition_key}' not found in data")
                return False

            # Group by partition key and save to separate files
            for partition_value, group_df in df.groupby(partition_key):
                partition_path = os.path.join(base_path, f"{partition_key}={partition_value}", "data.csv")
                Path(partition_path).parent.mkdir(parents=True, exist_ok=True)

                if os.path.exists(partition_path):
                    # Append to existing partition
                    existing_df = pd.read_csv(partition_path)
                    combined_df = pd.concat([existing_df, group_df], ignore_index=True)
                    combined_df.to_csv(partition_path, index=False)
                else:
                    group_df.to_csv(partition_path, index=False)

            self.logger.info(f"Successfully loaded partitioned data to {base_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load partitioned data: {e}")
            return False

    def validate_csv_structure(self, file_path: str,
                              required_columns: List[str]) -> bool:
        """Validate CSV file structure.

        Args:
            file_path: Path to CSV file
            required_columns: List of required column names

        Returns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"CSV file does not exist: {file_path}")
                return False

            df = pd.read_csv(file_path)

            # Check for required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False

            # Check for empty file
            if df.empty:
                self.logger.warning(f"CSV file is empty: {file_path}")
                return False

            self.logger.info(f"CSV file structure is valid: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate CSV structure: {e}")
            return False

    def get_csv_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Dictionary with file information or None if error
        """
        try:
            if not os.path.exists(file_path):
                return None

            df = pd.read_csv(file_path)

            info = {
                'file_path': file_path,
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'last_modified': pd.to_datetime(os.path.getmtime(file_path), unit='s')
            }

            # Data types
            info['dtypes'] = df.dtypes.astype(str).to_dict()

            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if not numeric_cols.empty:
                info['numeric_stats'] = df[numeric_cols].describe().to_dict()

            return info

        except Exception as e:
            self.logger.error(f"Failed to get CSV info: {e}")
            return None
