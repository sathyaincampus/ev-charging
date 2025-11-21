# 💳 Payment Tools - Quick Reference Guide

## 📚 Tool Overview

| # | Tool Name | Purpose | Response Time |
|---|-----------|---------|---------------|
| 1 | `process_payment()` | Process single payment | 1.5-3s |
| 2 | `validate_wallet()` | Validate wallet & get details | Instant |
| 3 | `get_wallet_balance()` | Get balance breakdown | Instant |
| 4 | `calculate_fees()` | Calculate transaction fees | Instant |
| 5 | `process_batch_payments()` | Process multiple payments | 2s + processing |
| 6 | `initiate_refund()` | Start refund process | 1.5s |
| 7 | `add_payment_method()` | Add new payment method | 1s |
| 8 | `verify_transaction()` | Check transaction status | 0.5s |
| 9 | `generate_receipt()` | Create detailed receipt | 0.3s |
| 10 | `get_payment_history()` | Retrieve transaction history | Instant |

---

## 🔧 Tool Details

### 1️⃣ process_payment()

**Purpose:** Process a single payment transaction

**Parameters:**
```python
amount: float           # Payment amount in USD
wallet_id: str         # User's wallet identifier
merchant: str          # Merchant name/ID
description: str       # Transaction description
payment_method: str    # "default" or specific method ID
```

**Returns:**
```python
{
    "success": bool,
    "transaction_id": str,
    "amount": float,
    "fee": float,
    "total": float,
    "merchant": str,
    "status": str,
    "timestamp": str,
    "receipt_url": str,
    "message": str
}
```

**Example:**
```python
result = process_payment(
    amount=24.50,
    wallet_id="WALLET-12345",
    merchant="EVgo Charging",
    description="Fast charging session"
)
```

---

### 2️⃣ validate_wallet()

**Purpose:** Validate wallet and return complete details

**Parameters:**
```python
wallet_id: str         # User's wallet identifier
```

**Returns:**
```python
{
    "valid": bool,
    "wallet_id": str,
    "name": str,
    "balance": float,
    "payment_methods": list,
    "spending_limit": float,
    "monthly_spent": float,
    "remaining_limit": float,
    "message": str
}
```

**Example:**
```python
result = validate_wallet("WALLET-12345")
if result['valid']:
    print(f"Balance: ${result['balance']:.2f}")
```

---

### 3️⃣ get_wallet_balance()

**Purpose:** Get balance breakdown across all payment methods

**Parameters:**
```python
wallet_id: str         # User's wallet identifier
```

**Returns:**
```python
{
    "wallet_id": str,
    "primary_balance": float,
    "total_balance": float,
    "payment_methods": [
        {
            "id": str,
            "type": str,
            "brand": str,
            "balance": float,
            "default": bool
        }
    ],
    "message": str
}
```

---

### 4️⃣ calculate_fees()

**Purpose:** Calculate transaction fees before processing

**Parameters:**
```python
amount: float          # Transaction amount
payment_method: str    # Payment method type
merchant_type: str     # Merchant category
```

**Returns:**
```python
{
    "amount": float,
    "fee": float,
    "fee_percent": float,
    "total": float,
    "breakdown": dict,
    "message": str
}
```

**Fee Structures:**
- Credit Card: 2.9% + $0.30
- Debit Card: 1.5% + $0.25
- Apple Pay: 2.5% + $0.20
- Google Pay: 2.5% + $0.20

---

### 5️⃣ process_batch_payments()

**Purpose:** Process multiple payments efficiently

**Parameters:**
```python
transactions: list     # List of transaction dicts
wallet_id: str        # User's wallet identifier
```

**Transaction Format:**
```python
{
    "amount": float,
    "merchant": str,
    "description": str,
    "payment_method": str  # optional
}
```

**Returns:**
```python
{
    "success": bool,
    "total_transactions": int,
    "successful_count": int,
    "failed_count": int,
    "total_amount": float,
    "successful": list,
    "failed": list,
    "message": str
}
```

---

### 6️⃣ initiate_refund()

**Purpose:** Start refund process for a transaction

**Parameters:**
```python
transaction_id: str    # Original transaction ID
amount: float         # Refund amount
reason: str           # Refund reason
```

**Returns:**
```python
{
    "success": bool,
    "refund_id": str,
    "amount": float,
    "status": str,
    "estimated_days": int,
    "estimated_date": str,
    "message": str
}
```

---

### 7️⃣ add_payment_method()

**Purpose:** Add new payment method to wallet

**Parameters:**
```python
wallet_id: str        # User's wallet identifier
method_type: str      # Payment method type
details: dict         # Payment method details
```

**Returns:**
```python
{
    "success": bool,
    "payment_method_id": str,
    "type": str,
    "brand": str,
    "status": str,
    "message": str
}
```

---

### 8️⃣ verify_transaction()

**Purpose:** Check current status of a transaction

**Parameters:**
```python
transaction_id: str    # Transaction ID to verify
```

**Returns:**
```python
{
    "transaction_id": str,
    "status": str,         # completed, pending, failed, refunded
    "verified": bool,
    "message": str
}
```

---

### 9️⃣ generate_receipt()

**Purpose:** Generate detailed receipt for transaction

**Parameters:**
```python
transaction_id: str    # Transaction ID
```

**Returns:**
```python
{
    "receipt_id": str,
    "transaction_id": str,
    "date": str,
    "merchant": str,
    "items": list,
    "subtotal": float,
    "fee": float,
    "total": float,
    "payment_method": str,
    "status": str,
    "receipt_url": str
}
```

---

### 🔟 get_payment_history()

**Purpose:** Retrieve transaction history with filters

**Parameters:**
```python
wallet_id: str        # User's wallet identifier
limit: int           # Number of transactions (default: 10)
date_from: str       # Filter from date (optional)
date_to: str         # Filter to date (optional)
merchant: str        # Filter by merchant (optional)
status: str          # Filter by status (optional)
```

**Returns:**
```python
[
    {
        "transaction_id": str,
        "amount": float,
        "merchant": str,
        "status": str,
        "timestamp": str,
        ...
    }
]
```

---

## 🎭 Mock Data

### Available Wallets

| Wallet ID | Name | Balance | Spending Limit | Monthly Spent |
|-----------|------|---------|----------------|---------------|
| WALLET-12345 | John Doe | $1,250.00 | $500.00 | $342.50 |
| WALLET-67890 | Jane Smith | $2,500.00 | $1,000.00 | $678.25 |
| WALLET-11111 | Bob Johnson | $150.00 | $300.00 | $245.80 |
| WALLET-22222 | Alice Williams | $5,000.00 | $2,000.00 | $1,234.56 |
| WALLET-33333 | Demo User | $500.00 | $500.00 | $89.99 |

### Available Merchants

**Charging Networks:**
- EVgo (2.5% fee)
- ChargePoint (2.8% fee)
- Electrify America (2.3% fee)
- Tesla Supercharger (2.0% fee)

**Food Services:**
- Starbucks (3.0% fee)
- McDonald's (2.9% fee)
- Subway (2.9% fee)
- Chipotle (3.1% fee)

**Parking:**
- ParkMobile (3.5% fee)
- SpotHero (3.2% fee)
- ParkWhiz (3.3% fee)

**Other:**
- Amazon (2.9% fee)
- Walmart (2.5% fee)
- Target (2.7% fee)

---

## 🚦 Error Handling

### Common Errors

**Insufficient Funds:**
```python
{
    "success": False,
    "error": "insufficient_funds",
    "message": "Insufficient balance. Required: $25.21, Available: $10.00",
    "required": 25.21,
    "available": 10.00
}
```

**Payment Declined:**
```python
{
    "success": False,
    "error": "payment_declined",
    "message": "Payment was declined by the payment processor.",
    "retry_allowed": True
}
```

**Wallet Not Found:**
```python
{
    "valid": False,
    "error": "wallet_not_found",
    "message": "Wallet WALLET-99999 not found or invalid"
}
```

---

## 💡 Usage Examples

### Example 1: Simple Payment Flow
```python
from tools.payment_tools import validate_wallet, process_payment

# Step 1: Validate wallet
wallet = validate_wallet("WALLET-12345")

if wallet['valid'] and wallet['balance'] > 25:
    # Step 2: Process payment
    result = process_payment(
        amount=24.50,
        wallet_id="WALLET-12345",
        merchant="EVgo Charging",
        description="Fast charging"
    )
    
    if result['success']:
        print(f"✓ Payment successful: {result['transaction_id']}")
    else:
        print(f"✗ Payment failed: {result['message']}")
```

### Example 2: Batch Payment with Error Handling
```python
from tools.payment_tools import process_batch_payments

transactions = [
    {"amount": 24.50, "merchant": "EVgo", "description": "Charging"},
    {"amount": 6.75, "merchant": "Starbucks", "description": "Coffee"},
    {"amount": 12.00, "merchant": "ParkMobile", "description": "Parking"}
]

result = process_batch_payments(transactions, "WALLET-12345")

print(f"Processed: {result['successful_count']}/{result['total_transactions']}")
print(f"Total: ${result['total_amount']:.2f}")

if result['failed']:
    print("Failed transactions:")
    for failed in result['failed']:
        print(f"  - {failed['merchant']}: {failed['message']}")
```

### Example 3: Payment with Fee Calculation
```python
from tools.payment_tools import calculate_fees, process_payment

# Calculate fees first
fees = calculate_fees(24.50, "credit_card", "charging")
print(f"Amount: ${fees['amount']:.2f}")
print(f"Fee: ${fees['fee']:.2f}")
print(f"Total: ${fees['total']:.2f}")

# Confirm and process
result = process_payment(
    amount=fees['amount'],
    wallet_id="WALLET-12345",
    merchant="EVgo Charging",
    description="Charging session"
)
```

### Example 4: Transaction History with Filters
```python
from tools.payment_tools import get_payment_history

# Get charging transactions only
history = get_payment_history(
    wallet_id="WALLET-12345",
    limit=10,
    merchant="EVgo",
    status="completed"
)

print(f"Found {len(history)} charging transactions")
for txn in history:
    print(f"  {txn['timestamp']}: ${txn['amount']:.2f}")
```

---

## 🧪 Testing

**Run all tests:**
```bash
cd ev-concierge
python3 test_payment_tools.py
```

**Expected output:**
```
Total Tests: 11
✓ Passed: 11
✗ Failed: 0
Success Rate: 100.0%
```

---

## 📖 Additional Resources

- **Full Documentation:** `PHASE1_COMPLETE.md`
- **Implementation Plan:** `payment_agent_plan.md`
- **Test Suite:** `test_payment_tools.py`
- **Mock Data Generator:** `utils/mock_payment_data.py`

---

**Last Updated:** 2025-11-20  
**Version:** 1.0  
**Status:** ✅ Production Ready
