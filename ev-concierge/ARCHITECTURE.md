# 🏗️ EV Concierge Architecture

## Overview

The EV Concierge is a multi-agent system built on AWS Strands SDK that orchestrates specialized AI agents to manage EV charging logistics proactively.

## Updated Architecture (Post-Migration)

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit UI<br/>app_streamlit.py]
    end
    
    subgraph "Coordinator Layer"
        COORD[Coordinator Agent<br/>coordinator.py<br/>Orchestrates workflow]
    end
    
    subgraph "Specialized Agent Layer"
        TRIP[Trip Planning Agent<br/>trip_planning.py<br/>✓ Async + Sync wrapper]
        CHARGE[Charging Negotiation Agent<br/>charging_negotiation.py<br/>✓ Async + Sync wrapper]
        AMEN[Amenities Agent<br/>amenities.py<br/>✓ Async + Sync wrapper]
        PAY[Payment Agent<br/>payment.py<br/>✓ Async + Sync wrapper]
        MON[Monitoring Agent<br/>monitoring.py<br/>✓ Async + Sync wrapper]
    end
    
    subgraph "Tool Layer"
        RT[Route Tools<br/>calculate_energy_needs<br/>get_route_info<br/>→ Returns JSON strings]
        CT[Charging Tools<br/>search_chargers<br/>reserve_charging_slot<br/>check_charger_status<br/>→ Returns JSON strings]
        AT[Amenities Tools<br/>check_nearby_amenities<br/>get_restaurant_menu<br/>place_food_order<br/>→ Returns JSON strings]
        PT[Payment Tools<br/>process_payment<br/>get_payment_history<br/>→ Returns JSON strings]
    end
    
    subgraph "AWS Strands SDK"
        BEDROCK_MODEL[BedrockModel<br/>Model Configuration<br/>region_name, temperature]
        AGENT_CLASS[Agent Class<br/>stream_async&#40;&#41;<br/>Event-based streaming]
        TOOL_DECORATOR[@tool Decorator<br/>Tool registration]
    end
    
    subgraph "AWS Services"
        BEDROCK[Amazon Bedrock<br/>Claude 3.5 Sonnet<br/>anthropic.claude-3-5-sonnet-20241022-v2:0]
        DYNAMO[DynamoDB<br/>User preferences & history]
        SECRETS[Secrets Manager<br/>API keys]
    end
    
    subgraph "External APIs"
        CHARGING_APIS[Charging Networks<br/>EVgo, ChargePoint<br/>Tesla, Electrify America]
        FOOD_APIS[Food Services<br/>Starbucks, Uber Eats]
        PAYMENT_APIS[Payment Services<br/>Stripe, Apple Pay]
        MAP_APIS[Location Services<br/>Google Maps, Weather]
    end
    
    UI --> COORD
    COORD --> TRIP
    COORD --> CHARGE
    COORD --> AMEN
    COORD --> PAY
    COORD --> MON
    
    TRIP --> BEDROCK_MODEL
    CHARGE --> BEDROCK_MODEL
    AMEN --> BEDROCK_MODEL
    PAY --> BEDROCK_MODEL
    MON --> BEDROCK_MODEL
    
    TRIP --> AGENT_CLASS
    CHARGE --> AGENT_CLASS
    AMEN --> AGENT_CLASS
    PAY --> AGENT_CLASS
    MON --> AGENT_CLASS
    
    TRIP --> RT
    CHARGE --> CT
    AMEN --> AT
    PAY --> PT
    MON --> CT
    
    RT --> TOOL_DECORATOR
    CT --> TOOL_DECORATOR
    AT --> TOOL_DECORATOR
    PT --> TOOL_DECORATOR
    
    BEDROCK_MODEL --> BEDROCK
    AGENT_CLASS --> BEDROCK
    
    RT --> MAP_APIS
    CT --> CHARGING_APIS
    AT --> FOOD_APIS
    PT --> PAYMENT_APIS
    
    COORD --> DYNAMO
    COORD --> SECRETS
    
    style BEDROCK_MODEL fill:#FF9900
    style AGENT_CLASS fill:#FF9900
    style TOOL_DECORATOR fill:#FF9900
    style TRIP fill:#4CAF50
    style CHARGE fill:#4CAF50
    style AMEN fill:#4CAF50
    style PAY fill:#4CAF50
    style MON fill:#4CAF50
```

## Architecture Layers

### 1. User Interface Layer
**Component**: `app_streamlit.py`
- Streamlit-based chat interface
- Real-time streaming responses
- Session management
- User input handling

### 2. Coordinator Layer
**Component**: `agents/coordinator.py`
- Orchestrates all specialized agents
- Manages workflow execution
- Aggregates results
- Generates comprehensive summaries
- Uses synchronous wrappers for agent calls

### 3. Specialized Agent Layer
Each agent follows this pattern:

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
    
    def my_method(self, data):
        """Synchronous wrapper for backward compatibility"""
        return asyncio.run(self.my_method_async(data))
    
    async def my_method_async(self, data):
        """Async implementation using Strands SDK"""
        agent = Agent(
            model=self.model,
            system_prompt="...",
            tools=[...]
        )
        
        response_text = ""
        tool_results = []
        
        async for event in agent.stream_async(user_prompt):
            # Extract text and tool results from events
            if isinstance(event, dict):
                if 'data' in event:
                    response_text += str(event['data'])
                
                if 'message' in event:
                    # Extract tool results from message content
                    ...
        
        return {"response": response_text, "tool_results": tool_results}
```

**Agents**:
1. **Trip Planning Agent** (`trip_planning.py`)
   - Analyzes energy requirements
   - Determines charging strategy
   - Tools: `calculate_energy_needs`, `get_route_info`

2. **Charging Negotiation Agent** (`charging_negotiation.py`)
   - Finds optimal chargers
   - Makes reservations
   - Tools: `search_chargers`, `reserve_charging_slot`, `check_charger_status`

3. **Amenities Agent** (`amenities.py`)
   - Finds nearby restaurants
   - Pre-orders food/drinks
   - Tools: `check_nearby_amenities`, `get_restaurant_menu`, `place_food_order`

4. **Payment Agent** (`payment.py`)
   - Processes transactions
   - Manages payment history
   - Tools: `process_payment`, `get_payment_history`

5. **Monitoring Agent** (`monitoring.py`)
   - Tracks charger status
   - Handles re-routing
   - Tools: `check_charger_status`, `cancel_reservation`, `search_chargers`

### 4. Tool Layer
All tools follow this pattern:

```python
from strands.tools import tool
import json

@tool
def my_tool(param: str) -> str:
    """Tool description for Claude"""
    result = {
        "key": "value"
    }
    return json.dumps(result)
```

**Key Requirements**:
- Use `@tool` decorator (lowercase)
- Return JSON strings (not dicts)
- Include clear docstrings
- Type hints for parameters

### 5. AWS Strands SDK Layer

**BedrockModel**:
- Configures the LLM model
- Sets temperature, region
- Manages model parameters

**Agent Class**:
- Orchestrates tool calling
- Streams responses via `stream_async()`
- Handles event loop
- Manages conversation state

**Tool Decorator**:
- Registers tools with agents
- Generates tool schemas
- Validates parameters

### 6. AWS Services Layer

**Amazon Bedrock**:
- Hosts Claude 3.5 Sonnet model
- Processes agent requests
- Executes tool calls
- Generates responses

**DynamoDB** (Optional):
- Stores user preferences
- Maintains trip history
- Caches charger data

**Secrets Manager** (Optional):
- Securely stores API keys
- Manages credentials

### 7. External APIs Layer

**Charging Networks**:
- EVgo API
- ChargePoint API
- Tesla Supercharger API
- Electrify America API

**Food Services**:
- Starbucks Mobile Order
- Uber Eats
- DoorDash

**Payment Services**:
- Stripe
- Apple Pay
- Google Pay

**Location Services**:
- Google Maps API
- OpenWeatherMap API

## Data Flow

### 1. User Request Flow
```
User Input → Streamlit UI → Coordinator Agent
```

### 2. Agent Orchestration Flow
```
Coordinator → Trip Planning Agent → Energy Analysis
           → Charging Agent → Find & Reserve Charger
           → Amenities Agent → Pre-order Food
           → Payment Agent → Process Payments
           → Monitoring Agent → Track Status
```

### 3. Tool Execution Flow
```
Agent → BedrockModel → Claude 3.5 Sonnet
     → Tool Call Decision
     → Tool Execution (via @tool decorator)
     → Tool Result (JSON string)
     → Claude Analysis
     → Final Response
```

### 4. Event Stream Flow
```
agent.stream_async(prompt)
  → {'data': 'text chunk'}
  → {'message': {'content': [{'toolUse': {...}}]}}
  → {'message': {'content': [{'toolResult': {...}}]}}
  → {'data': 'final response'}
```

## Key Design Patterns

### 1. Async with Sync Wrappers
All agents provide both async and sync interfaces:
- `method_async()` - Native async implementation
- `method()` - Sync wrapper using `asyncio.run()`

**Benefits**:
- Backward compatibility
- Easy integration with sync code
- Performance benefits of async

### 2. Event-Based Streaming
Agents use `stream_async()` for real-time responses:
- Progressive text generation
- Tool call visibility
- Better user experience

### 3. Tool Result Extraction
Tool results are extracted from nested event structure:
```python
event['message']['content'][]['toolResult']['content'][]['text']
```

### 4. JSON String Returns
All tools return JSON strings for compatibility:
```python
return json.dumps({"key": "value"})
```

## Configuration

### Environment Variables
```env
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
USE_MOCK_DATA=true  # Set to false for real APIs
```

### Model Configuration
```python
BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-west-2",
    temperature=0.7,
    performance_config={"latency": "optimized"}
)
```

## Testing Architecture

### Unit Tests
- Test individual tools
- Verify JSON string returns
- Check parameter validation

### Integration Tests
- Test agent orchestration
- Verify tool calling
- Check event stream parsing

### End-to-End Tests
- Test complete user flows
- Verify multi-agent coordination
- Check UI integration

## Migration Notes

### What Changed
1. **SDK**: Custom implementation → AWS Strands SDK
2. **Imports**: `from strands import Strands` → `from strands.models import BedrockModel`
3. **Execution**: `strands.run()` → `agent.stream_async()`
4. **Tools**: `@Tool` → `@tool`, dict returns → JSON string returns
5. **Async**: Added async methods with sync wrappers

### What Stayed the Same
1. Agent responsibilities
2. Tool functionality
3. User interface
4. Orchestration logic
5. External API integrations

## Performance Characteristics

### Latency
- **Tool Call**: ~1-2 seconds
- **Agent Response**: ~2-5 seconds
- **Full Orchestration**: ~10-15 seconds

### Scalability
- Async architecture supports concurrent requests
- Each agent can be scaled independently
- Tool calls are parallelizable

### Cost Optimization
- Streaming reduces perceived latency
- Tool results cached when possible
- Model temperature tuned for efficiency

## Security Considerations

1. **API Keys**: Stored in AWS Secrets Manager
2. **User Data**: Encrypted in DynamoDB
3. **Payment Info**: Never stored, tokenized via Stripe
4. **AWS Credentials**: IAM roles with least privilege
5. **Tool Validation**: Input sanitization on all tools

## Future Enhancements

1. **Multi-Region Support**: Deploy agents across regions
2. **Caching Layer**: Redis for tool result caching
3. **Monitoring**: CloudWatch metrics and alarms
4. **A/B Testing**: Compare agent strategies
5. **Voice Interface**: Alexa/Google Assistant integration

## References

- [AWS Strands SDK Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Claude 3.5 Sonnet](https://www.anthropic.com/claude)
- [Automotive Reference Implementation](../automotive/agents.py)

---

**Last Updated**: 2025-11-20  
**Version**: 2.0 (Post-Strands SDK Migration)  
**Status**: Production Ready
