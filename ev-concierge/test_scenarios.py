#!/usr/bin/env python3
"""
Test scenarios for EV Concierge
Different battery/distance combinations to test all agent paths
"""

# City coordinates for API queries
CITY_COORDINATES = {
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Francisco, CA": (37.7749, -122.4194),
    "San Diego, CA": (32.7157, -117.1611),
    "Seattle, WA": (47.6062, -122.3321),
    "Las Vegas, NV": (36.1699, -115.1398),
}

# Test Scenarios
SCENARIOS = {
    "no_charging_needed": {
        "name": "High Battery, Short Trip",
        "description": "Plenty of range, no charging needed",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 80,
            "range_miles": 300
        },
        "trip": {
            "origin": "San Diego, CA",
            "destination": "Los Angeles, CA",
            "distance_miles": 120,
            "departure": "2024-01-15T09:00:00"
        },
        "expected": {
            "needs_charging": False,
            "charging_stops": 0
        }
    },
    
    "one_charging_stop": {
        "name": "Low Battery, Long Trip",
        "description": "Need one charging stop en route",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 30,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "San Francisco, CA",
            "distance_miles": 380,
            "departure": "2024-01-15T09:00:00"
        },
        "expected": {
            "needs_charging": True,
            "charging_stops": 1,
            "amenities_ordered": True,
            "payment_processed": True
        }
    },
    
    "emergency_charging": {
        "name": "Critical Battery, Medium Trip",
        "description": "Very low battery, needs immediate charging",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 15,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "San Diego, CA",
            "distance_miles": 120,
            "departure": "2024-01-15T09:00:00"
        },
        "expected": {
            "needs_charging": True,
            "charging_stops": 1,
            "strategy": "pre-trip"
        }
    },
    
    "multiple_stops": {
        "name": "Very Long Trip",
        "description": "Cross-state trip requiring multiple charging stops",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 50,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "Seattle, WA",
            "distance_miles": 1150,
            "departure": "2024-01-15T06:00:00"
        },
        "expected": {
            "needs_charging": True,
            "charging_stops": 3,
            "amenities_ordered": True
        }
    },
    
    "cold_weather": {
        "name": "Cold Weather Impact",
        "description": "Reduced range due to cold weather",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 60,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "Las Vegas, NV",
            "distance_miles": 270,
            "departure": "2024-01-15T09:00:00"
        },
        "weather": {
            "temp_f": 30  # Cold weather reduces range
        },
        "expected": {
            "needs_charging": True,
            "charging_stops": 1
        }
    },
    
    "user_preference_cheapest": {
        "name": "Cheapest Charging Preference",
        "description": "User wants the cheapest charging option",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 35,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "San Francisco, CA",
            "distance_miles": 380,
            "departure": "2024-01-15T09:00:00"
        },
        "preferences": {
            "charging_priority": "cheapest",
            "auto_order_coffee": False
        },
        "expected": {
            "needs_charging": True,
            "selected_charger_criteria": "lowest_price"
        }
    },
    
    "user_preference_fastest": {
        "name": "Fastest Charging Preference",
        "description": "User wants the fastest charging option",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 35,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "San Francisco, CA",
            "distance_miles": 380,
            "departure": "2024-01-15T09:00:00"
        },
        "preferences": {
            "charging_priority": "fastest",
            "auto_order_coffee": True,
            "favorite_drink": "Large Latte",
            "favorite_food": "Breakfast Sandwich"
        },
        "expected": {
            "needs_charging": True,
            "selected_charger_criteria": "highest_power",
            "amenities_ordered": True
        }
    },
    
    "borderline_case": {
        "name": "Borderline Battery",
        "description": "Just barely enough range (testing edge case)",
        "vehicle": {
            "model": "Tesla Model Y",
            "battery_percent": 55,
            "range_miles": 300
        },
        "trip": {
            "origin": "Los Angeles, CA",
            "destination": "San Diego, CA",
            "distance_miles": 120,
            "departure": "2024-01-15T09:00:00"
        },
        "expected": {
            "needs_charging": False  # Should have just enough with 20% buffer
        }
    }
}

def get_scenario(scenario_name: str) -> dict:
    """Get a specific test scenario"""
    return SCENARIOS.get(scenario_name)

def list_scenarios():
    """List all available scenarios"""
    print("\n📋 Available Test Scenarios:")
    print("=" * 60)
    for key, scenario in SCENARIOS.items():
        print(f"\n🔹 {key}")
        print(f"   Name: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Battery: {scenario['vehicle']['battery_percent']}%")
        print(f"   Distance: {scenario['trip']['distance_miles']} miles")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    list_scenarios()
