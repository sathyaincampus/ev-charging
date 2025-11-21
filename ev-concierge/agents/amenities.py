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
        # Check if auto-order is disabled
        if not user_prefs.get('auto_order_coffee'):
            print("\n⏭️  Amenities: Auto-order disabled by user")
            return {"order": None, "message": "Auto-order disabled", "tool_results": []}
        
        favorite_drink = user_prefs.get('favorite_drink', 'Coffee')
        favorite_food = user_prefs.get('favorite_food', '')
        
        # Check if both are set to None
        if (not favorite_drink or favorite_drink == 'None') and (not favorite_food or favorite_food == 'None'):
            print("\n⏭️  Amenities: No food or drink preferences set (both are 'None')")
            return {"order": None, "message": "No food or drink preferences", "tool_results": []}
        
        system_prompt = """You are an amenities specialist. Check what's available and 
pre-order based on user preferences and charging duration. ONLY order items that the user 
has specified in their preferences. If they don't want drinks or food, don't order them."""
        
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
