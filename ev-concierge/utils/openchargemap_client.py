"""
OpenChargeMap API client for fetching real charging station data.
"""

import requests
import os
from typing import Optional
from dotenv import load_dotenv
from utils.location_coords import calculate_midpoint, calculate_distance_km

# Load environment variables
load_dotenv()

# Network name mapping
NETWORK_MAPPING = {
    "EVgo Network": "EVgo",
    "EVgo": "EVgo",
    "ChargePoint Network": "ChargePoint",
    "ChargePoint": "ChargePoint",
    "Electrify America": "Electrify America",
    "Tesla Supercharger": "Tesla Supercharger",
    "Tesla": "Tesla Supercharger",
    "Blink Network": "Blink",
    "Blink": "Blink",
    "Volta": "Volta",
    "Greenlots": "Greenlots",
    "SemaConnect": "SemaConnect",
    "EV Connect": "EV Connect",
    "FLO": "FLO",
    "Webasto": "Webasto",
}

def map_operator_to_network(operator_name: Optional[str]) -> str:
    """
    Map OpenChargeMap operator names to standardized network names.
    
    Args:
        operator_name: Operator name from OpenChargeMap
    
    Returns:
        Standardized network name or original name if not in mapping
    """
    if not operator_name:
        return "Unknown Network"
    
    # Check exact match first
    if operator_name in NETWORK_MAPPING:
        return NETWORK_MAPPING[operator_name]
    
    # Check if any known network name is contained in the operator name
    operator_lower = operator_name.lower()
    for key, value in NETWORK_MAPPING.items():
        if key.lower() in operator_lower:
            return value
    
    return operator_name

def parse_openchargemap_response(api_response: list) -> list[dict]:
    """
    Parse OpenChargeMap API response into internal format.
    
    Args:
        api_response: Raw JSON response from OpenChargeMap (list of POIs)
    
    Returns:
        List of standardized charging station dictionaries
    """
    stations = []
    
    for poi in api_response:
        try:
            # Extract address info
            address_info = poi.get('AddressInfo', {})
            
            # Extract operator - try multiple fields
            operator_info = poi.get('OperatorInfo', {})
            operator_name = operator_info.get('Title') if operator_info else None
            
            # If no operator, try to infer from title or comments
            if not operator_name:
                title = address_info.get('Title', '').lower()
                if 'evgo' in title:
                    operator_name = 'EVgo'
                elif 'chargepoint' in title or 'charge point' in title:
                    operator_name = 'ChargePoint'
                elif 'electrify america' in title:
                    operator_name = 'Electrify America'
                elif 'tesla' in title or 'supercharger' in title:
                    operator_name = 'Tesla Supercharger'
                elif 'blink' in title:
                    operator_name = 'Blink'
            
            network = map_operator_to_network(operator_name)
            
            # Extract location
            title = address_info.get('Title', 'Unknown Location')
            town = address_info.get('Town', '')
            state = address_info.get('StateOrProvince', '')
            location = f"{town}, {state}" if town and state else title
            
            # Extract address
            address_line = address_info.get('AddressLine1', '')
            address = f"{address_line}, {town}, {state}" if address_line else location
            
            # Extract coordinates
            latitude = address_info.get('Latitude')
            longitude = address_info.get('Longitude')
            
            if not latitude or not longitude:
                continue  # Skip stations without coordinates
            
            # Extract power rating (max from all connections)
            connections = poi.get('Connections', [])
            max_power = 0
            for conn in connections:
                power = conn.get('PowerKW')
                if power and power > max_power:
                    max_power = power
            
            # Check operational status
            status_type = poi.get('StatusType', {})
            is_operational = status_type.get('IsOperational', True) if status_type else True
            
            # Extract usage cost (if available)
            usage_cost = poi.get('UsageCost', '')
            price_per_kwh = 0.40  # Default estimate
            if usage_cost and '$' in usage_cost:
                try:
                    # Try to extract price from string like "$0.43/kWh"
                    price_str = usage_cost.split('$')[1].split('/')[0]
                    price_per_kwh = float(price_str)
                except:
                    pass
            
            station = {
                "id": f"OCM-{poi.get('ID', 'unknown')}",
                "network": network,
                "location": location,
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "power_kw": int(max_power) if max_power > 0 else 50,  # Default to 50kW if unknown
                "price_per_kwh": price_per_kwh,
                "available": is_operational,
                "slots": ["10:00", "10:30", "11:00", "11:30", "12:00"],  # Mock slots
                "amenities": []  # Will be populated in future enhancement
            }
            
            stations.append(station)
            
        except Exception as e:
            print(f"Error parsing station: {e}")
            continue
    
    return stations

def get_chargers_along_route(
    origin_coords: tuple[float, float],
    destination_coords: tuple[float, float],
    min_power_kw: int = 50,
    max_results: int = 10,
    distance_km: int = 50
) -> list[dict]:
    """
    Query OpenChargeMap for charging stations along a route.
    
    Args:
        origin_coords: (latitude, longitude) of starting point
        destination_coords: (latitude, longitude) of destination
        min_power_kw: Minimum power rating filter
        max_results: Maximum number of results to return
        distance_km: Search radius from route midpoint in kilometers
    
    Returns:
        List of charging station dictionaries
    """
    api_key = os.getenv('OPENCHARGEMAP_API_KEY', '')
    
    if not api_key:
        print("⚠️  OpenChargeMap API key not found. Falling back to mock data.")
        return []
    
    # Calculate midpoint and search radius
    midpoint = calculate_midpoint(origin_coords, destination_coords)
    route_distance = calculate_distance_km(origin_coords, destination_coords)
    
    # Use route distance / 2 + buffer as search radius
    search_radius = max(distance_km, route_distance / 2 + 30)
    
    # Build API request
    base_url = "https://api.openchargemap.io/v3/poi/"
    params = {
        "key": api_key,
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "distance": search_radius,
        "distanceunit": "KM",
        "maxresults": max_results * 2,  # Get more results to filter
        "minpowerkw": min_power_kw,
        "compact": "false",  # Get full response with operator info
        "verbose": "false"
    }
    
    try:
        print(f"🔍 Querying OpenChargeMap API...")
        print(f"   Midpoint: {midpoint}")
        print(f"   Search radius: {search_radius:.1f} km")
        print(f"   Min power: {min_power_kw} kW")
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"   Found {len(data)} stations from API")
        
        # Parse response
        stations = parse_openchargemap_response(data)
        
        # Sort by distance from origin
        for station in stations:
            station_coords = (station['latitude'], station['longitude'])
            station['_distance_from_origin'] = calculate_distance_km(origin_coords, station_coords)
        
        stations.sort(key=lambda s: s['_distance_from_origin'])
        
        # Remove temporary distance field and limit results
        for station in stations:
            station.pop('_distance_from_origin', None)
        
        return stations[:max_results]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying OpenChargeMap API: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []
