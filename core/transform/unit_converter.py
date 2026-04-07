"""Unit conversion utilities for weather data."""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class UnitConverter:
    """Handles unit conversions for weather data."""

    # Temperature conversions
    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return (fahrenheit - 32) * 5/9

    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        """Convert Kelvin to Celsius."""
        return kelvin - 273.15

    @staticmethod
    def celsius_to_kelvin(celsius: float) -> float:
        """Convert Celsius to Kelvin."""
        return celsius + 273.15

    # Wind speed conversions
    @staticmethod
    def mps_to_kmph(mps: float) -> float:
        """Convert meters per second to kilometers per hour."""
        return mps * 3.6

    @staticmethod
    def mps_to_mph(mps: float) -> float:
        """Convert meters per second to miles per hour."""
        return mps * 2.237

    @staticmethod
    def kmph_to_mps(kmph: float) -> float:
        """Convert kilometers per hour to meters per second."""
        return kmph / 3.6

    @staticmethod
    def mph_to_mps(mph: float) -> float:
        """Convert miles per hour to meters per second."""
        return mph / 2.237

    # Pressure conversions
    @staticmethod
    def hpa_to_mmhg(hpa: float) -> float:
        """Convert hectopascals to millimeters of mercury."""
        return hpa * 0.750062

    @staticmethod
    def mmhg_to_hpa(mmhg: float) -> float:
        """Convert millimeters of mercury to hectopascals."""
        return mmhg / 0.750062

    @staticmethod
    def hpa_to_inhg(hpa: float) -> float:
        """Convert hectopascals to inches of mercury."""
        return hpa * 0.02953

    @staticmethod
    def inhg_to_hpa(inhg: float) -> float:
        """Convert inches of mercury to hectopascals."""
        return inhg / 0.02953

    # Distance conversions
    @staticmethod
    def meters_to_kilometers(meters: float) -> float:
        """Convert meters to kilometers."""
        return meters / 1000

    @staticmethod
    def meters_to_miles(meters: float) -> float:
        """Convert meters to miles."""
        return meters * 0.000621371

    @staticmethod
    def kilometers_to_meters(km: float) -> float:
        """Convert kilometers to meters."""
        return km * 1000

    @staticmethod
    def miles_to_meters(miles: float) -> float:
        """Convert miles to meters."""
        return miles / 0.000621371

    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between units."""
        # First convert to Celsius as intermediate
        if from_unit.lower() == 'fahrenheit':
            celsius = self.fahrenheit_to_celsius(value)
        elif from_unit.lower() == 'kelvin':
            celsius = self.kelvin_to_celsius(value)
        elif from_unit.lower() == 'celsius':
            celsius = value
        else:
            raise ValueError(f"Unsupported temperature unit: {from_unit}")

        # Then convert to target unit
        if to_unit.lower() == 'fahrenheit':
            return self.celsius_to_fahrenheit(celsius)
        elif to_unit.lower() == 'kelvin':
            return self.celsius_to_kelvin(celsius)
        elif to_unit.lower() == 'celsius':
            return celsius
        else:
            raise ValueError(f"Unsupported temperature unit: {to_unit}")

    def convert_wind_speed(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert wind speed between units."""
        # First convert to m/s as intermediate
        if from_unit.lower() in ['m/s', 'mps']:
            mps = value
        elif from_unit.lower() in ['km/h', 'kmph']:
            mps = self.kmph_to_mps(value)
        elif from_unit.lower() in ['mph', 'mi/h']:
            mps = self.mph_to_mps(value)
        else:
            raise ValueError(f"Unsupported wind speed unit: {from_unit}")

        # Then convert to target unit
        if to_unit.lower() in ['m/s', 'mps']:
            return mps
        elif to_unit.lower() in ['km/h', 'kmph']:
            return self.mps_to_kmph(mps)
        elif to_unit.lower() in ['mph', 'mi/h']:
            return self.mps_to_mph(mps)
        else:
            raise ValueError(f"Unsupported wind speed unit: {to_unit}")

    def convert_pressure(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert pressure between units."""
        # First convert to hPa as intermediate
        if from_unit.lower() in ['hpa', 'hectopascal', 'millibar', 'mb']:
            hpa = value
        elif from_unit.lower() in ['mmhg', 'torr']:
            hpa = self.mmhg_to_hpa(value)
        elif from_unit.lower() in ['inhg']:
            hpa = self.inhg_to_hpa(value)
        else:
            raise ValueError(f"Unsupported pressure unit: {from_unit}")

        # Then convert to target unit
        if to_unit.lower() in ['hpa', 'hectopascal', 'millibar', 'mb']:
            return hpa
        elif to_unit.lower() in ['mmhg', 'torr']:
            return self.hpa_to_mmhg(hpa)
        elif to_unit.lower() in ['inhg']:
            return self.hpa_to_inhg(hpa)
        else:
            raise ValueError(f"Unsupported pressure unit: {to_unit}")

    def convert_distance(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert distance between units."""
        # First convert to meters as intermediate
        if from_unit.lower() in ['m', 'meters']:
            meters = value
        elif from_unit.lower() in ['km', 'kilometers']:
            meters = self.kilometers_to_meters(value)
        elif from_unit.lower() in ['mi', 'miles']:
            meters = self.miles_to_meters(value)
        else:
            raise ValueError(f"Unsupported distance unit: {from_unit}")

        # Then convert to target unit
        if to_unit.lower() in ['m', 'meters']:
            return meters
        elif to_unit.lower() in ['km', 'kilometers']:
            return self.meters_to_kilometers(meters)
        elif to_unit.lower() in ['mi', 'miles']:
            return self.meters_to_miles(meters)
        else:
            raise ValueError(f"Unsupported distance unit: {to_unit}")

    def convert_weather_data(self, data: Dict[str, Any], target_units: Dict[str, str]) -> Dict[str, Any]:
        """Convert weather data to target units."""
        converted_data = data.copy()

        try:
            # Convert temperature fields
            temp_fields = ['temperature', 'feels_like']
            for field in temp_fields:
                if field in converted_data and converted_data[field] is not None:
                    if 'temperature' in target_units:
                        converted_data[field] = self.convert_temperature(
                            converted_data[field], 'celsius', target_units['temperature']
                        )

            # Convert wind speed
            if 'wind' in converted_data and isinstance(converted_data['wind'], dict):
                if 'speed' in converted_data['wind'] and converted_data['wind']['speed'] is not None:
                    if 'wind_speed' in target_units:
                        converted_data['wind']['speed'] = self.convert_wind_speed(
                            converted_data['wind']['speed'], 'm/s', target_units['wind_speed']
                        )

            # Convert pressure
            if 'pressure' in converted_data and converted_data['pressure'] is not None:
                if 'pressure' in target_units:
                    converted_data['pressure'] = self.convert_pressure(
                        converted_data['pressure'], 'hPa', target_units['pressure']
                    )

            # Convert visibility
            if 'visibility' in converted_data and converted_data['visibility'] is not None:
                if 'distance' in target_units:
                    converted_data['visibility'] = self.convert_distance(
                        converted_data['visibility'], 'm', target_units['distance']
                    )

        except Exception as e:
            logger.error(f"Error converting weather data units: {e}")
            # Return original data if conversion fails
            return data

        return converted_data
