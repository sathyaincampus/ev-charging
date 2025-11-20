from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID
from tools.amenities_tools import check_nearby_amenities, get_restaurant_menu, place_food_order

class AmenitiesAgent:
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def order_amenities(self, location: str, user_prefs: dict, charging_duration_min: int) -> dict:
        if not user_prefs.get('auto_order_coffee'):
            return {"order": None, "message": "Auto-order disabled"}
        
        system_prompt = """You are an amenities specialist. Check what's available and 
pre-order based on user preferences and charging duration."""
        
        favorite_drink = user_prefs.get('favorite_drink', 'Coffee')
        favorite_food = user_prefs.get('favorite_food', '')
        
        user_prompt = f"""
Location: {location}
Charging Duration: {charging_duration_min} minutes
User Preferences:"""
        
        if favorite_drink and favorite_drink != 'None':
            user_prompt += f" Favorite drink: {favorite_drink}"
        if favorite_food and favorite_food != 'None':
            user_prompt += f", Favorite food: {favorite_food}"
        
        user_prompt += "\n\nCheck amenities and pre-order appropriate items."
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=[check_nearby_amenities, get_restaurant_menu, place_food_order],
            max_iterations=4
        )
        
        return {
            "order": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
