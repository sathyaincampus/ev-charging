from datetime import datetime

def get_mock_chargers(route, location):
    return [
        {
            "id": "CHG-101",
            "network": "EVgo",
            "location": "Tejon Ranch, CA",
            "address": "5161 Outlets at Tejon Pkwy",
            "power_kw": 350,
            "price_per_kwh": 0.43,
            "available": True,
            "slots": ["10:00", "10:30", "11:00"],
            "amenities": ["Starbucks", "Restrooms", "WiFi"]
        },
        {
            "id": "CHG-102",
            "network": "Electrify America",
            "location": "Bakersfield, CA",
            "address": "9000 Ming Ave",
            "power_kw": 150,
            "price_per_kwh": 0.38,
            "available": True,
            "slots": ["10:15", "11:00", "11:30"],
            "amenities": ["Subway", "Restrooms"]
        },
        {
            "id": "CHG-103",
            "network": "Tesla Supercharger",
            "location": "Lebec, CA",
            "address": "5172 Frazier Mountain Park Rd",
            "power_kw": 250,
            "price_per_kwh": 0.45,
            "available": True,
            "slots": ["09:45", "10:00", "10:15"],
            "amenities": ["Convenience Store", "Restrooms"]
        }
    ]

def get_mock_amenities(location):
    """Return mock amenities for any location.
    In production, this would query Google Places API or similar."""
    return {
        "restaurants": ["Starbucks", "Subway", "McDonald's"],
        "facilities": ["Restrooms", "WiFi", "Convenience Store", "ATM"],
        "note": f"Mock amenities for {location} - In production, would query real nearby businesses"
    }

def get_mock_menu(restaurant):
    menus = {
        "Starbucks": ["Large Latte", "Cappuccino", "Breakfast Sandwich", "Croissant"],
        "Subway": ["6-inch Turkey Sub", "Footlong Italian BMT", "Cookies"],
        "McDonald's": ["Big Mac", "Chicken McNuggets", "Coffee", "Hash Browns"]
    }
    return menus.get(restaurant, [])
