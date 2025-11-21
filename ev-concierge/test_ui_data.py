#!/usr/bin/env python3
"""
Test to see what data the UI will receive
"""

from agents.coordinator import CoordinatorAgent
from datetime import datetime, timedelta
import json

print("=" * 70)
print("Testing UI Data Flow")
print("=" * 70)

coordinator = CoordinatorAgent()

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

print(f"\n🚗 Vehicle: {vehicle['battery_percent']}% battery")
print(f"🗺️  Trip: {trip['origin']} → {trip['destination']} ({trip['distance_miles']} mi)")
print(f"\n⏳ Running coordinator...\n")

result = coordinator.orchestrate(vehicle, trip, preferences)

print("\n" + "=" * 70)
print("RESULT STRUCTURE")
print("=" * 70)

print(f"\nSummary: {result.get('summary', 'N/A')[:200]}...")

if 'results' in result:
    print(f"\nResults keys: {list(result['results'].keys())}")
    
    if 'charging' in result['results']:
        print("\n📍 CHARGING RESULTS:")
        charging = result['results']['charging']
        tool_results = charging.get('tool_results', [])
        
        print(f"   Number of tool results: {len(tool_results)}")
        
        for i, tool_result in enumerate(tool_results):
            if isinstance(tool_result, list):
                print(f"\n   Tool Result {i+1}: List of {len(tool_result)} stations")
                for j, station in enumerate(tool_result[:3], 1):
                    print(f"      {j}. {station.get('network')} - {station.get('location')}")
                    print(f"         Power: {station.get('power_kw')} kW")
            elif isinstance(tool_result, dict):
                if 'reservation_id' in tool_result:
                    print(f"\n   Tool Result {i+1}: Reservation")
                    print(f"      ID: {tool_result.get('reservation_id')}")
                    print(f"      Network: {tool_result.get('network', 'N/A')}")
                    print(f"      Location: {tool_result.get('location', 'N/A')}")

print("\n" + "=" * 70)
