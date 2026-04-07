-- Weather Data Platform Database Initialization

-- Create database (if not exists)
-- Note: This is handled by docker-compose, but included for reference

-- Create weather_data table
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    temperature FLOAT,
    feels_like FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    weather_main VARCHAR(50),
    weather_description TEXT,
    weather_icon VARCHAR(10),
    wind_speed FLOAT,
    wind_direction FLOAT,
    clouds FLOAT,
    visibility FLOAT,
    rain_1h FLOAT,
    snow_1h FLOAT,
    sunrise TIMESTAMP,
    sunset TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_weather_data_timestamp ON weather_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_data_city ON weather_data(city);
CREATE INDEX IF NOT EXISTS idx_weather_data_country ON weather_data(country);

-- Create daily_aggregations table for analytics
CREATE TABLE IF NOT EXISTS daily_weather_aggregations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    cities_covered INTEGER,
    avg_temperature_global FLOAT,
    max_temperature FLOAT,
    min_temperature FLOAT,
    total_records INTEGER,
    data_quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create alerts table for monitoring
CREATE TABLE IF NOT EXISTS weather_alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    city VARCHAR(100),
    metric VARCHAR(50),
    value FLOAT,
    threshold FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pipeline_runs table for tracking ETL runs
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    pipeline_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    success BOOLEAN,
    records_processed INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data (optional)
-- This is just for testing purposes
INSERT INTO weather_data (
    timestamp, city, country, latitude, longitude,
    temperature, humidity, pressure, weather_main
) VALUES (
    CURRENT_TIMESTAMP, 'Test City', 'TC', 40.7128, -74.0060,
    25.5, 65.0, 1013.25, 'Clear'
) ON CONFLICT DO NOTHING;