# Design Document

## Overview

This design integrates the OpenChargeMap API into the EV Concierge application to replace mock charging station data with real-time information. The system will query OpenChargeMap's REST API to find charging stations along a route, parse the response data, map operators to known charging networks, and present accurate location and power information to users.

The OpenChargeMap API provides a comprehensive global database of EV charging locations with details including operator, location, power ratings, and connection types. We will use the `/poi/` endpoint with geographic bounding box queries to find stations along routes.

## Architecture

### Current Architecture
- `charging_tools.py`: Contains `search_chargers()` function that returns mock data
- `mock_data.py`: Provides hardcoded charging station data
- `config.py`: Manages `USE_MOCK_DATA` flag
- Trip planning agent calls `search_chargers()` with route and destination

### New Architecture
- Add `openchargemap_client.py`: New module for API communication
- Update `charging_tools.py`: Integrate real API calls when `USE_MOCK_DATA=false`
- Update `config.py`: Add OpenChargeMap API key configuration
- Add network mapping logic to standardize operator names
- Add coordinate utilities for route-based queries

### Data Flow
1. User enters origin and destination in UI
2. Trip planning agent determines if charging is needed
3. If charging needed, `search_chargers()` is called with route info
4. System checks `USE_MOCK_DATA` flag
5. If false, query OpenChargeMap API with route coordinates
6. Parse API response and map to internal format
7. Return standardized charging station data with real network names (EVgo, ChargePoint, etc.)
8. Display results in UI with network, location, and power info
9. When user/agent selects a station, `reserve_charging_slot()` creates a mock reservation
10. Reservation response includes the real station ID, network, and location from OpenChargeMap
11. UI displays the booked station with correct network type and details

## Components and Interfaces

### OpenChargeMap Client Module

**File**: `ev-concierge/utils/openchargemap_client.py`

**Purpose**: Handle all communication with OpenChargeMap API

**Key Functions**:

```python
def get_chargers_along_route(
    origin_coords: tuple[float, float],
    destination_coords: tuple[float, float],
    min_power_kw: int = 50,
    max_results: int = 10,
    distance_km: int = 50
) -> list[dict]:
    """
    Query OpenChargeMap for charging stations along a route
    
    Args:
        origin_coords: (latitude, longitude) of starting point
        destination_coords: (latitude, longitude) of destination
        min_power_kw: Minimum power rating filter
        max_results: Maximum number of results to return
        distance_km: Search radius from route in kilometers
    
    Returns:
        List of charging station dictionaries
    """
```

```python
def parse_openchargemap_response(api_response: dict) -> list[dict]:
    """
    Parse OpenChargeMap API response into internal format
    
    Args:
        api_response: Raw JSON response from OpenChargeMap
    
    Returns:
        List of standardized charging station dictionaries
    """
```

```python
def map_operator_to_network(operator_name: str) -> str:
    """
    Map OpenChargeMap operator names to known networks
    
    Args:
        operator_name: Operator name from OpenChargeMap
    
    Returns:
        Standardized network name (EVgo, ChargePoint, etc.) or original name
    """
```

### Updated Charging Tools

**File**: `ev-concierge/tools/charging_tools.py`

**Changes**:
- Import `openchargemap_client`
- Update `search_chargers()` to call real API when `USE_MOCK_DATA=false`
- Add location name to coordinate conversion
- Keep `reserve_charging_slot()`, `check_charger_status()`, and `cancel_reservation()` as mock functions
- When reserving, use the real station data (ID, network, location) but mock the reservation process
- Maintain backward compatibility with existing interface

### Configuration Updates

**File**: `ev-concierge/utils/config.py`

**New Configuration**:
```python
OPENCHARGEMAP_API_KEY = os.getenv('OPENCHARGEMAP_API_KEY', '')
OPENCHARGEMAP_BASE_URL = 'https://api.openchargemap.io/v3'
```

### Location Coordinates Module

**File**: `ev-concierge/utils/location_coords.py`

**Purpose**: Map city names to coordinates for API queries

**Key Data**:
```python
CITY_COORDINATES = {
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Francisco, CA": (37.7749, -122.4194),
    "San Diego, CA": (32.7157, -117.1611),
    "Seattle, WA": (47.6062, -122.3321),
    "Las Vegas, NV": (36.1699, -115.1398),
}
```

## Data Models

### OpenChargeMap API Response Structure

Based on OpenChargeMap API documentation, the response contains:

```json
{
  "ID": 12345,
  "UUID": "abc-123",
  "AddressInfo": {
    "Title": "Station Name",
    "AddressLine1": "123 Main St",
    "Town": "City",
    "StateOrProvince": "CA",
    "Postcode": "90210",
    "Country": {"Title": "United States"},
    "Latitude": 34.0522,
    "Longitude": -118.2437
  },
  "OperatorInfo": {
    "Title": "EVgo Network",
    "ID": 25
  },
  "Connections": [
    {
      "PowerKW": 350,
      "ConnectionType": {"Title": "CCS"},
      "Level": {"Title": "Level 3"}
    }
  ],
  "StatusType": {
    "IsOperational": true,
    "Title": "Operational"
  },
  "UsageCost": "$0.43/kWh"
}
```

### Internal Charging Station Format

Our standardized format (matching current mock data):

```python
{
    "id": str,              # OpenChargeMap ID
    "network": str,         # Mapped network name
    "location": str,        # City, State
    "address": str,         # Full street address
    "latitude": float,      # Geographic coordinate
    "longitude": float,     # Geographic coordinate
    "power_kw": int,        # Maximum power rating
    "price_per_kwh": float, # Price (from API or estimated)
    "available": bool,      # Operational status
    "slots": list[str],     # Time slots (mock for now)
    "amenities": list[str]  # Nearby amenities (future enhancement)
}
```

### Network Mapping Dictionary

```python
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
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Acceptance Criteria Testing Prework

1.1 WHEN the system searches for chargers along a route, THE EV Concierge SHALL query the OpenChargeMap API with the route coordinates
Thoughts: This is about the system behavior for all route searches. We can test that when USE_MOCK_DATA is false and we have valid coordinates, an API call is made with the correct parameters.
Testable: yes - property

1.2 WHEN the OpenChargeMap API returns charging station data, THE EV Concierge SHALL parse and store the station information including location, network, and power rating
Thoughts: This is about parsing behavior across all API responses. We can generate various API response structures and verify all required fields are extracted.
Testable: yes - property

1.3 WHEN displaying charging stations, THE EV Concierge SHALL show stations that are located within a reasonable distance of the route
Thoughts: This is about filtering logic that should apply to all station lists. We can test that all returned stations fall within the specified distance threshold.
Testable: yes - property

1.4 WHEN the API request fails, THE EV Concierge SHALL handle the error gracefully and inform the user
Thoughts: This is about error handling behavior. We can simulate various API failures and verify graceful handling.
Testable: yes - example

1.5 WHEN the API key is missing or invalid, THE EV Concierge SHALL provide a clear error message to the user
Thoughts: This is a specific error case. We can test with missing and invalid keys.
Testable: yes - example

2.1 WHEN the system receives charging station data from OpenChargeMap, THE EV Concierge SHALL extract the operator name from the response
Thoughts: This is about extraction logic across all responses. We can test that operator names are always extracted when present.
Testable: yes - property

2.2 WHEN the operator name matches a known network, THE EV Concierge SHALL map it to the standardized network name
Thoughts: This is about mapping logic for all known networks. We can test that all entries in our mapping dictionary are correctly transformed.
Testable: yes - property

2.3 WHEN the operator name does not match a known network, THE EV Concierge SHALL display the original operator name
Thoughts: This is about fallback behavior for unknown operators. We can test with various unknown operator names.
Testable: yes - property

2.4 WHEN displaying charging stations, THE EV Concierge SHALL include the network name for each station
Thoughts: This is about output format for all stations. We can verify every station dict contains a network field.
Testable: yes - property

2.5 WHEN multiple charging networks are available, THE EV Concierge SHALL organize results by network for easy comparison
Thoughts: This is about organization logic. However, looking at the current implementation, results are returned as a flat list. This might be a UI concern rather than a data processing requirement.
Testable: no

3.1 WHEN the system receives charging station data, THE EV Concierge SHALL extract the maximum power rating in kilowatts
Thoughts: This is about extraction across all station data. We can test that power ratings are extracted from the Connections array.
Testable: yes - property

3.2 WHEN a station has multiple connectors with different power ratings, THE EV Concierge SHALL display the highest available power rating
Thoughts: This is about max-finding logic across all multi-connector stations. We can test with various connector configurations.
Testable: yes - property

3.3 WHEN power rating information is not available, THE EV Concierge SHALL indicate that the power rating is unknown
Thoughts: This is about handling missing data. We can test with responses lacking power info.
Testable: yes - example

3.4 WHEN displaying charging stations, THE EV Concierge SHALL show the power rating in kilowatts for each station
Thoughts: This is about output format. We can verify every station dict contains a power_kw field.
Testable: yes - property

3.5 WHEN filtering stations by minimum power, THE EV Concierge SHALL only return stations that meet or exceed the specified power threshold
Thoughts: This is about filtering logic for all power thresholds. We can test with various min_power_kw values.
Testable: yes - property

4.1 WHEN the system receives charging station data, THE EV Concierge SHALL extract the complete address including street, city, and state
Thoughts: This is about address extraction across all responses. We can test that address components are properly extracted and formatted.
Testable: yes - property

4.2 WHEN the system receives charging station data, THE EV Concierge SHALL extract the geographic coordinates (latitude and longitude)
Thoughts: This is about coordinate extraction for all stations. We can verify lat/lon are extracted from AddressInfo.
Testable: yes - property

4.3 WHEN displaying charging stations, THE EV Concierge SHALL show the formatted address for each station
Thoughts: This is about output format. We can verify every station has an address field.
Testable: yes - property

4.4 WHEN address information is incomplete, THE EV Concierge SHALL display the available address components
Thoughts: This is about handling partial data. We can test with various incomplete address structures.
Testable: yes - example

4.5 WHEN the user requests station details, THE EV Concierge SHALL provide the geographic coordinates for navigation purposes
Thoughts: This is about including coordinates in output. We can verify latitude and longitude fields are present.
Testable: yes - property

5.1 WHEN the application starts, THE EV Concierge SHALL read the OpenChargeMap API key from the OPENCHARGEMAP_API_KEY environment variable
Thoughts: This is about configuration loading at startup. This is a specific initialization behavior.
Testable: yes - example

5.2 WHEN the API key is not found in the environment, THE EV Concierge SHALL log a warning and fall back to mock data mode
Thoughts: This is about fallback behavior for missing config. This is a specific error case.
Testable: yes - example

5.3 WHEN making API requests, THE EV Concierge SHALL include the API key in the request headers as specified by OpenChargeMap documentation
Thoughts: This is about request formatting for all API calls. We can verify the key is in the correct header.
Testable: yes - property

5.4 WHEN the USE_MOCK_DATA flag is set to false, THE EV Concierge SHALL use the real OpenChargeMap API instead of mock data
Thoughts: This is about mode switching. We can test that the correct code path is taken based on the flag.
Testable: yes - example

5.5 WHEN the USE_MOCK_DATA flag is set to true, THE EV Concierge SHALL continue using mock data regardless of API key availability
Thoughts: This is about mock mode behavior. We can verify mock data is returned when flag is true.
Testable: yes - example

6.1 WHEN the user provides origin and destination locations, THE EV Concierge SHALL calculate the route path between them
Thoughts: This is about route calculation for all location pairs. However, we're using a simple bounding box approach rather than actual route calculation.
Testable: no

6.2 WHEN searching for charging stations, THE EV Concierge SHALL query OpenChargeMap for stations within a specified distance of the route path
Thoughts: This is about query construction for all searches. We can verify the bounding box parameters are correctly calculated.
Testable: yes - property

6.3 WHEN the route is very long, THE EV Concierge SHALL query multiple segments of the route to ensure comprehensive coverage
Thoughts: This is about handling long routes. This is a future enhancement not in the initial implementation.
Testable: no

6.4 WHEN displaying results, THE EV Concierge SHALL order charging stations by their position along the route from origin to destination
Thoughts: This is about sorting logic. We can test that stations are ordered by distance from origin.
Testable: yes - property

6.5 WHEN no charging stations are found along the route, THE EV Concierge SHALL inform the user and suggest expanding the search radius
Thoughts: This is about handling empty results. This is a specific case.
Testable: yes - example

### Property Reflection

After reviewing all testable properties, I've identified the following consolidations:

- Properties 2.4, 3.4, 4.3, and 4.5 all test that output contains required fields. These can be combined into a single comprehensive property about output format completeness.
- Properties 1.2 and 2.1 both test extraction from API responses and can be combined.
- Properties 3.1 and 3.2 can be combined into a single property about power rating extraction and max-finding.

### Correctness Properties

Property 1: API query construction
*For any* valid origin and destination coordinates with USE_MOCK_DATA=false, the system should construct an OpenChargeMap API request with correct bounding box parameters and minimum power filter
**Validates: Requirements 1.1, 6.2**

Property 2: Complete data extraction
*For any* valid OpenChargeMap API response, the system should extract all required fields: operator name, location, address, coordinates, and power rating
**Validates: Requirements 1.2, 2.1, 3.1, 4.1, 4.2**

Property 3: Route-based filtering
*For any* list of charging stations and route coordinates, all returned stations should be within the specified distance threshold from the route
**Validates: Requirements 1.3**

Property 4: Network name mapping
*For any* operator name in the network mapping dictionary, the system should return the corresponding standardized network name
**Validates: Requirements 2.2**

Property 5: Unknown network passthrough
*For any* operator name not in the network mapping dictionary, the system should return the original operator name unchanged
**Validates: Requirements 2.3**

Property 6: Maximum power selection
*For any* charging station with multiple connectors, the system should return the highest power rating among all connectors
**Validates: Requirements 3.2**

Property 7: Power filtering
*For any* minimum power threshold and list of stations, all returned stations should have power ratings greater than or equal to the threshold
**Validates: Requirements 3.5**

Property 8: Complete output format
*For any* processed charging station, the output dictionary should contain all required fields: id, network, location, address, latitude, longitude, power_kw, and available status
**Validates: Requirements 2.4, 3.4, 4.3, 4.5**

Property 9: API key header inclusion
*For any* API request when USE_MOCK_DATA=false, the request headers should include the API key in the format specified by OpenChargeMap
**Validates: Requirements 5.3**

Property 10: Distance-based ordering
*For any* list of charging stations along a route, stations should be ordered by increasing distance from the origin
**Validates: Requirements 6.4**

## Error Handling

### API Errors
- **Network failures**: Catch connection errors, log warning, fall back to mock data
- **Invalid API key**: Return clear error message to user
- **Rate limiting**: Implement exponential backoff, respect API limits
- **Malformed responses**: Validate JSON structure, skip invalid entries

### Data Validation
- **Missing coordinates**: Skip stations without valid lat/lon
- **Invalid power ratings**: Default to 0 or "Unknown"
- **Missing operator**: Use "Unknown Network"
- **Incomplete addresses**: Format with available components

### Configuration Errors
- **Missing API key**: Log warning, use mock data mode
- **Invalid coordinates**: Return error message for invalid city names
- **Empty results**: Inform user, suggest expanding search radius

## Testing Strategy

### Unit Tests
- Test coordinate lookup for all cities in dropdown
- Test network name mapping for known operators
- Test API response parsing with sample data
- Test error handling for various failure modes
- Test power rating extraction from multi-connector stations
- Test address formatting with complete and incomplete data

### Property-Based Tests
We will use the `hypothesis` library for Python property-based testing. Each test should run a minimum of 100 iterations.

**Test Configuration**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
```

**Property Tests**:
1. Network mapping consistency (Property 4, 5)
2. Power rating max-finding (Property 6)
3. Power filtering correctness (Property 7)
4. Output format completeness (Property 8)
5. Distance-based ordering (Property 10)
6. Data extraction completeness (Property 2)

Each property-based test must include a comment tag:
```python
# Feature: openchargemap-integration, Property 4: Network name mapping
```

### Integration Tests
- Test end-to-end flow with real API (using test API key)
- Test fallback to mock data when API unavailable
- Test UI display of real charging station data
- Verify coordinate updates in test scenarios work correctly

### Manual Testing
- Verify map display shows correct station locations (future enhancement)
- Test with various origin/destination combinations
- Verify network logos/branding display correctly (future enhancement)
- Test with different minimum power filters

## Implementation Notes

### Scope Clarification

**Real API Integration**:
- `search_chargers()`: Use real OpenChargeMap API to find stations
- Display real station data: network names, locations, addresses, power ratings
- Show actual charging networks: EVgo, ChargePoint, Electrify America, Tesla, etc.

**Mock Functionality** (unchanged):
- `reserve_charging_slot()`: Mock reservation process
- `check_charger_status()`: Mock real-time status
- `cancel_reservation()`: Mock cancellation
- Pricing information: Use estimated/mock prices
- Time slots: Use mock availability slots

**Hybrid Approach**:
When a station is selected for reservation, the mock reservation will include the real station details (ID, network, location) from OpenChargeMap, so the UI shows "Reserved at EVgo - Tejon Ranch, CA" with actual data.

### OpenChargeMap API Details

**Base URL**: `https://api.openchargemap.io/v3`

**Endpoint**: `/poi/`

**Query Parameters**:
- `key`: API key (required)
- `latitude`: Center latitude
- `longitude`: Center longitude
- `distance`: Search radius in km
- `distanceunit`: "KM" or "Miles"
- `maxresults`: Maximum number of results (default 100)
- `minpowerkw`: Minimum power rating filter
- `compact`: true (for smaller response)
- `verbose`: false (for smaller response)

**Example Request**:
```
GET https://api.openchargemap.io/v3/poi/?key=YOUR_KEY&latitude=34.0522&longitude=-118.2437&distance=50&distanceunit=KM&maxresults=10&minpowerkw=50&compact=true&verbose=false
```

### Route-Based Search Strategy

Since we're searching along a route, we'll use a bounding box approach:
1. Calculate midpoint between origin and destination
2. Calculate distance between origin and destination
3. Use midpoint as search center
4. Use half the route distance + buffer as search radius
5. Filter results to only include stations reasonably close to the route line

### Coordinate Updates for Test Data

Update `test_scenarios.py` with accurate coordinates:
```python
CITY_COORDINATES = {
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Francisco, CA": (37.7749, -122.4194),
    "San Diego, CA": (32.7157, -117.1611),
    "Seattle, WA": (47.6062, -122.3321),
    "Las Vegas, NV": (36.1699, -115.1398),
}
```

### Future Enhancements

1. **Map Visualization**: Display charging stations on an interactive map
2. **Real-time Availability**: Query station status APIs for live availability
3. **Pricing Integration**: Fetch real-time pricing from network APIs
4. **Amenities Integration**: Cross-reference with Google Places API for nearby restaurants
5. **Route Optimization**: Use actual route geometry instead of bounding box
6. **Multi-segment Queries**: For very long routes, query multiple segments
7. **Caching**: Cache API responses to reduce API calls and improve performance
8. **User Reviews**: Display OpenChargeMap user ratings and comments
