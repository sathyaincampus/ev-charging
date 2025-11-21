#!/usr/bin/env python3
"""
Full integration test with real OpenChargeMap data
"""

from agents.coordinator import CoordinatorAgent
from datetime import datetime, timedelta

print("=" * 70)
print("🚗 EV Concierge - Full Integration Test with Real Charging Data")
print("=" * 70)

# Initialize coordinator
coordinator = CoordinatorAgent()

# Test scenario: Low battery, long trip (will need charging)
vehicle = {
    "model": "Tesla Model Y",
    "battery_percent": 35,
    "range_miles": 300
}

trip = {
    "origin": "Los Angeles, CA",
    "destination": "San Francisco, CA",
    "distance_miles": 380,
    "departure": (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0).isoformat()
}

preferences = {
    "auto_order_coffee": True,
    "favorite_drink": "Large Latte",
    "wallet_id": "WALLET-12345"
}

print(f"\n📊 Test Scenario:")
print(f"   Vehicle: {vehicle['model']}")
print(f"   Battery: {vehicle['battery_percent']}%")
print(f"   Trip: {trip['origin']} → {trip['destination']}")
print(f"   Distance: {trip['distance_miles']} miles")
print(f"\n🔄 Running multi-agent orchestration...\n")

try:
    result = coordinator.orchestrate(vehicle, trip, preferences)
    
    print("\n" + "=" * 70)
    print("✅ RESULTS")
    print("=" * 70)
    print(f"\n{result['summary']}")
    
    # Show charging stations found
    if 'results' in result and 'charging' in result['results']:
        charging_results = result['results']['charging']
        tool_results = charging_results.get('tool_results', [])
        
        print("\n📍 Real Charging Stations Found:")
        for i, tool_result in enumerate(tool_results):
            if isinstance(tool_result, list):
                # This is the search_chargers result
                print(f"\n   Found {len(tool_result)} stations:")
                for j, station in enumerate(tool_result[:3], 1):
                    print(f"\n   {j}. {station.get('network', 'Unknown')} - {station.get('location', 'Unknown')}")
                    print(f"      Address: {station.get('address', 'N/A')}")
                    print(f"      Power: {station.get('power_kw', 0)} kW")
                    print(f"      Price: ${station.get('price_per_kwh', 0)}/kWh")
            elif isinstance(tool_result, dict) and 'reservation_id' in tool_result:
                # This is a reservation
                print(f"\n   ✅ Reservation Made:")
                print(f"      ID: {tool_result.get('reservation_id')}")
                print(f"      Network: {tool_result.get('network', 'N/A')}")
                print(f"      Location: {tool_result.get('location', 'N/A')}")
                print(f"      Time: {tool_result.get('time_slot', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("✅ Integration test complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
