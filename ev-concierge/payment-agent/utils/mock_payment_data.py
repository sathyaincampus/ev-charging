"""
Mock Payment Data Generator
Generates realistic payment data for demo and testing purposes.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict


class MockPaymentData:
    """Generate realistic mock payment data for demo"""
    
    # Mock merchant data
    MERCHANTS = {
        "charging": [
            {"name": "EVgo", "fee_percent": 2.5},
            {"name": "ChargePoint", "fee_percent": 2.8},
            {"name": "Electrify America", "fee_percent": 2.3},
            {"name": "Tesla Supercharger", "fee_percent": 2.0},
        ],
        "food": [
            {"name": "Starbucks", "fee_percent": 3.0},
            {"name": "McDonald's", "fee_percent": 2.9},
            {"name": "Subway", "fee_percent": 2.9},
            {"name": "Chipotle", "fee_percent": 3.1},
        ],
        "parking": [
            {"name": "ParkMobile", "fee_percent": 3.5},
            {"name": "SpotHero", "fee_percent": 3.2},
            {"name": "ParkWhiz", "fee_percent": 3.3},
        ],
        "other": [
            {"name": "Amazon", "fee_percent": 2.9},
            {"name": "Walmart", "fee_percent": 2.5},
            {"name": "Target", "fee_percent": 2.7},
        ]
    }
    
    # Payment method types
    PAYMENT_METHODS = [
        {
            "type": "credit_card",
            "brand": "Visa",
            "fee_percent": 2.9,
            "fee_fixed": 0.30
        },
        {
            "type": "credit_card",
            "brand": "Mastercard",
            "fee_percent": 2.9,
            "fee_fixed": 0.30
        },
        {
            "type": "debit_card",
            "brand": "Visa Debit",
            "fee_percent": 1.5,
            "fee_fixed": 0.25
        },
        {
            "type": "apple_pay",
            "brand": "Apple Pay",
            "fee_percent": 2.5,
            "fee_fixed": 0.20
        },
        {
            "type": "google_pay",
            "brand": "Google Pay",
            "fee_percent": 2.5,
            "fee_fixed": 0.20
        }
    ]
    
    # Wallet profiles
    WALLET_PROFILES = {
        "WALLET-12345": {
            "name": "John Doe",
            "balance": 1250.00,
            "spending_limit": 500.00,
            "monthly_spent": 342.50
        },
        "WALLET-67890": {
            "name": "Jane Smith",
            "balance": 2500.00,
            "spending_limit": 1000.00,
            "monthly_spent": 678.25
        },
        "WALLET-11111": {
            "name": "Bob Johnson",
            "balance": 150.00,
            "spending_limit": 300.00,
            "monthly_spent": 245.80
        },
        "WALLET-22222": {
            "name": "Alice Williams",
            "balance": 5000.00,
            "spending_limit": 2000.00,
            "monthly_spent": 1234.56
        },
        "WALLET-33333": {
            "name": "Demo User",
            "balance": 500.00,
            "spending_limit": 500.00,
            "monthly_spent": 89.99
        }
    }
    
    @staticmethod
    def generate_wallet(wallet_id: str) -> Dict:
        """Generate mock wallet with balance and payment methods"""
        
        # Get profile or create default
        profile = MockPaymentData.WALLET_PROFILES.get(
            wallet_id,
            {
                "name": "Default User",
                "balance": 1000.00,
                "spending_limit": 500.00,
                "monthly_spent": 0.00
            }
        )
        
        # Generate payment methods
        payment_methods = []
        for i, method_template in enumerate(MockPaymentData.PAYMENT_METHODS[:3]):
            payment_methods.append({
                "id": f"PM-{wallet_id.split('-')[1]}-{i+1:03d}",
                "type": method_template["type"],
                "brand": method_template["brand"],
                "last4": str(random.randint(1000, 9999)),
                "default": i == 0,
                "balance": profile["balance"] if i == 0 else random.randint(1000, 10000),
                "fee_percent": method_template["fee_percent"],
                "fee_fixed": method_template["fee_fixed"]
            })
        
        return {
            "wallet_id": wallet_id,
            "name": profile["name"],
            "balance": profile["balance"],
            "currency": "USD",
            "payment_methods": payment_methods,
            "spending_limit": profile["spending_limit"],
            "monthly_spent": profile["monthly_spent"],
            "status": "active",
            "created_at": (datetime.now() - timedelta(days=365)).isoformat()
        }
    
    @staticmethod
    def generate_transaction_history(wallet_id: str, count: int = 20) -> List[Dict]:
        """Generate realistic transaction history"""
        transactions = []
        
        for i in range(count):
            # Random merchant type and merchant
            merchant_type = random.choice(list(MockPaymentData.MERCHANTS.keys()))
            merchant = random.choice(MockPaymentData.MERCHANTS[merchant_type])
            
            # Random amount based on merchant type
            if merchant_type == "charging":
                amount = round(random.uniform(15.0, 45.0), 2)
            elif merchant_type == "food":
                amount = round(random.uniform(5.0, 25.0), 2)
            elif merchant_type == "parking":
                amount = round(random.uniform(8.0, 30.0), 2)
            else:
                amount = round(random.uniform(10.0, 100.0), 2)
            
            # Calculate fee
            fee = round(amount * (merchant["fee_percent"] / 100) + 0.30, 2)
            total = round(amount + fee, 2)
            
            # Random timestamp in the past 30 days
            days_ago = random.randint(0, 30)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Random status (mostly completed)
            status = random.choices(
                ["completed", "pending", "failed", "refunded"],
                weights=[85, 5, 5, 5]
            )[0]
            
            transaction = {
                "transaction_id": f"TXN-{int(timestamp.timestamp())}-{i:03d}",
                "wallet_id": wallet_id,
                "amount": amount,
                "fee": fee,
                "total": total,
                "merchant": merchant["name"],
                "merchant_type": merchant_type,
                "description": MockPaymentData._generate_description(merchant["name"], merchant_type),
                "payment_method": f"PM-{wallet_id.split('-')[1]}-001",
                "status": status,
                "timestamp": timestamp.isoformat(),
                "receipt_url": f"https://receipts.example.com/TXN-{int(timestamp.timestamp())}-{i:03d}"
            }
            
            transactions.append(transaction)
        
        # Sort by timestamp descending (newest first)
        transactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return transactions
    
    @staticmethod
    def _generate_description(merchant: str, merchant_type: str) -> str:
        """Generate realistic transaction description"""
        descriptions = {
            "charging": [
                "Fast charging session",
                "DC fast charge",
                "Level 2 charging",
                "Supercharger session"
            ],
            "food": [
                "Coffee and pastry",
                "Lunch order",
                "Breakfast meal",
                "Snack and drink"
            ],
            "parking": [
                "2 hour parking",
                "Daily parking",
                "Overnight parking",
                "Hourly parking"
            ],
            "other": [
                "Online purchase",
                "In-store purchase",
                "Subscription payment",
                "Service fee"
            ]
        }
        
        desc = random.choice(descriptions.get(merchant_type, descriptions["other"]))
        return f"{desc} at {merchant}"
    
    @staticmethod
    def generate_merchants() -> List[Dict]:
        """Generate list of all mock merchants"""
        all_merchants = []
        for merchant_type, merchants in MockPaymentData.MERCHANTS.items():
            for merchant in merchants:
                all_merchants.append({
                    "name": merchant["name"],
                    "type": merchant_type,
                    "fee_percent": merchant["fee_percent"]
                })
        return all_merchants
    
    @staticmethod
    def generate_payment_methods() -> List[Dict]:
        """Generate mock payment methods"""
        return MockPaymentData.PAYMENT_METHODS.copy()
    
    @staticmethod
    def calculate_realistic_fees(amount: float, method_type: str) -> float:
        """Calculate realistic transaction fees"""
        # Find fee structure for method type
        for method in MockPaymentData.PAYMENT_METHODS:
            if method["type"] == method_type:
                fee = (amount * method["fee_percent"] / 100) + method["fee_fixed"]
                return round(fee, 2)
        
        # Default fee structure
        return round((amount * 2.9 / 100) + 0.30, 2)
    
    @staticmethod
    def get_random_wallet_id() -> str:
        """Get a random wallet ID from profiles"""
        return random.choice(list(MockPaymentData.WALLET_PROFILES.keys()))
    
    @staticmethod
    def simulate_processing_delay() -> float:
        """Get realistic processing delay in seconds"""
        return round(random.uniform(1.5, 3.0), 2)
