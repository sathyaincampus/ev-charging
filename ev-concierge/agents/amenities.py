from strands.models import BedrockModel
from strands import Agent
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.amenities_tools import check_nearby_amenities, get_restaurant_menu, place_food_order
import json
import asyncio

class AmenitiesAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def order_amenities(self, location: str, user_prefs: dict, charging_duration_min: int) -> dict:
        """Synchronous wrapper for async order_amenities"""
        if not user_prefs.get('auto_order_coffee'):
            return {"order": None, "message": "Auto-order disabled"}
        
        return asyncio.run(self.order_amenities_async(location, user_prefs, charging_duration_min))
    
    async def order_amenities_async(self, location: str, user_prefs: dict, charging_duration_min: int) -> dict:
        system_prompt = """You are an amenities specialist. Check what's available and 
pre-order based on user preferences and charging duration.

NOTE: The amenities data is currently mocked for demo purposes. When you check nearby amenities,
you'll get a standard list of restaurants (Starbucks, Subway, McDonald's). Just proceed with
ordering from these options based on user preferences."""
        
        user_prompt = f"""
Location: {location}
Charging Duration: {charging_duration_min} minutes
User Preferences: Favorite drink: {user_prefs.get('favorite_drink', 'Coffee')}

Check nearby amenities and pre-order the user's favorite drink and any snacks that would be ready 
within the charging duration."""
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[check_nearby_amenities, get_restaurant_menu, place_food_order]
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
            "order": response_text,
            "tool_results": tool_results
        }
