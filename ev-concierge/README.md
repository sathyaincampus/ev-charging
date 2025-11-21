# 🚗 Proactive EV Concierge - Multi-Agent System

An intelligent, proactive EV charging assistant that manages your entire charging logistics using multiple specialized AI agents.

## 🏗️ Architecture

> **📖 See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation**

```mermaid
graph TB
    subgraph "User Interface"
        UI[Streamlit UI<br/>Real-time streaming]
    end
    
    subgraph "Coordinator"
        COORD[Coordinator Agent<br/>Orchestrates workflow]
    end
    
    subgraph "Specialized Agents - AWS Strands SDK"
        TRIP[Trip Planning<br/>✓ Async + Sync]
        CHARGE[Charging<br/>✓ Async + Sync]
        AMEN[Amenities<br/>✓ Async + Sync]
        PAY[Payment<br/>✓ Async + Sync]
        MON[Monitoring<br/>✓ Async + Sync]
    end
    
    subgraph "Tools Layer"
        TOOLS[@tool decorated<br/>Returns JSON strings]
    end
    
    subgraph "AWS Strands SDK"
        SDK[BedrockModel + Agent<br/>stream_async&#40;&#41;]
    end
    
    subgraph "AWS Services"
        BEDROCK[Amazon Bedrock<br/>Claude 3.5 Sonnet]
    end
    
    UI --> COORD
    COORD --> TRIP & CHARGE & AMEN & PAY & MON
    TRIP & CHARGE & AMEN & PAY & MON --> SDK
    TRIP & CHARGE & AMEN & PAY & MON --> TOOLS
    SDK --> BEDROCK
    
    style SDK fill:#FF9900
    style TRIP fill:#4CAF50
    style CHARGE fill:#4CAF50
    style AMEN fill:#4CAF50
    style PAY fill:#4CAF50
    style MON fill:#4CAF50
```

### Key Features
- ✅ **AWS Strands SDK**: Official agent framework
- ✅ **Async Architecture**: `stream_async()` with sync wrappers
- ✅ **Tool Calling**: `@tool` decorator with JSON returns
- ✅ **Event Streaming**: Real-time progressive responses
- ✅ **Multi-Agent**: 5 specialized agents + coordinator

## 📋 Required APIs & Services

### AWS Services (Required)
- **Amazon Bedrock**: Claude 3.5 Sonnet model access
- **AWS Strands SDK**: Agent orchestration framework
- **DynamoDB** (Optional): Store user preferences and trip history
- **AWS Secrets Manager** (Optional): Secure API key storage

### External APIs (Integration Points)
1. **Charging Networks**:
   - EVgo API - https://developer.evgo.com
   - ChargePoint API - https://developer.chargepoint.com
   - Tesla Supercharger API - https://developer.tesla.com
   - Electrify America API - https://developer.electrifyamerica.com

2. **Food & Amenities**:
   - Starbucks Mobile Order API
   - Uber Eats API
   - DoorDash API

3. **Payment**:
   - Stripe API - https://stripe.com/docs/api
   - Apple Pay API
   - Google Pay API

4. **Location & Route**:
   - Google Maps API - https://developers.google.com/maps
   - OpenWeatherMap API - https://openweathermap.org/api

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9+
python --version

# AWS CLI configured
aws configure

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### Run the Application
```bash
python app.py
```

Access the UI at: `http://localhost:7860`

## 💬 Example User Interactions

### Example 1: Basic Trip Planning
```
User: "I'm driving to Los Angeles tomorrow morning. Current battery is at 35%."

Agent: "I see you need charging for your LA trip. I've found an EVgo 350kW charger 
at Tejon Ranch with a slot at 10:00 AM. Would you like me to reserve it and 
pre-order your usual latte?"
```

### Example 2: Proactive Notification
```
Agent: "Good morning! I noticed you have a calendar event in San Diego tomorrow 
at 2 PM. Your current charge (42%) won't be enough. I recommend charging tonight 
at the nearby Electrify America station. Shall I book a slot for 8 PM?"
```

### Example 3: Emergency Re-routing
```
Agent: "Alert: Your reserved charger at Tejon Ranch is reported offline. I've 
automatically rebooked you at Bakersfield (15 min detour) at 10:15 AM. Your 
coffee order has been moved to the new location."
```

### Example 4: Cost Optimization
```
User: "Find me the cheapest charging option for my trip to San Francisco."

Agent: "I found 3 options:
1. EVgo (Gilroy) - $0.43/kWh - 350kW - 25 min
2. Electrify America (San Jose) - $0.38/kWh - 150kW - 45 min ⭐ Cheapest
3. Tesla Supercharger (Morgan Hill) - $0.45/kWh - 250kW - 30 min

Recommending option 2 to save $3.50. Shall I proceed?"
```

### Example 5: Multi-Stop Trip
```
User: "Road trip to Seattle with stops in SF and Portland. Battery at 80%."

Agent: "Planning your 3-day trip:
- Day 1: No charging needed (SF is 380 mi, you have range)
- Day 2: Charge in SF before Portland leg (reserved 7 AM slot)
- Day 3: Charge in Portland before Seattle (reserved 9 AM slot)

Total cost: $67. All reservations confirmed. Want breakfast orders too?"
```

## 📁 Project Structure

```
ev-concierge/
├── README.md
├── requirements.txt
├── .env.example
├── app.py                          # Main Gradio UI
├── agents/
│   ├── __init__.py
│   ├── coordinator.py              # Coordinator Agent
│   ├── trip_planning.py            # Trip Planning Agent
│   ├── charging_negotiation.py    # Charging Agent
│   ├── amenities.py                # Amenities Agent
│   ├── payment.py                  # Payment Agent
│   └── monitoring.py               # Monitoring Agent
├── tools/
│   ├── __init__.py
│   ├── charging_tools.py           # Charging network integrations
│   ├── amenities_tools.py          # Food ordering integrations
│   ├── payment_tools.py            # Payment processing
│   └── route_tools.py              # Maps & routing
├── utils/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   └── mock_data.py                # Mock API responses for demo
└── tests/
    ├── test_agents.py
    └── test_tools.py
```

## 🔧 Configuration

Edit `.env` file:
```env
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Charging Networks (Optional - uses mocks if not provided)
EVGO_API_KEY=your_key_here
CHARGEPOINT_API_KEY=your_key_here
ELECTRIFY_AMERICA_API_KEY=your_key_here

# Food & Amenities (Optional)
STARBUCKS_API_KEY=your_key_here

# Payment (Optional)
STRIPE_API_KEY=your_key_here

# Maps & Weather (Optional)
GOOGLE_MAPS_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
```

## 🎯 Features

- ✅ Multi-agent architecture with specialized agents
- ✅ Proactive trip analysis and charging recommendations
- ✅ Real-time charger availability and reservation
- ✅ Autonomous payment processing
- ✅ Pre-ordering food/coffee at charging locations
- ✅ Cost optimization across charging networks
- ✅ Emergency re-routing for broken chargers
- ✅ Natural language chat interface
- ✅ Mock mode for demo without real API keys

## 📊 Agent Responsibilities

| Agent | Purpose | Tools |
|-------|---------|-------|
| **Coordinator** | Orchestrates all agents, manages workflow | All agent APIs |
| **Trip Planning** | Analyzes energy needs, route optimization | Maps API, Weather API |
| **Charging Negotiation** | Finds & reserves optimal chargers | EVgo, ChargePoint, Tesla APIs |
| **Amenities** | Pre-orders food/drinks | Starbucks, Uber Eats APIs |
| **Payment** | Handles all transactions | Stripe, Wallet APIs |
| **Monitoring** | Real-time tracking & alerts | Charger status APIs |

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_agents.py -v
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.
