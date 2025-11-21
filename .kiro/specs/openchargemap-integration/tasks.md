# Implementation Plan

- [x] 1. Create location coordinates module
  - Create `ev-concierge/utils/location_coords.py` with city coordinate mappings
  - Add coordinates for all cities in UI dropdown: LA, SF, San Diego, Seattle, Las Vegas
  - _Requirements: 6.1_

- [x] 2. Create OpenChargeMap API client
  - Create `ev-concierge/utils/openchargemap_client.py`
  - Implement `get_chargers_along_route()` function to query API with bounding box
  - Implement `parse_openchargemap_response()` to extract station data
  - Implement `map_operator_to_network()` for network name mapping
  - Add network mapping dictionary for EVgo, ChargePoint, Electrify America, Tesla, etc.
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 4.1, 4.2_

- [x] 3. Update configuration
  - Update `ev-concierge/utils/config.py` to load OPENCHARGEMAP_API_KEY
  - Add OPENCHARGEMAP_BASE_URL constant
  - _Requirements: 5.1, 5.2_

- [x] 4. Update charging tools to use real API
  - Update `ev-concierge/tools/charging_tools.py`
  - Modify `search_chargers()` to call OpenChargeMap API when USE_MOCK_DATA=false
  - Convert location names to coordinates using location_coords module
  - Keep reservation functions mocked but include real station details
  - _Requirements: 1.1, 1.3, 1.4, 5.3, 5.4, 6.2_

- [x] 5. Update test scenarios with real coordinates
  - Update `ev-concierge/test_scenarios.py` to include coordinate data
  - Ensure all test scenarios have accurate lat/lon for cities
  - _Requirements: 6.1_

- [x] 6. Set USE_MOCK_DATA to false and test
  - Update `ev-concierge/.env` to set USE_MOCK_DATA=false
  - Run the application and verify real charging stations appear
  - Test with different origin/destination combinations
  - Verify network names are correctly mapped
  - _Requirements: 5.4, 5.5_
