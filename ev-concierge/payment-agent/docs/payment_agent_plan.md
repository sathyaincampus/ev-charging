# 💳 Payment Agent - Development Specification

## 📋 Overview

**Purpose:** Develop an independent, production-ready Payment Agent that handles autonomous payment processing, wallet management, and transaction operations. This agent will be used by the Coordinator Agent and can be called by other agents (Charging, Amenities, etc.) for payment operations.

**Status:** Development Spec  
**Version:** 1.0  
**Last Updated:** 2025-11-20

---

## 🎯 Goals

### Primary Goals
1. **Independent Operation:** Agent works standalone without dependencies on other agents
2. **Coordinator Integration:** Exposes clean API for Coordinator to orchestrate payments
3. **Multi-Agent Support:** Other agents can request payment operations
4. **Intelligent Processing:** AI-powered decision making for payment routing and optimization
5. **Demo-Ready:** Full mock implementation for demonstration without real payment APIs

### Success Criteria
- ✅ Process single and batch payments autonomously
- ✅ Handle payment failures with intelligent retry logic
- ✅ Manage multiple payment methods per wallet
- ✅ Provide transaction history and reporting
- ✅ Support refunds and cancellations
- ✅ Expose clean API for other agents
- ✅ Complete demo UI for standalone testing

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                  Coordinator Agent                       │
│              (Orchestrates all agents)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ calls payment_agent.process_payment()
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Payment Agent                           │
│  - process_payment()                                     │
│  - process_batch_payments()                              │
│  - initiate_refund()                                     │
│  - get_transaction_history()                             │
│  - validate_wallet()                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ uses tools
                     │
┌────────────────────▼────────────────────────────────────┐
│              Payment Tools (10+ tools)                   │
│  - process_payment()                                     │
│  - validate_wallet()                                     │
│  - calculate_fees()                                      │
│  - process_batch_payments()                              │
│  - initiate_refund()                                     │
│  - get_wallet_balance()                                  │
│  - add_payment_method()                                  │
│  - verify_transaction()                                  │
│  - generate_receipt()                                    │
│  - get_payment_history()                                 │
└─────────────────────────────────────────────────────────┘
```

### Integration Points

**Called By:**
- Coordinator Agent (primary orchestrator)
- Charging Negotiation Agent (for charging payments)
- Amenities Agent (for food/coffee orders)
- Monitoring Agent (for refunds on failed services)

**Calls:**
- Payment Tools (internal)
- AWS Bedrock (for AI reasoning)
- Mock Payment APIs (demo mode)
- Real Payment APIs (production mode)

---

## 📦 Components

### 1. Payment Agent (`agents/payment.py`)

#### Public Methods (API for Other Agents)

```python
class PaymentAgent:
    """
    Autonomous payment processing agent with AI-powered decision making.
    Can be used independently or called by Coordinator/other agents.
    """
    
    def process_payment(
        self,
        amount: float,
        merchant: str,
        wallet_id: str,
        description: str = "",
        payment_method: str = "auto"
    ) -> dict:
        """
        Process a single payment transaction.
        
        Args:
            amount: Payment amount in USD
            merchant: Merchant name/ID
            wallet_id: User's wallet identifier
            description: Transaction description
            payment_method: Specific method or "auto" for intelligent selection
            
        Returns:
            {
                "success": bool,
                "transaction_id": str,
                "amount": float,
                "payment_method": str,
                "timestamp": str,
                "receipt": dict,
                "message": str
            }
        """
        
    def process_batch_payments(
        self,
        transactions: list[dict],
        wallet_id: str
    ) -> dict:
        """
        Process multiple payments in a batch.
        
        Args:
            transactions: List of payment dicts with amount, merchant, description
            wallet_id: User's wallet identifier
            
        Returns:
            {
                "success": bool,
                "total_processed": int,
                "total_amount": float,
                "successful": list[dict],
                "failed": list[dict],
                "summary": str
            }
        """
        
    def initiate_refund(
        self,
        transaction_id: str,
        reason: str,
        amount: float = None
    ) -> dict:
        """
        Initiate a refund for a previous transaction.
        
        Args:
            transaction_id: Original transaction ID
            reason: Refund reason
            amount: Partial refund amount (None for full refund)
            
        Returns:
            {
                "success": bool,
                "refund_id": str,
                "amount": float,
                "status": str,
                "estimated_days": int,
                "message": str
            }
        """
        
    def validate_wallet(
        self,
        wallet_id: str,
        required_amount: float = None
    ) -> dict:
        """
        Validate wallet and check if it can process payment.
        
        Args:
            wallet_id: User's wallet identifier
            required_amount: Amount to check availability for
            
        Returns:
            {
                "valid": bool,
                "balance": float,
                "can_process": bool,
                "payment_methods": list[dict],
                "message": str
            }
        """
        
    def get_transaction_history(
        self,
        wallet_id: str,
        limit: int = 10,
        filters: dict = None
    ) -> dict:
        """
        Get transaction history for a wallet.
        
        Args:
            wallet_id: User's wallet identifier
            limit: Number of transactions to return
            filters: Optional filters (date_from, date_to, merchant, status)
            
        Returns:
            {
                "transactions": list[dict],
                "total_count": int,
                "total_amount": float,
                "summary": str
            }
        """
```

#### Internal Methods

```python
    def _select_payment_method(self, wallet_id: str, amount: float) -> str:
        """Intelligently select best payment method based on amount, fees, balance"""
        
    def _detect_fraud(self, transaction: dict) -> dict:
        """Simulate fraud detection on transaction"""
        
    def _retry_payment(self, transaction: dict, max_retries: int = 3) -> dict:
        """Retry failed payment with exponential backoff"""
        
    def _generate_summary(self, results: dict) -> str:
        """Generate human-readable summary using AI"""
```

---

### 2. Payment Tools (`tools/payment_tools.py`)

#### Tool Specifications

```python
@Tool
def process_payment(
    amount: float,
    wallet_id: str,
    merchant: str,
    description: str,
    payment_method: str = "default"
) -> dict:
    """
    Process a single payment transaction.
    
    Returns transaction details with ID, status, timestamp.
    Simulates 2-3 second processing time in mock mode.
    """

@Tool
def validate_wallet(wallet_id: str) -> dict:
    """
    Validate wallet ID and return wallet details.
    
    Returns wallet status, balance, available payment methods.
    """

@Tool
def get_wallet_balance(wallet_id: str) -> dict:
    """
    Get current wallet balance across all payment methods.
    
    Returns total balance, breakdown by payment method.
    """

@Tool
def calculate_fees(amount: float, payment_method: str, merchant_type: str) -> dict:
    """
    Calculate transaction fees based on amount and payment method.
    
    Returns fee amount, percentage, total with fees.
    """

@Tool
def process_batch_payments(transactions: list[dict], wallet_id: str) -> dict:
    """
    Process multiple payments in a single batch operation.
    
    Returns summary with successful/failed transactions.
    """

@Tool
def initiate_refund(
    transaction_id: str,
    amount: float,
    reason: str
) -> dict:
    """
    Initiate a refund for a previous transaction.
    
    Returns refund ID, status, estimated processing time.
    """

@Tool
def add_payment_method(
    wallet_id: str,
    method_type: str,
    details: dict
) -> dict:
    """
    Add a new payment method to wallet.
    
    Returns payment method ID and confirmation.
    """

@Tool
def verify_transaction(transaction_id: str) -> dict:
    """
    Verify the status of a transaction.
    
    Returns current status, details, and any issues.
    """

@Tool
def generate_receipt(transaction_id: str) -> dict:
    """
    Generate a detailed receipt for a transaction.
    
    Returns formatted receipt with all transaction details.
    """

@Tool
def get_payment_history(
    wallet_id: str,
    limit: int = 10,
    date_from: str = None,
    date_to: str = None
) -> list:
    """
    Get payment history for a wallet with optional filters.
    
    Returns list of transactions with details.
    """
```

---

### 3. Mock Data Generator (`utils/mock_payment_data.py`)

#### Mock Data Structures

```python
class MockPaymentData:
    """Generate realistic mock payment data for demo"""
    
    @staticmethod
    def generate_wallet(wallet_id: str) -> dict:
        """Generate mock wallet with balance and payment methods"""
        
    @staticmethod
    def generate_transaction_history(wallet_id: str, count: int = 20) -> list:
        """Generate realistic transaction history"""
        
    @staticmethod
    def generate_merchants() -> list:
        """Generate list of mock merchants (charging, food, parking, etc.)"""
        
    @staticmethod
    def generate_payment_methods() -> list:
        """Generate mock payment methods (cards, Apple Pay, etc.)"""
        
    @staticmethod
    def calculate_realistic_fees(amount: float, method: str) -> float:
        """Calculate realistic transaction fees"""
```

#### Mock Data Examples

**Wallet Structure:**
```json
{
  "wallet_id": "WALLET-12345",
  "balance": 1250.00,
  "currency": "USD",
  "payment_methods": [
    {
      "id": "PM-001",
      "type": "credit_card",
      "brand": "Visa",
      "last4": "4242",
      "default": true,
      "balance": 5000.00
    },
    {
      "id": "PM-002",
      "type": "apple_pay",
      "linked_card": "PM-001",
      "default": false
    }
  ],
  "spending_limit": 500.00,
  "monthly_spent": 342.50
}
```

**Transaction Structure:**
```json
{
  "transaction_id": "TXN-1732123456",
  "wallet_id": "WALLET-12345",
  "amount": 24.50,
  "fee": 0.71,
  "total": 25.21,
  "merchant": "EVgo Charging",
  "merchant_type": "charging",
  "description": "Fast charging session",
  "payment_method": "PM-001",
  "status": "completed",
  "timestamp": "2025-11-20T10:30:00Z",
  "receipt_url": "https://receipts.example.com/TXN-1732123456"
}
```

---

### 4. Demo UI (`payment_demo.py`)

#### UI Components

**1. Dashboard Section**
- Wallet balance display
- Active payment methods
- Monthly spending chart
- Quick stats (total transactions, total spent)

**2. Payment Processing Section**
- Single payment form
- Batch payment upload (CSV)
- Quick payment presets
- Real-time agent activity monitor

**3. Transaction History Section**
- Searchable transaction list
- Filters (date, merchant, amount, status)
- Export to CSV
- Refund request button

**4. Wallet Management Section**
- Payment methods list
- Add new payment method
- Set default method
- View spending limits

**5. Agent Activity Monitor**
- Real-time tool calls
- AI reasoning display
- Decision transparency
- Performance metrics

#### Demo Scenarios

```python
DEMO_SCENARIOS = {
    "single_payment": {
        "name": "Single Charging Payment",
        "amount": 24.50,
        "merchant": "EVgo Charging",
        "description": "Fast charging session at Tejon Ranch"
    },
    "batch_payment": {
        "name": "Trip Expenses Batch",
        "transactions": [
            {"amount": 24.50, "merchant": "EVgo", "description": "Charging"},
            {"amount": 6.75, "merchant": "Starbucks", "description": "Coffee"},
            {"amount": 12.00, "merchant": "ParkMobile", "description": "Parking"}
        ]
    },
    "insufficient_funds": {
        "name": "Insufficient Balance",
        "amount": 2000.00,
        "merchant": "Tesla Service",
        "description": "Trigger split payment scenario"
    },
    "refund_request": {
        "name": "Refund Broken Charger",
        "transaction_id": "TXN-1732123456",
        "reason": "Charger was non-functional"
    },
    "fraud_detection": {
        "name": "Suspicious Transaction",
        "amount": 999.99,
        "merchant": "Unknown Merchant",
        "description": "Trigger fraud detection"
    }
}
```

---

## 🔧 Implementation Details

### Phase 1: Enhanced Payment Tools (Priority 1)

**Files to Create/Modify:**
- ✏️ `tools/payment_tools.py` - Add 8 new tools, enhance existing 2
- 🆕 `utils/mock_payment_data.py` - Create mock data generator

**Tasks:**
1. Implement `validate_wallet()` with realistic wallet data
2. Implement `get_wallet_balance()` with multi-method breakdown
3. Implement `calculate_fees()` with realistic fee structures
4. Implement `process_batch_payments()` with parallel processing simulation
5. Implement `initiate_refund()` with status tracking
6. Implement `add_payment_method()` with validation
7. Implement `verify_transaction()` with status checks
8. Implement `generate_receipt()` with formatted output
9. Enhance `process_payment()` with delays and error simulation
10. Enhance `get_payment_history()` with filtering

**Mock Data Requirements:**
- 5+ wallet profiles with different balances
- 20+ transaction history per wallet
- 10+ merchant types (charging, food, parking, etc.)
- 3+ payment method types (credit, debit, digital wallet)
- Realistic fee structures (2.9% + $0.30 for cards, etc.)

### Phase 2: Enhanced Payment Agent (Priority 2)

**Files to Modify:**
- ✏️ `agents/payment.py` - Add public API methods and intelligence

**Tasks:**
1. Implement `process_payment()` public method
2. Implement `process_batch_payments()` public method
3. Implement `initiate_refund()` public method
4. Implement `validate_wallet()` public method
5. Implement `get_transaction_history()` public method
6. Add `_select_payment_method()` intelligence
7. Add `_detect_fraud()` simulation
8. Add `_retry_payment()` with exponential backoff
9. Add `_generate_summary()` using AI
10. Add comprehensive error handling

**AI Intelligence Features:**
- Smart payment method selection based on amount and fees
- Fraud detection patterns (unusual amounts, unknown merchants)
- Automatic retry logic with different payment methods
- Budget tracking and alerts
- Natural language summary generation

### Phase 3: Demo UI (Priority 3)

**Files to Create:**
- 🆕 `payment_demo.py` - Standalone Streamlit demo
- 🆕 `start_payment_demo.sh` - Quick start script

**Tasks:**
1. Create dashboard layout with metrics
2. Build single payment form with validation
3. Build batch payment upload interface
4. Create transaction history table with filters
5. Add wallet management section
6. Build agent activity monitor with real-time updates
7. Add demo scenario buttons
8. Create export functionality
9. Add charts and visualizations
10. Polish UI/UX

### Phase 4: Integration & Testing (Priority 4)

**Tasks:**
1. Test all payment tools independently
2. Test agent with various scenarios
3. Test coordinator integration
4. Create integration examples for other agents
5. Write documentation
6. Create demo video script

---

## 📊 Data Models

### Payment Request Model

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PaymentRequest(BaseModel):
    amount: float
    merchant: str
    wallet_id: str
    description: Optional[str] = ""
    payment_method: Optional[str] = "auto"
    metadata: Optional[dict] = {}

class BatchPaymentRequest(BaseModel):
    transactions: List[PaymentRequest]
    wallet_id: str
    
class RefundRequest(BaseModel):
    transaction_id: str
    reason: str
    amount: Optional[float] = None  # None = full refund
```

### Response Models

```python
class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str
    amount: float
    fee: float
    total: float
    payment_method: str
    timestamp: datetime
    receipt: dict
    message: str

class BatchPaymentResponse(BaseModel):
    success: bool
    total_processed: int
    total_amount: float
    successful: List[PaymentResponse]
    failed: List[dict]
    summary: str

class RefundResponse(BaseModel):
    success: bool
    refund_id: str
    amount: float
    status: str
    estimated_days: int
    message: str
```

---

## 🔌 Integration Examples

### Example 1: Coordinator Calling Payment Agent

```python
# In coordinator.py
from agents.payment import PaymentAgent

class CoordinatorAgent:
    def __init__(self):
        self.payment_agent = PaymentAgent()
    
    def orchestrate(self, vehicle_data, trip_data, user_prefs):
        # ... other agent calls ...
        
        # Process payments for charging and amenities
        transactions = [
            {
                "amount": 24.50,
                "merchant": "EVgo Charging",
                "description": "Fast charging at Tejon Ranch"
            },
            {
                "amount": 6.75,
                "merchant": "Starbucks",
                "description": "Large Latte"
            }
        ]
        
        payment_result = self.payment_agent.process_batch_payments(
            transactions=transactions,
            wallet_id=user_prefs['wallet_id']
        )
        
        return payment_result
```

### Example 2: Charging Agent Requesting Payment

```python
# In charging_negotiation.py
from agents.payment import PaymentAgent

class ChargingNegotiationAgent:
    def __init__(self):
        self.payment_agent = PaymentAgent()
    
    def reserve_and_pay(self, charger_info, wallet_id):
        # Reserve charger
        reservation = self.reserve_charging_slot(charger_info)
        
        # Process payment
        payment_result = self.payment_agent.process_payment(
            amount=charger_info['cost'],
            merchant=charger_info['network'],
            wallet_id=wallet_id,
            description=f"Charging reservation {reservation['id']}"
        )
        
        if not payment_result['success']:
            # Cancel reservation if payment fails
            self.cancel_reservation(reservation['id'])
            
        return payment_result
```

### Example 3: Monitoring Agent Requesting Refund

```python
# In monitoring.py
from agents.payment import PaymentAgent

class MonitoringAgent:
    def __init__(self):
        self.payment_agent = PaymentAgent()
    
    def handle_broken_charger(self, transaction_id):
        # Initiate refund for broken charger
        refund_result = self.payment_agent.initiate_refund(
            transaction_id=transaction_id,
            reason="Charger was non-functional upon arrival"
        )
        
        return refund_result
```

---

## 🎯 Demo Scenarios

### Scenario 1: Happy Path - Single Payment
**Input:** Process $24.50 charging payment  
**Expected:** Successful payment, receipt generated, balance updated  
**Agent Actions:** Validate wallet → Calculate fees → Process payment → Generate receipt

### Scenario 2: Batch Payment Processing
**Input:** Process 5 payments (charging, food, parking)  
**Expected:** All payments processed, summary generated  
**Agent Actions:** Validate wallet → Process batch → Generate summary

### Scenario 3: Insufficient Funds
**Input:** Payment amount exceeds wallet balance  
**Expected:** Split payment across multiple methods or suggest alternative  
**Agent Actions:** Check balance → Detect insufficient funds → Suggest split payment

### Scenario 4: Payment Failure & Retry
**Input:** Payment fails due to network error  
**Expected:** Automatic retry with exponential backoff  
**Agent Actions:** Attempt payment → Detect failure → Retry with delay → Success

### Scenario 5: Fraud Detection
**Input:** Unusual payment (high amount, unknown merchant)  
**Expected:** Flag transaction, request verification  
**Agent Actions:** Analyze transaction → Detect anomaly → Request verification

### Scenario 6: Refund Processing
**Input:** Refund request for broken charger  
**Expected:** Refund initiated, confirmation provided  
**Agent Actions:** Verify transaction → Process refund → Update history

---

## 📈 Success Metrics

### Functional Metrics
- ✅ All 10 payment tools working correctly
- ✅ Agent handles 6+ demo scenarios successfully
- ✅ 100% success rate for valid transactions
- ✅ Proper error handling for invalid transactions
- ✅ Transaction history accurately maintained

### Performance Metrics
- ⚡ Single payment processing: < 3 seconds
- ⚡ Batch payment (5 items): < 5 seconds
- ⚡ Transaction history retrieval: < 1 second
- ⚡ Wallet validation: < 1 second

### Integration Metrics
- 🔌 Clean API for coordinator integration
- 🔌 Easy to call from other agents
- 🔌 Comprehensive error responses
- 🔌 Well-documented methods

### Demo Metrics
- 🎨 Professional, intuitive UI
- 🎨 Real-time agent activity visualization
- 🎨 Clear transaction history display
- 🎨 Easy scenario testing

---

## 📝 Documentation Requirements

### Code Documentation
- Docstrings for all public methods
- Type hints for all parameters
- Example usage in docstrings
- Error handling documentation

### User Documentation
- README for payment agent
- API reference guide
- Integration guide for other agents
- Demo scenario guide

### Developer Documentation
- Architecture diagrams
- Data flow diagrams
- Mock data structure reference
- Testing guide

---

## 🚀 Deployment Considerations

### Mock Mode (Demo)
- No real API keys required
- Simulated processing delays
- Realistic mock data
- Safe for public demos

### Production Mode
- Real payment API integration (Stripe, etc.)
- Secure credential management
- PCI compliance considerations
- Transaction logging and auditing
- Error monitoring and alerting

---

## 🔐 Security Considerations

### Mock Mode
- No real payment data
- Simulated security checks
- Educational fraud detection

### Production Mode
- PCI DSS compliance
- Encrypted payment data
- Secure API key storage (AWS Secrets Manager)
- Transaction audit logs
- Fraud detection integration
- Rate limiting
- IP whitelisting

---

## 📅 Timeline

### Week 1: Core Development
- Day 1-2: Payment tools implementation
- Day 3-4: Payment agent enhancement
- Day 5: Mock data generator

### Week 2: Demo & Integration
- Day 1-2: Demo UI development
- Day 3: Integration testing
- Day 4: Documentation
- Day 5: Polish and demo preparation

---

## ✅ Acceptance Criteria

### Must Have
- [ ] All 10 payment tools implemented and tested
- [ ] Payment agent with 5 public methods
- [ ] Mock data generator with realistic data
- [ ] Standalone demo UI working
- [ ] Integration with coordinator agent
- [ ] Comprehensive error handling
- [ ] Documentation complete

### Should Have
- [ ] 6+ demo scenarios working
- [ ] Real-time agent activity monitor
- [ ] Transaction export functionality
- [ ] Spending analytics
- [ ] Budget alerts

### Nice to Have
- [ ] Payment method recommendations
- [ ] Multi-currency support
- [ ] Scheduled payments
- [ ] Payment splitting logic
- [ ] Advanced fraud detection

---

## 🤝 Integration Contract

### For Coordinator Agent

```python
# Coordinator can call these methods:
payment_agent.process_payment(amount, merchant, wallet_id, description)
payment_agent.process_batch_payments(transactions, wallet_id)
payment_agent.validate_wallet(wallet_id, required_amount)
payment_agent.get_transaction_history(wallet_id, limit, filters)
```

### For Other Agents

```python
# Any agent can request payment:
from agents.payment import PaymentAgent

payment_agent = PaymentAgent()
result = payment_agent.process_payment(
    amount=24.50,
    merchant="EVgo",
    wallet_id="WALLET-12345",
    description="Charging session"
)

if result['success']:
    # Payment successful
    transaction_id = result['transaction_id']
else:
    # Handle payment failure
    error_message = result['message']
```

---

## 📚 References

- AWS Bedrock Documentation: https://docs.aws.amazon.com/bedrock
- Stripe API Reference: https://stripe.com/docs/api
- Streamlit Documentation: https://docs.streamlit.io
- Pydantic Models: https://docs.pydantic.dev

---

**End of Specification**

This document serves as the complete specification for developing the Payment Agent independently and integrating it with the EV Concierge multi-agent system.
