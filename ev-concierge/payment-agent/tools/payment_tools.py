"""
Payment Tools - Enhanced with 10+ tools for comprehensive payment operations
Supports mock mode for demo and real API integration for production
"""

import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.mock_payment_data import MockPaymentData


def process_payment(
    amount: float,
    wallet_id: str,
    merchant: str,
    description: str,
    payment_method: str = "default"
) -> dict:
    """
    Process a single payment transaction.
    
    Args:
        amount: Payment amount in USD
        wallet_id: User's wallet identifier
        merchant: Merchant name/ID
        description: Transaction description
        payment_method: Specific payment method ID or "default"
    
    Returns:
        Transaction details with ID, status, timestamp, receipt
    """
    # Simulate processing delay
    time.sleep(MockPaymentData.simulate_processing_delay())
    
    # Get wallet to validate
    wallet = MockPaymentData.generate_wallet(wallet_id)
    
    # Select payment method
    if payment_method == "default":
        pm = next((m for m in wallet["payment_methods"] if m["default"]), wallet["payment_methods"][0])
    else:
        pm = next((m for m in wallet["payment_methods"] if m["id"] == payment_method), wallet["payment_methods"][0])
    
    # Calculate fees
    fee = round((amount * pm["fee_percent"] / 100) + pm["fee_fixed"], 2)
    total = round(amount + fee, 2)
    
    # Check balance
    if wallet["balance"] < total:
        return {
            "success": False,
            "error": "insufficient_funds",
            "message": f"Insufficient balance. Required: ${total:.2f}, Available: ${wallet['balance']:.2f}",
            "required": total,
            "available": wallet["balance"]
        }
    
    # Generate transaction
    transaction_id = f"TXN-{int(datetime.now().timestamp())}"
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "amount": amount,
        "fee": fee,
        "total": total,
        "wallet_id": wallet_id,
        "merchant": merchant,
        "description": description,
        "payment_method": pm["id"],
        "payment_method_type": pm["type"],
        "payment_method_brand": pm["brand"],
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "receipt_url": f"https://receipts.example.com/{transaction_id}",
        "message": f"Payment of ${amount:.2f} to {merchant} completed successfully"
    }


def validate_wallet(wallet_id: str) -> dict:
    """
    Validate wallet ID and return wallet details.
    
    Args:
        wallet_id: User's wallet identifier
    
    Returns:
        Wallet status, balance, available payment methods
    """
    try:
        wallet = MockPaymentData.generate_wallet(wallet_id)
        
        return {
            "valid": True,
            "wallet_id": wallet_id,
            "name": wallet["name"],
            "balance": wallet["balance"],
            "currency": wallet["currency"],
            "status": wallet["status"],
            "payment_methods_count": len(wallet["payment_methods"]),
            "payment_methods": wallet["payment_methods"],
            "spending_limit": wallet["spending_limit"],
            "monthly_spent": wallet["monthly_spent"],
            "remaining_limit": wallet["spending_limit"] - wallet["monthly_spent"],
            "message": f"Wallet {wallet_id} is valid and active"
        }
    except Exception as e:
        return {
            "valid": False,
            "wallet_id": wallet_id,
            "error": "wallet_not_found",
            "message": f"Wallet {wallet_id} not found or invalid"
        }


def get_wallet_balance(wallet_id: str) -> dict:
    """
    Get current wallet balance across all payment methods.
    
    Args:
        wallet_id: User's wallet identifier
    
    Returns:
        Total balance, breakdown by payment method
    """
    wallet = MockPaymentData.generate_wallet(wallet_id)
    
    # Calculate total balance across all payment methods
    total_balance = sum(pm["balance"] for pm in wallet["payment_methods"])
    
    return {
        "wallet_id": wallet_id,
        "primary_balance": wallet["balance"],
        "total_balance": total_balance,
        "currency": wallet["currency"],
        "payment_methods": [
            {
                "id": pm["id"],
                "type": pm["type"],
                "brand": pm["brand"],
                "last4": pm["last4"],
                "balance": pm["balance"],
                "default": pm["default"]
            }
            for pm in wallet["payment_methods"]
        ],
        "message": f"Total available balance: ${total_balance:.2f}"
    }


def calculate_fees(amount: float, payment_method: str, merchant_type: str = "general") -> dict:
    """
    Calculate transaction fees based on amount and payment method.
    
    Args:
        amount: Transaction amount
        payment_method: Payment method type (credit_card, debit_card, apple_pay, etc.)
        merchant_type: Type of merchant (charging, food, parking, etc.)
    
    Returns:
        Fee amount, percentage, total with fees
    """
    fee = MockPaymentData.calculate_realistic_fees(amount, payment_method)
    total = round(amount + fee, 2)
    fee_percent = round((fee / amount) * 100, 2) if amount > 0 else 0
    
    return {
        "amount": amount,
        "fee": fee,
        "fee_percent": fee_percent,
        "total": total,
        "payment_method": payment_method,
        "merchant_type": merchant_type,
        "breakdown": {
            "base_amount": amount,
            "processing_fee": fee,
            "total": total
        },
        "message": f"Total with fees: ${total:.2f} (fee: ${fee:.2f})"
    }


def process_batch_payments(transactions: List[dict], wallet_id: str) -> dict:
    """
    Process multiple payments in a single batch operation.
    
    Args:
        transactions: List of transaction dicts with amount, merchant, description
        wallet_id: User's wallet identifier
    
    Returns:
        Summary with successful/failed transactions
    """
    # Simulate batch processing delay
    time.sleep(2.0)
    
    successful = []
    failed = []
    total_amount = 0
    
    for txn in transactions:
        result = process_payment(
            amount=txn.get("amount", 0),
            wallet_id=wallet_id,
            merchant=txn.get("merchant", "Unknown"),
            description=txn.get("description", ""),
            payment_method=txn.get("payment_method", "default")
        )
        
        if result.get("success"):
            successful.append(result)
            total_amount += result["amount"]
        else:
            failed.append({
                "merchant": txn.get("merchant"),
                "amount": txn.get("amount"),
                "error": result.get("error"),
                "message": result.get("message")
            })
    
    return {
        "success": len(failed) == 0,
        "total_transactions": len(transactions),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "total_amount": round(total_amount, 2),
        "successful": successful,
        "failed": failed,
        "message": f"Processed {len(successful)}/{len(transactions)} transactions successfully. Total: ${total_amount:.2f}"
    }


def initiate_refund(transaction_id: str, amount: float, reason: str) -> dict:
    """
    Initiate a refund for a previous transaction.
    
    Args:
        transaction_id: Original transaction ID
        amount: Refund amount (None for full refund)
        reason: Refund reason
    
    Returns:
        Refund ID, status, estimated processing time
    """
    # Simulate processing delay
    time.sleep(1.5)
    
    refund_id = f"RFD-{int(datetime.now().timestamp())}"
    estimated_days = random.randint(3, 7)
    
    return {
        "success": True,
        "refund_id": refund_id,
        "transaction_id": transaction_id,
        "amount": amount,
        "reason": reason,
        "status": "pending",
        "estimated_days": estimated_days,
        "estimated_date": (datetime.now() + timedelta(days=estimated_days)).strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "message": f"Refund of ${amount:.2f} initiated. Expected in {estimated_days} business days."
    }


def add_payment_method(wallet_id: str, method_type: str, details: dict) -> dict:
    """
    Add a new payment method to wallet.
    
    Args:
        wallet_id: User's wallet identifier
        method_type: Type of payment method (credit_card, debit_card, etc.)
        details: Payment method details (card number, expiry, etc.)
    
    Returns:
        Payment method ID and confirmation
    """
    # Simulate processing delay
    time.sleep(1.0)
    
    wallet = MockPaymentData.generate_wallet(wallet_id)
    new_pm_id = f"PM-{wallet_id.split('-')[1]}-{len(wallet['payment_methods']) + 1:03d}"
    
    return {
        "success": True,
        "payment_method_id": new_pm_id,
        "wallet_id": wallet_id,
        "type": method_type,
        "brand": details.get("brand", "Unknown"),
        "last4": details.get("last4", "****"),
        "status": "active",
        "default": False,
        "timestamp": datetime.now().isoformat(),
        "message": f"Payment method {method_type} added successfully"
    }


def verify_transaction(transaction_id: str) -> dict:
    """
    Verify the status of a transaction.
    
    Args:
        transaction_id: Transaction ID to verify
    
    Returns:
        Current status, details, and any issues
    """
    # Simulate verification delay
    time.sleep(0.5)
    
    # Simulate different statuses
    status = random.choices(
        ["completed", "pending", "failed", "refunded"],
        weights=[80, 10, 5, 5]
    )[0]
    
    result = {
        "transaction_id": transaction_id,
        "status": status,
        "verified": True,
        "timestamp": datetime.now().isoformat()
    }
    
    if status == "completed":
        result["message"] = "Transaction completed successfully"
    elif status == "pending":
        result["message"] = "Transaction is still processing"
    elif status == "failed":
        result["message"] = "Transaction failed"
        result["error"] = "payment_declined"
    elif status == "refunded":
        result["message"] = "Transaction has been refunded"
        result["refund_id"] = f"RFD-{int(datetime.now().timestamp())}"
    
    return result


def generate_receipt(transaction_id: str) -> dict:
    """
    Generate a detailed receipt for a transaction.
    
    Args:
        transaction_id: Transaction ID
    
    Returns:
        Formatted receipt with all transaction details
    """
    # Simulate receipt generation
    time.sleep(0.3)
    
    # Note: In mock mode, we return a generic receipt since we don't have
    # a transaction database. The actual transaction details are in the
    # payment result, not the receipt.
    receipt = {
        "receipt_id": f"RCP-{transaction_id}",
        "transaction_id": transaction_id,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Generated",
        "receipt_url": f"https://receipts.example.com/{transaction_id}",
        "message": "Receipt generated successfully. See transaction details for payment information."
    }
    
    return receipt


def get_payment_history(
    wallet_id: str,
    limit: int = 10,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    merchant: Optional[str] = None,
    status: Optional[str] = None
) -> list:
    """
    Get payment history for a wallet with optional filters.
    
    Args:
        wallet_id: User's wallet identifier
        limit: Number of transactions to return
        date_from: Filter transactions from this date (ISO format)
        date_to: Filter transactions to this date (ISO format)
        merchant: Filter by merchant name
        status: Filter by status (completed, pending, failed, refunded)
    
    Returns:
        List of transactions with details
    """
    # Generate transaction history
    all_transactions = MockPaymentData.generate_transaction_history(wallet_id, count=50)
    
    # Apply filters
    filtered = all_transactions
    
    if date_from:
        filtered = [t for t in filtered if t["timestamp"] >= date_from]
    
    if date_to:
        filtered = [t for t in filtered if t["timestamp"] <= date_to]
    
    if merchant:
        filtered = [t for t in filtered if merchant.lower() in t["merchant"].lower()]
    
    if status:
        filtered = [t for t in filtered if t["status"] == status]
    
    # Apply limit
    filtered = filtered[:limit]
    
    return filtered
