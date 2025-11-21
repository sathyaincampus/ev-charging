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
            print("\n⏭️  Amenities: Auto-order disabled by user")
            return {"order": None, "message": "Auto-order disabled", "tool_results": []}
        
        favorite_drink = user_prefs.get('favorite_drink', 'Coffee')
        favorite_food = user_prefs.get('favorite_food', '')
        
        # Check if both are set to None
        if (not favorite_drink or favorite_drink == 'None') and (not favorite_food or favorite_food == 'None'):
            print("\n⏭️  Amenities: No food or drink preferences set (both are 'None')")
            return {"order": None, "message": "No food or drink preferences", "tool_results": []}
        
        return asyncio.run(self.order_amenities_async(location, user_prefs, charging_duration_min))
    
    async def order_amenities_async(self, location: str, user_prefs: dict, charging_duration_min: int) -> dict:
        print(f"🍽️  Amenities Agent: Starting async order_amenities...")
        print(f"   Location: {location}")
        print(f"   Duration: {charging_duration_min} min")
        
        # Extract preferences
        favorite_drink = user_prefs.get('favorite_drink', 'None')
        favorite_food = user_prefs.get('favorite_food', 'None')
        
        system_prompt = """You are an amenities specialist. Check what's available and 
pre-order based on user preferences and charging duration. ONLY order items that the user 
has specified in their preferences. If they don't want drinks or food, don't order them.

NOTE: The amenities data is currently mocked for demo purposes. When you check nearby amenities,
you'll get a standard list of restaurants (Starbucks, Subway, McDonald's). Just proceed with
ordering from these options based on user preferences."""
        
        user_prompt = f"""
Location: {location}
Charging Duration: {charging_duration_min} minutes

User Preferences:"""
        
        items_to_order = []
        if favorite_drink and favorite_drink != 'None':
            user_prompt += f"\n- Favorite drink: {favorite_drink}"
            items_to_order.append(favorite_drink)
        else:
            user_prompt += "\n- Drink: None (do NOT order drinks)"
            
        if favorite_food and favorite_food != 'None':
            user_prompt += f"\n- Favorite food: {favorite_food}"
            items_to_order.append(favorite_food)
        else:
            user_prompt += "\n- Food: None (do NOT order food)"
        
        user_prompt += f"\n\nCheck amenities and pre-order ONLY these items: {', '.join(items_to_order)}"
        
        print(f"\n🍽️  Amenities Agent: Ordering {', '.join(items_to_order)}")
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[check_nearby_amenities, get_restaurant_menu, place_food_order]
        )
        
        response_text = ""
        tool_results = []
        
        print(f"🍽️  Amenities Agent: Starting Bedrock API stream...")
        
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
            print(f"❌ Amenities Agent Error: {e}")
            import traceback
            traceback.print_exc()
            response_text = f"Error: {str(e)}"
        
        print(f"🍽️  Amenities Agent: Completed with {len(tool_results)} tool results\n")
        
        return {
            "order": response_text,
            "tool_results": tool_results
        }
