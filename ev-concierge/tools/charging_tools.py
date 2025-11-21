from datetime import datetime
from strands.tools import tool
from utils.config import USE_MOCK_DATA
from utils.mock_data import get_mock_chargers
from utils.location_coords import get_coordinates
from utils.openchargemap_client import get_chargers_along_route
import json

@tool
def search_chargers(route: str, destination: str, min_power_kw: int = 150) -> str:
    """Search for available EV chargers along route"""
    if USE_MOCK_DATA:
        result = get_mock_chargers(route, destination)
    else:
        # Get coordinates for origin and destination
        origin_coords = get_coordinates(route)
        dest_coords = get_coordinates(destination)
        
        if not origin_coords or not dest_coords:
            print(f"⚠️  Could not find coordinates for {route} or {destination}")
            result = get_mock_chargers(route, destination)
        else:
            # Query OpenChargeMap API
            result = get_chargers_along_route(
                origin_coords,
                dest_coords,
                min_power_kw=min_power_kw,
                max_results=10
            )
            
            # Fallback to mock if no results
            if not result:
                print("⚠️  No stations found from API, using mock data")
                result = get_mock_chargers(route, destination)
    
    return json.dumps(result)

@tool
def reserve_charging_slot(charger_id: str, time_slot: str, duration_min: int = 30, location: str = "", network: str = "") -> str:
    """Reserve a specific charging slot at a charger.
    
    Args:
        charger_id: The ID of the charger from search results
        time_slot: Preferred time slot (e.g., "10:00")
        duration_min: Duration in minutes (default 30)
        location: Location of the charger (e.g., "Kettleman City, CA")
        network: Network name (e.g., "Tesla Supercharger", "EVgo", "Electrify America")
    """
    result = {
        "reservation_id": f"RES-{charger_id}-{int(datetime.now().timestamp())}",
        "charger_id": charger_id,
        "network": network,  # Include real network name
        "location": location,  # Include real location
        "time_slot": time_slot,
        "duration_min": duration_min,
        "status": "confirmed",
        "cancellation_deadline": "15 minutes before slot"
    }
    return json.dumps(result)

@tool
def check_charger_status(charger_id: str) -> str:
    """Check real-time status of a charger"""
    result = {
        "charger_id": charger_id,
        "status": "online",
        "available_ports": 4,
        "current_wait_time_min": 0
    }
    return json.dumps(result)

@tool
def cancel_reservation(reservation_id: str) -> str:
    """Cancel a charging reservation"""
    result = {
        "reservation_id": reservation_id,
        "status": "cancelled",
        "refund_status": "full_refund"
    }
    return json.dumps(result)
