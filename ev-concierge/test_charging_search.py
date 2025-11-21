#!/usr/bin/env python3
"""
Test the charging search tool directly
"""

from tools.charging_tools import search_chargers
import json

print("=" * 60)
print("Testing Charging Search Tool")
print("=" * 60)

# Test with real API
print("\n🧪 Test: Los Angeles to San Francisco")
result = search_chargers("Los Angeles, CA", "San Francisco, CA", min_power_kw=100)
stations = json.loads(result)

print(f"\n✅ Found {len(stations)} stations:")
for i, station in enumerate(stations[:5], 1):
    print(f"\n{i}. {station['network']} - {station['location']}")
    print(f"   Address: {station['address']}")
    print(f"   Power: {station['power_kw']} kW")
    print(f"   Price: ${station['price_per_kwh']}/kWh")

print("\n" + "=" * 60)
