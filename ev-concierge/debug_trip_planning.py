#!/usr/bin/env python3
"""
Debug script to test trip planning agent
"""
from agents.trip_planning import TripPlanningAgent

# Test with low battery, long trip (should need charging)
vehicle_data = {
    "model": "Tesla Model Y",
    "battery_percent": 28,
    "range_miles": 300
}

trip_data = {
    "origin": "Los Angeles, CA",
    "destination": "San Francisco, CA",
    "distance_miles": 380,
    "departure": "2024-01-15T09:00:00"
}

print("🧪 Testing Trip Planning Agent")
print("=" * 60)
print(f"Battery: {vehicle_data['battery_percent']}%")
print(f"Range: {vehicle_data['range_miles']} miles")
print(f"Trip: {trip_data['distance_miles']} miles")
print(f"Expected: CHARGING NEEDED")
print("=" * 60)

agent = TripPlanningAgent()
result = agent.analyze(vehicle_data, trip_data)

print("\n📊 RESULTS:")
print("=" * 60)
print(f"Analysis: {result['analysis']}")
print(f"\nTool Results: {result['tool_results']}")

if result['tool_results']:
    for tool_result in result['tool_results']:
        if isinstance(tool_result, dict) and 'needs_charging' in tool_result:
            needs_charging = tool_result['needs_charging']
            print(f"\n✅ Needs Charging: {needs_charging}")
            print(f"✅ Deficit: {tool_result.get('deficit_percent', 0)}%")
            
            if needs_charging:
                print("\n✅ SUCCESS: Tool correctly identified charging needed!")
            else:
                print("\n❌ FAIL: Should have identified charging needed!")
else:
    print("\n❌ FAIL: No tools were called!")
    print("   Check the Strands SDK implementation")

print("=" * 60)
