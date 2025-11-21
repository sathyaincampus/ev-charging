from datetime import datetime
from strands.tools import tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_amenities, get_mock_menu
import json

@tool
def check_nearby_amenities(location: str) -> str:
    """Check available restaurants and facilities near charging location"""
    # Always return mock amenities for demo purposes
    # In production, this would query Google Places API or similar
    result = get_mock_amenities(location)
    return json.dumps(result)

@tool
def get_restaurant_menu(restaurant_name: str) -> str:
    """Get menu items from a restaurant"""
    # Always return mock menu for demo purposes
    # In production, this would query restaurant APIs
    result = get_mock_menu(restaurant_name)
    return json.dumps(result)

@tool
def place_food_order(restaurant: str, items: list, pickup_time: str) -> str:
    """Place a mobile order for food/drinks"""
    total = sum([5.50 if 'coffee' in i.lower() or 'latte' in i.lower() else 8.00 for i in items])
    result = {
        "order_id": f"ORD-{int(datetime.now().timestamp())}",
        "restaurant": restaurant,
        "items": items,
        "total_usd": round(total, 2),
        "pickup_time": pickup_time,
        "status": "confirmed"
    }
    return json.dumps(result)
