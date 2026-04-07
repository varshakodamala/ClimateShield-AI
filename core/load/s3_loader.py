"""S3 data loader for weather data."""

from typing import Dict, Any, List, Optional, Union
import boto3
import pandas as pd
import json
import logging
from pathlib import Path
import io
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class S3Loader:
    """Handles loading weather data to Amazon S3."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # S3 configuration
        s3_config = config.get('s3', {})
        self.bucket_name = s3_config.get('bucket')
        self.region = s3_config.get('region', 'us-east-1')
        self.access_key = s3_config.get('access_key')
        self.secret_key = s3_config.get('secret_key')

        # Initialize S3 client
        self.s3_client = None
        if self.access_key and self.secret_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )

    def connect(self) -> bool:
        """Establish S3 connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.s3_client:
                self.logger.error("S3 client not initialized - missing credentials")
                return False

            # Test connection by listing buckets
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.logger.info("S3 connection established")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to connect to S3: {e}")
            return False

    def load_json(self, data: Union[Dict[str, Any], List[Dict[str, Any]]],
                  key: str, mode: str = 'overwrite') -> bool:
        """Load weather data as JSON to S3.

        Args:
            data: Weather data to load
            key: S3 object key
            mode: 'overwrite' or 'append' (for lists)

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.s3_client:
                if not self.connect():
                    return False

            if mode == 'append' and self._key_exists(key):
                # Load existing data and append
                existing_data = self._load_json_from_s3(key)
                if isinstance(existing_data, list) and isinstance(data, list):
                    existing_data.extend(data)
                    data = existing_data
                elif isinstance(existing_data, dict) and isinstance(data, dict):
                    # Merge dictionaries (data takes precedence)
                    existing_data.update(data)
                    data = existing_data

            # Convert to JSON
            json_data = json.dumps(data, indent=2, default=str)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data,
                ContentType='application/json'
            )

            self.logger.info(f"Successfully loaded JSON data to s3://{self.bucket_name}/{key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load JSON data to S3: {e}")
            return False

    def load_parquet(self, data: Union[Dict[str, Any], List[Dict[str, Any]]],
                     key: str, mode: str = 'overwrite') -> bool:
        """Load weather data as Parquet to S3.

        Args:
            data: Weather data to load
            key: S3 object key
            mode: 'overwrite' or 'append'

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.s3_client:
                if not self.connect():
                    return False

            # Convert to DataFrame
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

            if mode == 'append' and self._key_exists(key):
                # Load existing parquet and append
                existing_df = self._load_parquet_from_s3(key)
                if existing_df is not None:
                    df = pd.concat([existing_df, df], ignore_index=True)

            # Convert to parquet
            buffer = io.BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream'
            )

            self.logger.info(f"Successfully loaded Parquet data to s3://{self.bucket_name}/{key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load Parquet data to S3: {e}")
            return False

    def load_csv(self, data: Union[Dict[str, Any], List[Dict[str, Any]]],
                 key: str, mode: str = 'overwrite') -> bool:
        """Load weather data as CSV to S3.

        Args:
            data: Weather data to load
            key: S3 object key
            mode: 'overwrite' or 'append'

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.s3_client:
                if not self.connect():
                    return False

            # Convert to DataFrame
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

            if mode == 'append' and self._key_exists(key):
                # Load existing CSV and append
                existing_df = self._load_csv_from_s3(key)
                if existing_df is not None:
                    df = pd.concat([existing_df, df], ignore_index=True)

            # Convert to CSV
            csv_data = df.to_csv(index=False)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=csv_data,
                ContentType='text/csv'
            )

            self.logger.info(f"Successfully loaded CSV data to s3://{self.bucket_name}/{key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load CSV data to S3: {e}")
            return False

    def _key_exists(self, key: str) -> bool:
        """Check if S3 key exists."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def _load_json_from_s3(self, key: str) -> Optional[Union[Dict, List]]:
        """Load JSON data from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            return data
        except Exception as e:
            self.logger.error(f"Failed to load JSON from S3: {e}")
            return None

    def _load_parquet_from_s3(self, key: str) -> Optional[pd.DataFrame]:
        """Load Parquet data from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            buffer = io.BytesIO(response['Body'].read())
            df = pd.read_parquet(buffer)
            return df
        except Exception as e:
            self.logger.error(f"Failed to load Parquet from S3: {e}")
            return None

    def _load_csv_from_s3(self, key: str) -> Optional[pd.DataFrame]:
        """Load CSV data from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            df = pd.read_csv(io.StringIO(response['Body'].read().decode('utf-8')))
            return df
        except Exception as e:
            self.logger.error(f"Failed to load CSV from S3: {e}")
            return None

    def list_objects(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List objects in S3 bucket with optional prefix.

        Args:
            prefix: Object key prefix to filter by

        Returns:
            List of object information dictionaries
        """
        try:
            if not self.s3_client:
                if not self.connect():
                    return []

            objects = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'],
                            'etag': obj['ETag']
                        })

            return objects

        except Exception as e:
            self.logger.error(f"Failed to list S3 objects: {e}")
            return []

    def delete_object(self, key: str) -> bool:
        """Delete an object from S3.

        Args:
            key: S3 object key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.s3_client:
                if not self.connect():
                    return False

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            self.logger.info(f"Successfully deleted s3://{self.bucket_name}/{key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete S3 object: {e}")
            return False
