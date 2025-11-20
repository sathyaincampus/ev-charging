from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.route_tools import calculate_energy_needs, get_route_info

class TripPlanningAgent:
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def analyze(self, vehicle_data: dict, trip_data: dict) -> dict:
        system_prompt = """You are a trip planning specialist for EVs.

You have access to tools that you MUST use. Never make calculations yourself.

CRITICAL: You MUST call the calculate_energy_needs tool first before providing any analysis.
Do NOT respond with text until you have called the tool and received the results."""
        
        user_prompt = f"""
Vehicle Information:
- Model: {vehicle_data['model']}
- Current Battery: {vehicle_data['battery_percent']}%
- Vehicle Range: {vehicle_data['range_miles']} miles

Trip Information:
- From: {trip_data['origin']}
- To: {trip_data['destination']}
- Distance: {trip_data['distance_miles']} miles
- Departure: {trip_data['departure']}

Use the calculate_energy_needs tool to analyze if charging is needed for this trip.
Call it with: battery_percent={vehicle_data['battery_percent']}, trip_distance_miles={trip_data['distance_miles']}, vehicle_range_miles={vehicle_data['range_miles']}"""
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[calculate_energy_needs, get_route_info],
            max_iterations=3
        )
        
        # Debug: Print tool calls
        print(f"\n🔍 DEBUG - Trip Planning Agent:")
        print(f"   Tool calls made: {len(response.tool_calls)}")
        if response.tool_calls:
            for call in response.tool_calls:
                print(f"   - {call.tool_name}: {call.result}")
        else:
            print(f"   ⚠️  No tools were called!")
        
        return {
            "analysis": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
