#!/usr/bin/env python
"""Debug import test."""

import sys
import os
print("Python executable:", sys.executable)
print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\n--- Attempting imports ---")

try:
    import sqlalchemy
    print("✓ sqlalchemy imported successfully")
except Exception as e:
    print(f"✗ Failed to import sqlalchemy: {e}")

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from core.load.db_loader import DatabaseLoader
    print("✓ DatabaseLoader imported successfully")
except Exception as e:
    print(f"✗ Failed to import DatabaseLoader: {e}")
    import traceback
    traceback.print_exc()

try:
    from core.pipeline.weather_pipeline import WeatherPipeline
    print("✓ WeatherPipeline imported successfully")
except Exception as e:
    print(f"✗ Failed to import WeatherPipeline: {e}")
    import traceback
    traceback.print_exc()
