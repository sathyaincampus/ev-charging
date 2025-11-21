from utils.config import AWS_REGION, BEDROCK_MODEL_ID, USE_MOCK_DATA
from agents.trip_planning import TripPlanningAgent
from agents.charging_negotiation import ChargingNegotiationAgent
from agents.amenities import AmenitiesAgent
from agents.payment import PaymentAgent
from agents.monitoring import MonitoringAgent

class CoordinatorAgent:
    def __init__(self):
        self.use_mock = USE_MOCK_DATA
        self.trip_agent = TripPlanningAgent()
        self.charging_agent = ChargingNegotiationAgent()
        self.amenities_agent = AmenitiesAgent()
        self.payment_agent = PaymentAgent()
        self.monitoring_agent = MonitoringAgent()
        
        # Coordinator doesn't need its own agent - it orchestrates other agents
    
    def orchestrate(self, vehicle_data: dict, trip_data: dict, user_prefs: dict) -> dict:
        results = {}
        
        # Step 1: Trip Planning
        trip_plan = self.trip_agent.analyze(vehicle_data, trip_data)
        results['trip_plan'] = trip_plan
        
        # Check if charging needed by parsing actual tool results
        needs_charging = False
        energy_result = None
        
        for tool_result in trip_plan.get('tool_results', []):
            if isinstance(tool_result, dict):
                # Check if this is the energy calculation result
                if 'needs_charging' in tool_result:
                    needs_charging = tool_result.get('needs_charging', False)
                    energy_result = tool_result
                    break
        
        if not needs_charging:
            battery_pct = vehicle_data.get('battery_percent', 0)
            range_mi = vehicle_data.get('range_miles', 0)
            return {
                "summary": f"✅ No charging needed! Your {battery_pct}% battery ({range_mi} mi range) is sufficient for this trip.",
                "results": results,
                "energy_analysis": energy_result
            }
        
        # Step 2: Charging Negotiation
        charging_result = self.charging_agent.find_and_reserve(trip_plan, user_prefs)
        results['charging'] = charging_result
        
        # Extract charger location and duration
        charger_location = "charging location"
        charging_duration = 30
        for r in charging_result.get('tool_results', []):
            if isinstance(r, dict):
                if 'location' in r:
                    charger_location = r['location']
                if 'duration_min' in r:
                    charging_duration = r['duration_min']
        
        # Step 3: Amenities
        amenities_result = self.amenities_agent.order_amenities(
            charger_location, user_prefs, charging_duration
        )
        results['amenities'] = amenities_result
        
        # Step 4: Payment
        transactions = []
        for r in amenities_result.get('tool_results', []):
            if isinstance(r, dict) and 'total_usd' in r:
                transactions.append({
                    "amount": r['total_usd'],
                    "merchant": r.get('restaurant', 'Food vendor'),
                    "description": f"Pre-order: {', '.join(r.get('items', []))}"
                })
        
        payment_result = self.payment_agent.process_payments(
            transactions, user_prefs.get('wallet_id', 'default')
        )
        results['payments'] = payment_result
        
        # Step 5: Generate Summary
        summary = self._generate_summary(results)
        
        return {
            "summary": summary,
            "results": results
        }
    
    def _generate_summary(self, results: dict) -> str:
        """Generate a comprehensive summary of the trip plan"""
        
        summary_parts = []
        
        # Trip analysis
        trip_analysis = results.get('trip_plan', {}).get('analysis', '')
        if trip_analysis:
            summary_parts.append(f"**Trip Analysis:**\n{trip_analysis}")
        
        # Charging details
        charging_tools = results.get('charging', {}).get('tool_results', [])
        if charging_tools:
            summary_parts.append("\n**⚡ Charging Plan:**")
            
            # First, collect charger info from search results
            chargers_map = {}
            for tool_result in charging_tools:
                if isinstance(tool_result, list):
                    # This is from search_chargers
                    for charger in tool_result:
                        if isinstance(charger, dict) and 'id' in charger:
                            chargers_map[charger['id']] = charger
            
            # Then, show reservations with charger details
            for tool_result in charging_tools:
                if isinstance(tool_result, dict):
                    if 'reservation_id' in tool_result:
                        charger_id = tool_result.get('charger_id', 'Unknown')
                        time_slot = tool_result.get('time_slot', 'TBD')
                        duration = tool_result.get('duration_min', 30)
                        
                        # Try to get charger details from search results first
                        charger_info = chargers_map.get(charger_id, {})
                        
                        # If not in map, use data from reservation (agent should pass it)
                        location = tool_result.get('location') or charger_info.get('location', charger_id)
                        network = tool_result.get('network') or charger_info.get('network', 'Charger')
                        power_kw = charger_info.get('power_kw', 'N/A')
                        
                        summary_parts.append(f"- **{network}** at {location}")
                        if power_kw != 'N/A':
                            summary_parts.append(f"  Power: {power_kw} kW")
                        summary_parts.append(f"  Time: {time_slot}, Duration: {duration} min")
                        summary_parts.append(f"  Confirmation: `{tool_result['reservation_id']}`")
        
        # Amenities
        amenities_tools = results.get('amenities', {}).get('tool_results', [])
        if amenities_tools:
            summary_parts.append("\n**🍽️ Amenities:**")
            for tool_result in amenities_tools:
                if isinstance(tool_result, dict):
                    if 'order_id' in tool_result:
                        restaurant = tool_result.get('restaurant', 'Restaurant')
                        items = tool_result.get('items', [])
                        total = tool_result.get('total_usd', 0)
                        pickup_time = tool_result.get('pickup_time', 'TBD')
                        summary_parts.append(f"- Pre-ordered from {restaurant}")
                        summary_parts.append(f"  Items: {', '.join(items)}")
                        summary_parts.append(f"  Total: ${total:.2f}")
                        summary_parts.append(f"  Pickup: {pickup_time}")
                        summary_parts.append(f"  Order: `{tool_result['order_id']}`")
        
        # Payments
        payment_tools = results.get('payments', {}).get('tool_results', [])
        if payment_tools:
            total_paid = 0
            summary_parts.append("\n**💳 Payments:**")
            for tool_result in payment_tools:
                if isinstance(tool_result, dict) and 'transaction_id' in tool_result:
                    amount = tool_result.get('amount', 0)
                    merchant = tool_result.get('merchant', 'Merchant')
                    total_paid += amount
                    summary_parts.append(f"- ${amount:.2f} to {merchant}")
            
            if total_paid > 0:
                summary_parts.append(f"\n**Total Charged: ${total_paid:.2f}**")
        
        # Combine all parts
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "✅ Trip planned successfully!"
