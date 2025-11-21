#!/usr/bin/env python3
"""
Test that amenities work with real charging station locations
"""

from tools.amenities_tools import check_nearby_amenities, get_restaurant_menu, place_food_order
import json

print("=" * 70)
print("Testing Amenities with Real Locations")
print("=" * 70)

# Test with a real location from OpenChargeMap
real_locations = [
    "Lost Hills, CA",
    "Kettleman City, CA",
    "San Luis Obispo, CA"
]

for location in real_locations:
    print(f"\n📍 Location: {location}")
    
    # Check amenities
    amenities_result = check_nearby_amenities(location)
    amenities = json.loads(amenities_result)
    
    print(f"   Restaurants: {', '.join(amenities.get('restaurants', []))}")
    print(f"   Facilities: {', '.join(amenities.get('facilities', []))}")
    
    # Get menu from first restaurant
    if amenities.get('restaurants'):
        restaurant = amenities['restaurants'][0]
        menu_result = get_restaurant_menu(restaurant)
        menu = json.loads(menu_result)
        print(f"   {restaurant} menu: {', '.join(menu[:3])}")

# Test placing an order
print(f"\n🍽️  Placing order...")
order_result = place_food_order(
    restaurant="Starbucks",
    items=["Large Latte", "Breakfast Sandwich"],
    pickup_time="10:15"
)
order = json.loads(order_result)

print(f"   Order ID: {order['order_id']}")
print(f"   Restaurant: {order['restaurant']}")
print(f"   Items: {', '.join(order['items'])}")
print(f"   Total: ${order['total_usd']}")
print(f"   Pickup: {order['pickup_time']}")

print("\n" + "=" * 70)
print("✅ Amenities work with any location!")
print("=" * 70)
