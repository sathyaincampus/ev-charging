"""
Location coordinate mappings for cities in the EV Concierge application.
Maps city names to (latitude, longitude) tuples for OpenChargeMap API queries.
"""

CITY_COORDINATES = {
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Francisco, CA": (37.7749, -122.4194),
    "San Diego, CA": (32.7157, -117.1611),
    "Seattle, WA": (47.6062, -122.3321),
    "Las Vegas, NV": (36.1699, -115.1398),
}

def get_coordinates(city_name: str) -> tuple[float, float] | None:
    """
    Get coordinates for a city name.
    
    Args:
        city_name: City name (e.g., "Los Angeles, CA")
    
    Returns:
        Tuple of (latitude, longitude) or None if city not found
    """
    return CITY_COORDINATES.get(city_name)

def calculate_midpoint(coord1: tuple[float, float], coord2: tuple[float, float]) -> tuple[float, float]:
    """
    Calculate the midpoint between two coordinates.
    
    Args:
        coord1: First coordinate (lat, lon)
        coord2: Second coordinate (lat, lon)
    
    Returns:
        Midpoint coordinate (lat, lon)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return ((lat1 + lat2) / 2, (lon1 + lon2) / 2)

def calculate_distance_km(coord1: tuple[float, float], coord2: tuple[float, float]) -> float:
    """
    Calculate approximate distance between two coordinates in kilometers.
    Uses simple Euclidean distance (good enough for bounding box calculations).
    
    Args:
        coord1: First coordinate (lat, lon)
        coord2: Second coordinate (lat, lon)
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Approximate: 1 degree latitude ≈ 111 km, 1 degree longitude ≈ 111 km * cos(latitude)
    import math
    avg_lat = (lat1 + lat2) / 2
    lat_diff_km = (lat2 - lat1) * 111
    lon_diff_km = (lon2 - lon1) * 111 * math.cos(math.radians(avg_lat))
    
    return math.sqrt(lat_diff_km**2 + lon_diff_km**2)
