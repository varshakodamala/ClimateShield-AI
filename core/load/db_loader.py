"""Database loader for weather data."""

from typing import Dict, Any, List, Optional, Union
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseLoader:
    """Handles loading weather data to database."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.engine = None
        self.metadata = MetaData()

    def connect(self) -> bool:
        """Establish database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            db_config = self.config.get('database', {})

            # Build connection string
            if db_config.get('type', 'postgresql') == 'postgresql':
                db_name = db_config.get('name') or db_config.get('database')
                connection_string = (
                    f"postgresql://{db_config.get('user')}:{db_config.get('password')}@"
                    f"{db_config.get('host')}:{db_config.get('port')}/{db_name}"
                )
            else:
                # Add support for other databases as needed
                self.logger.error(f"Unsupported database type: {db_config.get('type')}")
                return False

            self.engine = create_engine(connection_string, echo=False)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))

            self.logger.info("Database connection established")
            return True

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")

    def create_tables(self) -> bool:
        """Create weather data tables if they don't exist.

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.engine:
                if not self.connect():
                    return False

            # Weather data table
            weather_table = Table(
                'weather_data',
                self.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('timestamp', DateTime, nullable=False, index=True),
                Column('city', String(100), nullable=False, index=True),
                Column('country', String(10)),
                Column('latitude', Float),
                Column('longitude', Float),
                Column('temperature', Float),
                Column('feels_like', Float),
                Column('humidity', Float),
                Column('pressure', Float),
                Column('weather_main', String(50)),
                Column('weather_description', Text),
                Column('weather_icon', String(10)),
                Column('wind_speed', Float),
                Column('wind_direction', Float),
                Column('clouds', Float),
                Column('visibility', Float),
                Column('rain_1h', Float),
                Column('snow_1h', Float),
                Column('sunrise', DateTime),
                Column('sunset', DateTime),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            )

            # Create tables
            self.metadata.create_all(self.engine)
            self.logger.info("Database tables created successfully")
            return True

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to create tables: {e}")
            return False

    def load(self, data: Union[Dict[str, Any], List[Dict[str, Any]]],
             table_name: str = 'weather_data', mode: str = 'append') -> bool:
        """Load weather data to database table.

        Args:
            data: Weather data to load
            table_name: Target table name
            mode: 'append' or 'replace'

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.engine:
                if not self.connect():
                    return False

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

            # Transform data to match table schema
            df = self._transform_data_for_db(df)

            # Load data
            if mode == 'replace':
                df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            else:  # append
                df.to_sql(table_name, self.engine, if_exists='append', index=False)

            self.logger.info(f"Successfully loaded {len(df)} records to {table_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load data to database: {e}")
            return False

    def _transform_data_for_db(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform DataFrame to match database schema."""
        try:
            # Rename columns to match schema
            column_mapping = {
                'coordinates.lat': 'latitude',
                'coordinates.lon': 'longitude',
                'weather.main': 'weather_main',
                'weather.description': 'weather_description',
                'weather.icon': 'weather_icon',
                'wind.speed': 'wind_speed',
                'wind.direction': 'wind_direction',
                'rain': 'rain_1h',
                'snow': 'snow_1h'
            }

            # Flatten nested columns
            if 'coordinates' in df.columns:
                coords = pd.json_normalize(df['coordinates'])
                df = df.drop('coordinates', axis=1).join(coords)

            if 'weather' in df.columns:
                weather = pd.json_normalize(df['weather'])
                df = df.drop('weather', axis=1).join(weather)

            if 'wind' in df.columns:
                wind = pd.json_normalize(df['wind'])
                df = df.drop('wind', axis=1).join(wind)

            # Rename columns
            df = df.rename(columns=column_mapping)

            # Ensure timestamp is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Convert sunrise/sunset to datetime if they exist
            for col in ['sunrise', 'sunset']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            return df

        except Exception as e:
            self.logger.error(f"Error transforming data for database: {e}")
            return df

    def load_batch(self, data_list: List[List[Dict[str, Any]]],
                   table_names: List[str], mode: str = 'append') -> List[bool]:
        """Load multiple batches of data to different tables.

        Args:
            data_list: List of data batches
            table_names: Corresponding table names
            mode: 'append' or 'replace'

        Returns:
            List of success flags
        """
        if len(data_list) != len(table_names):
            self.logger.error("Data list and table names must have the same length")
            return [False] * len(data_list)

        results = []
        for data, table_name in zip(data_list, table_names):
            success = self.load(data, table_name, mode)
            results.append(success)

        return results

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[pd.DataFrame]:
        """Execute a custom SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query results as DataFrame or None if error
        """
        try:
            if not self.engine:
                if not self.connect():
                    return None

            with self.engine.connect() as conn:
                result = conn.execute(sa.text(query), params or {})
                return pd.DataFrame(result.fetchall(), columns=result.keys())

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to execute query: {e}")
            return None

    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a database table.

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with table information or None if error
        """
        try:
            if not self.engine:
                if not self.connect():
                    return None

            with self.engine.connect() as conn:
                # Get row count
                result = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.fetchone()[0]

                # Get column information
                result = conn.execute(sa.text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()

                # Get table size
                result = conn.execute(sa.text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table_name}'))
                """))
                size = result.fetchone()[0]

                info = {
                    'table_name': table_name,
                    'row_count': row_count,
                    'size': size,
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2] == 'YES'
                        } for col in columns
                    ]
                }

                return info

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get table info: {e}")
            return None

    def create_indexes(self, table_name: str, indexes: List[Dict[str, Any]]) -> bool:
        """Create indexes on a table.

        Args:
            indexes: List of index definitions with 'columns' and optional 'unique' flag

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.engine:
                if not self.connect():
                    return False

            with self.engine.begin() as conn:
                for index_def in indexes:
                    columns = index_def['columns']
                    unique = index_def.get('unique', False)

                    index_name = f"idx_{table_name}_{'_'.join(columns)}"
                    unique_str = "UNIQUE" if unique else ""

                    columns_str = ', '.join(columns)
                    query = f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"

                    conn.execute(sa.text(query))

            self.logger.info(f"Created indexes on {table_name}")
            return True

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to create indexes: {e}")
            return False

    def upsert_data(self, data: List[Dict[str, Any]], table_name: str,
                   conflict_columns: List[str]) -> bool:
        """Upsert (insert or update) data in database.

        Args:
            data: Data to upsert
            table_name: Target table name
            conflict_columns: Columns to check for conflicts

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.engine:
                if not self.connect():
                    return False

            if not data:
                return True

            df = pd.DataFrame(data)
            df = self._transform_data_for_db(df)

            # For PostgreSQL, use ON CONFLICT
            table = Table(table_name, self.metadata, autoload_with=self.engine)

            insert_stmt = insert(table).values(df.to_dict(orient='records'))
            update_cols = {
                col: insert_stmt.excluded[col]
                for col in df.columns
                if col not in conflict_columns
            }
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=conflict_columns,
                set_=update_cols
            )

            with self.engine.begin() as conn:
                conn.execute(upsert_stmt)

            self.logger.info(f"Successfully upserted {len(data)} records to {table_name}")
            return True

        except SQLAlchemyError as e:
            self.logger.error(f"Failed to upsert data: {e}")
            return False
