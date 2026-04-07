#!/usr/bin/env python3
"""Test script to verify the weather platform works."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from core.transform.unit_converter import UnitConverter
from core.transform.cleaner import DataCleaner
from core.transform.feature_engineering import FeatureEngineer
from core.load.csv_loader import CSVLoader
import tempfile

def test_unit_converter():
    """Test unit conversion functionality."""
    print("Testing Unit Converter...")
    uc = UnitConverter()

    # Test temperature conversion
    celsius = 25
    fahrenheit = uc.celsius_to_fahrenheit(celsius)
    assert fahrenheit == 77, f"Expected 77, got {fahrenheit}"
    print(f"✓ Celsius to Fahrenheit: {celsius}°C = {fahrenheit}°F")

    # Test wind speed conversion
    mps = 10
    kmph = uc.mps_to_kmph(mps)
    assert kmph == 36, f"Expected 36, got {kmph}"
    print(f"✓ Meters/second to km/h: {mps} m/s = {kmph} km/h")

    print("Unit Converter tests passed!\n")

def test_data_cleaner():
    """Test data cleaning functionality."""
    print("Testing Data Cleaner...")
    dc = DataCleaner()

    # Test data cleaning
    test_data = {
        'temperature': 25.5,
        'humidity': 65,
        'pressure': 1013.25,
        'wind': {'speed': 5.2, 'direction': 180}
    }

    cleaned = dc.clean_weather_data(test_data)
    assert 'temperature' in cleaned, "Temperature not in cleaned data"
    assert cleaned['temperature'] == 25.5, f"Expected 25.5, got {cleaned['temperature']}"
    print("✓ Data cleaning works correctly")

    print("Data Cleaner tests passed!\n")

def test_feature_engineering():
    """Test feature engineering functionality."""
    print("Testing Feature Engineering...")
    fe = FeatureEngineer()

    from datetime import datetime
    test_data = {
        'timestamp': datetime(2023, 6, 15, 14, 30),
        'temperature': 25.5,
        'humidity': 65,
        'weather': {'main': 'Clear'},
        'wind': {'speed': 5.2}
    }

    engineered = fe.engineer_features(test_data)
    assert 'hour' in engineered, "Hour feature not added"
    assert engineered['hour'] == 14, f"Expected hour 14, got {engineered['hour']}"
    assert 'is_clear' in engineered, "Weather feature not added"
    assert engineered['is_clear'] == 1, f"Expected is_clear=1, got {engineered['is_clear']}"
    print("✓ Feature engineering works correctly")

    print("Feature Engineering tests passed!\n")

def test_csv_loader():
    """Test CSV loading functionality."""
    print("Testing CSV Loader...")
    cl = CSVLoader({})

    # Test data
    test_data = [
        {
            'timestamp': '2023-06-15 14:30:00',
            'city': 'Test City',
            'temperature': 25.5,
            'humidity': 65
        }
    ]

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    try:
        # Load data to CSV
        success = cl.load(test_data, temp_file)
        assert success, "CSV loading failed"
        print("✓ CSV loading works correctly")

        # Verify file was created and contains data
        assert os.path.exists(temp_file), "CSV file was not created"

        # Check file contents
        with open(temp_file, 'r') as f:
            content = f.read()
            assert 'Test City' in content, "Data not written to CSV"
            assert '25.5' in content, "Temperature not written to CSV"

        print("✓ CSV file created and contains correct data")

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    print("CSV Loader tests passed!\n")

def main():
    """Run all tests."""
    print("🧪 Running Weather Platform Tests\n")
    print("=" * 50)

    try:
        test_unit_converter()
        test_data_cleaner()
        test_feature_engineering()
        test_csv_loader()

        print("=" * 50)
        print("🎉 All tests passed! Your weather platform is working correctly.")
        print("\nTo run the full platform:")
        print("1. Set up your OpenWeatherMap API key in .env file")
        print("2. Run: python main.py pipeline")
        print("3. Start API: python main.py api")
        print("4. Start dashboard: python main.py dashboard")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()