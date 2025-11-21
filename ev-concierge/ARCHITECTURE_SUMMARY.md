# Architecture Summary - EV Concierge

## Quick Overview

The EV Concierge is a **multi-agent system** built on **AWS Strands SDK** that uses **5 specialized agents** coordinated by a central orchestrator to manage EV charging logistics.

## System Layers (Top to Bottom)

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│              Streamlit UI (app_streamlit.py)            │
│           Real-time streaming chat interface            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   COORDINATOR AGENT                      │
│              (agents/coordinator.py)                     │
│         Orchestrates all agents & workflow              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              SPECIALIZED AGENT LAYER                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   Trip   │ │ Charging │ │Amenities │ │ Payment  │  │
│  │ Planning │ │   Agent  │ │  Agent   │ │  Agent   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                    ┌──────────┐                         │
│                    │Monitoring│                         │
│                    │  Agent   │                         │
│                    └──────────┘                         │
│         Each agent: Async + Sync wrapper                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    TOOL LAYER                            │
│  Route Tools | Charging Tools | Amenities | Payment    │
│  @tool decorated | Returns JSON strings                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 AWS STRANDS SDK                          │
│  BedrockModel + Agent + stream_async()                  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 AMAZON BEDROCK                           │
│            Claude 3.5 Sonnet Model                       │
└─────────────────────────────────────────────────────────┘
```

## Agent Responsibilities

| Agent | Purpose | Tools Used |
|-------|---------|------------|
| **Trip Planning** | Analyzes energy needs, determines charging strategy | `calculate_energy_needs`, `get_route_info` |
| **Charging** | Finds optimal chargers, makes reservations | `search_chargers`, `reserve_charging_slot`, `check_charger_status` |
| **Amenities** | Pre-orders food/drinks at charging locations | `check_nearby_amenities`, `get_restaurant_menu`, `place_food_order` |
| **Payment** | Processes all transactions autonomously | `process_payment`, `get_payment_history` |
| **Monitoring** | Tracks charger status, handles re-routing | `check_charger_status`, `cancel_reservation`, `search_chargers` |

## Code Pattern

### Agent Structure
```python
from strands.models import BedrockModel
from strands import Agent
import asyncio

class MyAgent:
    def __init__(self):
        self.model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            region_name="us-west-2",
            temperature=0.7
        )
    
    def method(self, data):
        """Sync wrapper"""
        return asyncio.run(self.method_async(data))
    
    async def method_async(self, data):
        """Async implementation"""
        agent = Agent(
            model=self.model,
            system_prompt="...",
            tools=[tool1, tool2]
        )
        
        async for event in agent.stream_async(prompt):
            # Process events
            ...
```

### Tool Structure
```python
from strands.tools import tool
import json

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    result = {"key": "value"}
    return json.dumps(result)
```

## Data Flow Example

### User Request: "I need to charge for my LA trip"

```
1. User Input → Streamlit UI
   ↓
2. Coordinator receives request
   ↓
3. Trip Planning Agent
   - Calls: calculate_energy_needs(battery=35, distance=380, range=300)
   - Returns: {"needs_charging": true, "deficit_percent": 113.7}
   ↓
4. Charging Agent
   - Calls: search_chargers(route="I-5", power_min=150)
   - Returns: [{"id": "EVgo-123", "location": "Tejon Ranch", ...}]
   - Calls: reserve_charging_slot(charger_id="EVgo-123", time="10:00")
   - Returns: {"reservation_id": "RES-456", "confirmed": true}
   ↓
5. Amenities Agent
   - Calls: check_nearby_amenities(location="Tejon Ranch")
   - Returns: [{"name": "Starbucks", "distance": 0.2}]
   - Calls: place_food_order(restaurant="Starbucks", items=["Latte"])
   - Returns: {"order_id": "ORD-789", "pickup_time": "10:15"}
   ↓
6. Payment Agent
   - Calls: process_payment(amount=18.50, merchant="EVgo")
   - Returns: {"transaction_id": "TXN-101", "status": "completed"}
   ↓
7. Coordinator aggregates results
   ↓
8. Streamlit UI displays summary
```

## Key Technologies

| Component | Technology |
|-----------|-----------|
| **Agent Framework** | AWS Strands SDK |
| **LLM Model** | Claude 3.5 Sonnet (Bedrock) |
| **Programming** | Python 3.9+ with async/await |
| **UI** | Streamlit |
| **Tool Calling** | `@tool` decorator |
| **Event Streaming** | `stream_async()` |

## Migration Highlights

### Before (Custom SDK)
```python
from strands import Strands

strands = Strands(model_id="...", region="...")
response = strands.run(
    system_prompt="...",
    user_prompt="...",
    tools=[...],
    max_iterations=5
)
```

### After (AWS Strands SDK)
```python
from strands.models import BedrockModel
from strands import Agent

model = BedrockModel(model_id="...", region_name="...")
agent = Agent(model=model, system_prompt="...", tools=[...])

async for event in agent.stream_async(user_prompt):
    # Process streaming events
```

## Performance Metrics

- **Tool Call Latency**: ~1-2 seconds
- **Agent Response**: ~2-5 seconds  
- **Full Orchestration**: ~10-15 seconds
- **Concurrent Requests**: Supported via async
- **Streaming**: Real-time progressive responses

## File Structure

```
ev-concierge/
├── app_streamlit.py          # UI
├── agents/
│   ├── coordinator.py         # Orchestrator
│   ├── trip_planning.py       # ✓ Async + Sync
│   ├── charging_negotiation.py # ✓ Async + Sync
│   ├── amenities.py           # ✓ Async + Sync
│   ├── payment.py             # ✓ Async + Sync
│   └── monitoring.py          # ✓ Async + Sync
├── tools/
│   ├── route_tools.py         # @tool, JSON returns
│   ├── charging_tools.py      # @tool, JSON returns
│   ├── amenities_tools.py     # @tool, JSON returns
│   └── payment_tools.py       # @tool, JSON returns
└── utils/
    ├── config.py              # Configuration
    └── mock_data.py           # Mock API responses
```

## Testing

- ✅ **Unit Tests**: Individual tool testing
- ✅ **Integration Tests**: Agent orchestration
- ✅ **E2E Tests**: Full user flows
- ✅ **Tool Calling**: Verified working
- ✅ **Event Streaming**: Verified working

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture
- **[STRANDS_SDK_MIGRATION.md](STRANDS_SDK_MIGRATION.md)** - Migration guide
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Test verification
- **[README.md](README.md)** - Getting started

---

**Version**: 2.0 (Post-Migration)  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-11-20
