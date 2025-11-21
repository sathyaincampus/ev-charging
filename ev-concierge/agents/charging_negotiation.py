from strands.models import BedrockModel
from strands import Agent
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.charging_tools import search_chargers, reserve_charging_slot, check_charger_status
import json
import asyncio

class ChargingNegotiationAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def find_and_reserve(self, trip_plan: dict, preferences: dict = None) -> dict:
        """Synchronous wrapper for async find_and_reserve"""
        return asyncio.run(self.find_and_reserve_async(trip_plan, preferences))
    
    async def find_and_reserve_async(self, trip_plan: dict, preferences: dict = None) -> dict:
        system_prompt = """You are a charging negotiation specialist. Find the best charger 
based on price, speed, location, and availability. Reserve the optimal slot.

IMPORTANT: When calling reserve_charging_slot, you MUST include:
- charger_id: from the search results
- time_slot: pick from available slots
- location: the location field from the charger
- network: the network field from the charger (e.g., "Tesla Supercharger", "EVgo")

Example: reserve_charging_slot(charger_id="OCM-12345", time_slot="10:00", location="Kettleman City, CA", network="Tesla Supercharger")"""
        
        user_prompt = f"""
Trip Plan: {trip_plan}
User Preferences: {preferences or 'Prioritize speed and convenience'}

Find and reserve the best charging option. Make sure to pass the network and location when reserving."""
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[search_chargers, reserve_charging_slot, check_charger_status]
        )
        
        response_text = ""
        tool_results = []
        
        try:
            async for event in agent.stream_async(user_prompt):
                if isinstance(event, dict):
                    if 'data' in event:
                        response_text += str(event['data'])
                    
                    # Extract tool results from message
                    if 'message' in event:
                        message = event['message']
                        if isinstance(message, dict) and 'content' in message:
                            for content_block in message['content']:
                                if isinstance(content_block, dict) and 'toolResult' in content_block:
                                    tool_result = content_block['toolResult']
                                    if 'content' in tool_result:
                                        for content_item in tool_result['content']:
                                            if 'text' in content_item:
                                                try:
                                                    result_json = json.loads(content_item['text'])
                                                    tool_results.append(result_json)
                                                except:
                                                    pass
        except Exception as e:
            response_text = f"Error: {str(e)}"
        
        return {
            "reservation": response_text,
            "tool_results": tool_results
        }
