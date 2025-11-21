from datetime import datetime
from strands import Tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_amenities, get_mock_menu

@Tool
def check_nearby_amenities(location: str) -> dict:
    """Check available restaurants and facilities near charging location"""
    if USE_MOCK_DATA:
        return get_mock_amenities(location)
    return {}

@Tool
def get_restaurant_menu(restaurant_name: str) -> list:
    """Get menu items from a restaurant"""
    if USE_MOCK_DATA:
        return get_mock_menu(restaurant_name)
    return []

@Tool
def place_food_order(restaurant: str, items: list, pickup_time: str) -> dict:
    """Place a mobile order for food/drinks"""
    # Calculate total based on item type
    total = 0
    for item in items:
        item_lower = item.lower()
        # Drinks pricing
        if 'latte' in item_lower or 'cappuccino' in item_lower or 'mocha' in item_lower:
            total += 5.50
        elif 'coffee' in item_lower or 'tea' in item_lower or 'espresso' in item_lower:
            total += 3.50
        # Food pricing
        elif 'sandwich' in item_lower or 'burger' in item_lower:
            total += 8.00
        elif 'croissant' in item_lower or 'pastry' in item_lower:
            total += 4.50
        elif 'cookies' in item_lower or 'cookie' in item_lower:
            total += 3.00
        else:
            total += 6.00  # Default price
    
    return {
        "order_id": f"ORD-{int(datetime.now().timestamp())}",
        "restaurant": restaurant,
        "items": items,
        "total_usd": round(total, 2),
        "pickup_time": pickup_time,
        "status": "confirmed"
    }
