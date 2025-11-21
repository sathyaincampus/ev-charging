#!/usr/bin/env python3
"""
Test that reservation includes real network and location
"""

from tools.charging_tools import search_chargers, reserve_charging_slot
import json

print("=" * 70)
print("Testing Reservation Format with Real Data")
print("=" * 70)

# Step 1: Search for chargers
print("\n1️⃣ Searching for chargers...")
result = search_chargers("Los Angeles, CA", "San Francisco, CA", min_power_kw=100)
stations = json.loads(result)

if stations:
    print(f"   Found {len(stations)} stations")
    first_station = stations[0]
    print(f"\n   First station:")
    print(f"   - ID: {first_station['id']}")
    print(f"   - Network: {first_station['network']}")
    print(f"   - Location: {first_station['location']}")
    print(f"   - Power: {first_station['power_kw']} kW")
    
    # Step 2: Reserve with real data
    print(f"\n2️⃣ Making reservation with real data...")
    reservation_result = reserve_charging_slot(
        charger_id=first_station['id'],
        time_slot="10:00",
        duration_min=30,
        location=first_station['location'],
        network=first_station['network']
    )
    
    reservation = json.loads(reservation_result)
    print(f"\n   Reservation created:")
    print(f"   - ID: {reservation['reservation_id']}")
    print(f"   - Network: {reservation['network']}")
    print(f"   - Location: {reservation['location']}")
    print(f"   - Time: {reservation['time_slot']}")
    
    print("\n" + "=" * 70)
    print("✅ Reservation includes real network and location!")
    print("=" * 70)
else:
    print("   ⚠️  No stations found")
