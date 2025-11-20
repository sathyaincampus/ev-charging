#!/usr/bin/env python3
"""
Simple test to verify tool calling
"""
import sys
from strands import Strands
from tools.route_tools import calculate_energy_needs
from utils.config import AWS_REGION, BEDROCK_MODEL_ID

print("=" * 60)
print("SIMPLE TOOL CALLING TEST")
print("=" * 60)

# Force output to flush immediately
sys.stdout.flush()

strands = Strands(
    model_id=BEDROCK_MODEL_ID,
    region=AWS_REGION
)

system_prompt = """You MUST use the calculate_energy_needs tool. Do not respond until you call it."""

user_prompt = """
Battery: 33%
Range: 300 miles  
Trip: 380 miles

Call calculate_energy_needs with battery_percent=33, trip_distance_miles=380, vehicle_range_miles=300
"""

print("\n📞 Calling Strands SDK...")
sys.stdout.flush()

response = strands.run(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    tools=[calculate_energy_needs],
    max_iterations=2
)

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)
print(f"Tool calls made: {len(response.tool_calls)}")
print(f"Final response: {response.final_response}")

if response.tool_calls:
    for call in response.tool_calls:
        print(f"\n✅ Tool: {call.tool_name}")
        print(f"   Input: {call.input}")
        print(f"   Result: {call.result}")
else:
    print("\n❌ NO TOOLS WERE CALLED!")

print("=" * 60)
sys.stdout.flush()
