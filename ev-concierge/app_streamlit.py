import streamlit as st
import json
from datetime import datetime, timedelta
from agents.coordinator import CoordinatorAgent
import time

st.set_page_config(page_title="EV Concierge", page_icon="🚗", layout="wide")

# Initialize
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = CoordinatorAgent()
    st.session_state.vehicle = {"model": "Tesla Model Y", "battery_percent": 45, "range_miles": 300}
    st.session_state.preferences = {"auto_order_coffee": True, "restaurant": "Starbucks", "favorite_drink": "Large Latte", "favorite_food": "Breakfast Sandwich", "wallet_id": "WALLET-12345"}
    st.session_state.agent_status = {}
    st.session_state.trip_active = False
    st.session_state.notifications = []
    
    # Initialize wallet balances (tracked in session)
    st.session_state.wallet_balances = {
        "WALLET-12345": 1250.00,
        "WALLET-67890": 2500.00,
        "WALLET-11111": 150.00,
        "WALLET-22222": 5000.00,
        "WALLET-33333": 500.00
    }

# Header
st.markdown("# 🚗 Proactive EV Concierge")
st.markdown("### Multi-Agent AI System for Autonomous Charging Management")

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🗺️ Trip Planning")
    
    # Trip Input
    with st.form("trip_form"):
        origin = st.selectbox("Starting From", ["Los Angeles, CA", "San Francisco, CA", "San Diego, CA", "Seattle, WA", "Las Vegas, NV"])
        destination = st.selectbox("Destination", ["Los Angeles, CA", "San Francisco, CA", "San Diego, CA", "Seattle, WA", "Las Vegas, NV"])
        departure = st.selectbox("Departure", ["Tomorrow Morning", "Tonight", "Next Week"])
        
        col_a, col_b = st.columns(2)
        with col_a:
            current_battery = st.slider("Current Battery %", 0, 100, st.session_state.vehicle['battery_percent'])
        with col_b:
            priority = st.selectbox("Priority", ["Fastest Route", "Cheapest Charging", "Most Amenities"])
        
        submitted = st.form_submit_button("🚀 Start Trip Planning", use_container_width=True)
    
    if submitted:
        st.session_state.trip_active = True
        st.session_state.notifications = []
        
        # Build trip data with distance matrix
        # Distance matrix (miles between cities)
        distance_matrix = {
            ("Los Angeles, CA", "San Francisco, CA"): 380,
            ("Los Angeles, CA", "San Diego, CA"): 120,
            ("Los Angeles, CA", "Seattle, WA"): 1150,
            ("Los Angeles, CA", "Las Vegas, NV"): 270,
            ("San Francisco, CA", "Los Angeles, CA"): 380,
            ("San Francisco, CA", "San Diego, CA"): 500,
            ("San Francisco, CA", "Seattle, WA"): 800,
            ("San Francisco, CA", "Las Vegas, NV"): 570,
            ("San Diego, CA", "Los Angeles, CA"): 120,
            ("San Diego, CA", "San Francisco, CA"): 500,
            ("San Diego, CA", "Seattle, WA"): 1250,
            ("San Diego, CA", "Las Vegas, NV"): 330,
            ("Seattle, WA", "Los Angeles, CA"): 1150,
            ("Seattle, WA", "San Francisco, CA"): 800,
            ("Seattle, WA", "San Diego, CA"): 1250,
            ("Seattle, WA", "Las Vegas, NV"): 1120,
            ("Las Vegas, NV", "Los Angeles, CA"): 270,
            ("Las Vegas, NV", "San Francisco, CA"): 570,
            ("Las Vegas, NV", "San Diego, CA"): 330,
            ("Las Vegas, NV", "Seattle, WA"): 1120,
        }
        
        # Get distance between origin and destination
        distance = distance_matrix.get((origin, destination), 0)
        
        if origin == destination:
            st.warning("⚠️ Origin and destination are the same!")
            distance = 0
        
        trip_data = {
            "origin": origin,
            "destination": destination,
            "distance_miles": distance,
            "departure": (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0).isoformat()
        }
        st.session_state.vehicle['battery_percent'] = current_battery
        
        # Agent Activity Panel
        st.markdown("---")
        st.markdown("### 🤖 Agent Activity (Live)")
        
        agent_container = st.container()
        with agent_container:
            status_cols = st.columns(6)
            agent_names = ["Coordinator", "Trip Planning", "Charging", "Amenities", "Payment", "Monitoring"]
            
            for idx, agent in enumerate(agent_names):
                with status_cols[idx]:
                    st.markdown(f"**{agent}**")
                    placeholder = st.empty()
                    placeholder.info("⏳ Waiting")
                    st.session_state.agent_status[agent] = placeholder
        
        # Simulate agent execution
        progress_bar = st.progress(0)
        result_placeholder = st.empty()
        
        try:
            # Step 1: Trip Planning
            st.session_state.agent_status["Trip Planning"].warning("🔄 Analyzing energy needs...")
            progress_bar.progress(0.2)
            time.sleep(0.2)
            
            # Run coordinator
            result = st.session_state.coordinator.orchestrate(
                st.session_state.vehicle,
                trip_data,
                st.session_state.preferences
            )
            
            st.session_state.agent_status["Trip Planning"].success("✅ Complete")
            progress_bar.progress(0.3)
            
            # Check if charging needed
            needs_charging = 'charging' in result.get('results', {})
            
            if needs_charging:
                # Step 2: Charging
                st.session_state.agent_status["Charging"].warning("🔄 Finding chargers...")
                progress_bar.progress(0.5)
                time.sleep(0.2)
                st.session_state.agent_status["Charging"].success("✅ Complete")
                
                # Step 3: Amenities
                st.session_state.agent_status["Amenities"].warning("🔄 Ordering food...")
                progress_bar.progress(0.7)
                time.sleep(0.2)
                st.session_state.agent_status["Amenities"].success("✅ Complete")
                
                # Step 4: Payment
                st.session_state.agent_status["Payment"].warning("🔄 Processing payment...")
                progress_bar.progress(0.9)
                time.sleep(0.2)
                st.session_state.agent_status["Payment"].success("✅ Complete")
                
                # Deduct payment from wallet balance
                if 'payments' in result.get('results', {}):
                    payment_result = result['results']['payments']
                    if 'tool_results' in payment_result:
                        for tool_result in payment_result['tool_results']:
                            if isinstance(tool_result, dict) and tool_result.get('success'):
                                # Check if it's a batch payment result
                                if 'successful' in tool_result:
                                    total_charged = tool_result.get('total_amount', 0)
                                    wallet_id = st.session_state.preferences.get('wallet_id', 'WALLET-12345')
                                    if wallet_id in st.session_state.wallet_balances:
                                        st.session_state.wallet_balances[wallet_id] -= total_charged
                                        st.session_state.wallet_balances[wallet_id] = round(st.session_state.wallet_balances[wallet_id], 2)
            else:
                # Mark unused agents as skipped
                st.session_state.agent_status["Charging"].info("⏭️ Skipped")
                st.session_state.agent_status["Amenities"].info("⏭️ Skipped")
                st.session_state.agent_status["Payment"].info("⏭️ Skipped")
            
            # Coordinator and Monitoring always run
            st.session_state.agent_status["Coordinator"].success("✅ Complete")
            st.session_state.agent_status["Monitoring"].success("✅ Complete")
            progress_bar.progress(1.0)
            
            # Display results with better formatting
            if needs_charging:
                result_placeholder.success(f"### ✅ Trip Planned Successfully\n\n{result['summary']}")
                
                # Show charging stations found
                if 'results' in result and 'charging' in result['results']:
                    charging_results = result['results']['charging']
                    tool_results = charging_results.get('tool_results', [])
                    
                    # Find the search results (list of stations)
                    for tool_result in tool_results:
                        if isinstance(tool_result, list) and len(tool_result) > 0:
                            st.markdown("---")
                            st.markdown("### 🔌 Charging Stations Found")
                            
                            # Display stations in a nice format
                            for i, station in enumerate(tool_result[:5], 1):
                                with st.expander(f"⚡ {station.get('network', 'Unknown')} - {station.get('location', 'Unknown')}", expanded=(i==1)):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown(f"**Address:** {station.get('address', 'N/A')}")
                                        st.markdown(f"**Power:** {station.get('power_kw', 0)} kW")
                                    with col_b:
                                        st.markdown(f"**Price:** ${station.get('price_per_kwh', 0)}/kWh")
                                        st.markdown(f"**Status:** {'🟢 Available' if station.get('available') else '🔴 Unavailable'}")
                                    
                                    if station.get('amenities'):
                                        st.markdown(f"**Amenities:** {', '.join(station['amenities'])}")
                            break
            else:
                result_placeholder.info(f"### ✅ Trip Planned\n\n{result['summary']}")
            
            # Add detailed notifications
            st.session_state.notifications.append({
                "time": datetime.now().strftime("%H:%M"),
                "message": f"Trip to {destination} planned",
                "type": "success"
            })
            
            # Parse and add specific notifications
            if 'results' in result:
                # Energy analysis
                if 'trip_plan' in result['results']:
                    trip_tools = result['results']['trip_plan'].get('tool_results', [])
                    for tool_result in trip_tools:
                        if isinstance(tool_result, dict) and 'needs_charging' in tool_result:
                            if tool_result['needs_charging']:
                                deficit = tool_result.get('deficit_percent', 0)
                                st.session_state.notifications.append({
                                    "time": datetime.now().strftime("%H:%M"),
                                    "message": f"⚡ Charging needed: {deficit}% deficit",
                                    "type": "warning"
                                })
                
                # Charging reservations
                if 'charging' in result['results']:
                    charging_tools = result['results']['charging'].get('tool_results', [])
                    for tool_result in charging_tools:
                        if isinstance(tool_result, dict) and 'reservation_id' in tool_result:
                            network = tool_result.get('network', 'Unknown')
                            location = tool_result.get('location', 'Unknown')
                            st.session_state.notifications.append({
                                "time": datetime.now().strftime("%H:%M"),
                                "message": f"🔌 Reserved {network} at {location}",
                                "type": "info"
                            })
                
                # Food orders
                if 'amenities' in result['results']:
                    amenities_tools = result['results']['amenities'].get('tool_results', [])
                    for tool_result in amenities_tools:
                        if isinstance(tool_result, dict) and 'order_id' in tool_result:
                            restaurant = tool_result.get('restaurant', 'Restaurant')
                            st.session_state.notifications.append({
                                "time": datetime.now().strftime("%H:%M"),
                                "message": f"🍽️ Pre-ordered from {restaurant}",
                                "type": "info"
                            })
            
        except Exception as e:
            result_placeholder.error(f"❌ Error: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            with st.expander("Error Details"):
                st.code(error_details)
            for agent in agent_names:
                if st.session_state.agent_status[agent]:
                    st.session_state.agent_status[agent].error("❌ Failed")

with col2:
    st.markdown("### ⚙️ Vehicle Status")
    
    # Vehicle Info Card
    with st.container():
        st.markdown(f"**Model:** {st.session_state.vehicle['model']}")
        st.metric("Battery Level", f"{st.session_state.vehicle['battery_percent']}%", 
                  delta=None if not st.session_state.trip_active else "-5%")
        st.metric("Range", f"{st.session_state.vehicle['range_miles']} mi")
        
        # Battery visualization
        battery_color = "🟢" if st.session_state.vehicle['battery_percent'] > 50 else "🟡" if st.session_state.vehicle['battery_percent'] > 20 else "🔴"
        st.progress(st.session_state.vehicle['battery_percent'] / 100)
        st.caption(f"{battery_color} Battery Status")
    
    st.markdown("---")
    st.markdown("### 🔔 Notifications")
    
    # Notifications Panel
    notif_container = st.container()
    with notif_container:
        if st.session_state.notifications:
            for notif in reversed(st.session_state.notifications[-5:]):
                icon = "✅" if notif['type'] == 'success' else "ℹ️"
                st.markdown(f"{icon} **{notif['time']}** - {notif['message']}")
        else:
            st.info("No notifications yet")
    
    st.markdown("---")
    st.markdown("### 🎯 Preferences")
    
    # Wallet options
    wallet_options = {
        "WALLET-12345": {"name": "John Doe"},
        "WALLET-67890": {"name": "Jane Smith"},
        "WALLET-11111": {"name": "Bob Johnson"},
        "WALLET-22222": {"name": "Alice Williams"},
        "WALLET-33333": {"name": "Demo User"}
    }
    
    with st.expander("Edit Preferences", expanded=False):
        auto_order = st.checkbox("Auto-order coffee/food", value=st.session_state.preferences['auto_order_coffee'])
        
        # Restaurant selection
        from utils.mock_data import get_mock_menu
        restaurants = ["Starbucks", "Subway", "McDonald's"]
        restaurant = st.selectbox("Preferred Restaurant", restaurants,
                                 index=restaurants.index(st.session_state.preferences.get('restaurant', 'Starbucks')))
        
        # Get menu from selected restaurant
        menu = get_mock_menu(restaurant)
        drinks = [item for item in menu if 'Latte' in item or 'Cappuccino' in item or 'Coffee' in item] + ["None"]
        foods = [item for item in menu if item not in drinks] + ["None"]
        
        favorite_drink = st.selectbox("Favorite Drink", drinks, 
                                      index=drinks.index(st.session_state.preferences.get('favorite_drink', drinks[0])) if st.session_state.preferences.get('favorite_drink') in drinks else 0)
        favorite_food = st.selectbox("Favorite Food", foods, 
                                     index=foods.index(st.session_state.preferences.get('favorite_food', foods[0])) if st.session_state.preferences.get('favorite_food') in foods else 0)
        
        # Create display labels with current balance from session state
        wallet_labels = [f"{wallet_id} - {info['name']} (${st.session_state.wallet_balances.get(wallet_id, 0):.2f})" 
                        for wallet_id, info in wallet_options.items()]
        wallet_ids = list(wallet_options.keys())
        
        # Find current wallet index
        current_wallet = st.session_state.preferences.get('wallet_id', 'WALLET-12345')
        current_index = wallet_ids.index(current_wallet) if current_wallet in wallet_ids else 0
        
        selected_wallet_label = st.selectbox(
            "Payment Wallet", 
            wallet_labels,
            index=current_index,
            help="Select wallet for charging and amenity payments"
        )
        
        # Extract wallet_id from selected label
        selected_wallet_id = wallet_ids[wallet_labels.index(selected_wallet_label)]
        
        if st.button("Save Preferences"):
            st.session_state.preferences = {
                "auto_order_coffee": auto_order,
                "restaurant": restaurant,
                "favorite_drink": favorite_drink,
                "favorite_food": favorite_food,
                "wallet_id": selected_wallet_id
            }
            st.success("Preferences saved!")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 💳 Active Wallet")
    
    # Display current wallet balance (from saved preferences)
    current_wallet_id = st.session_state.preferences.get('wallet_id', 'WALLET-12345')
    current_balance = st.session_state.wallet_balances.get(current_wallet_id, 0)
    current_wallet_name = wallet_options.get(current_wallet_id, {}).get('name', 'Unknown')
    
    st.markdown(f"**{current_wallet_name}**")
    st.markdown(f"`{current_wallet_id}`")
    st.metric("Balance", f"${current_balance:.2f}")
    
    # Reset balances button
    if st.button("🔄 Reset All Balances", help="Reset all wallet balances to initial values"):
        st.session_state.wallet_balances = {
            "WALLET-12345": 1250.00,
            "WALLET-67890": 2500.00,
            "WALLET-11111": 150.00,
            "WALLET-22222": 5000.00,
            "WALLET-33333": 500.00
        }
        st.success("All wallet balances reset!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>
    🤖 <b>Multi-Agent Architecture</b>: Trip Planning • Charging Negotiation • Amenities • Payment • Monitoring • Coordinator<br>
    Powered by <b>Amazon Bedrock (Claude 3.5 Sonnet)</b> + AWS Strands SDK
    </small>
</div>
""", unsafe_allow_html=True)
