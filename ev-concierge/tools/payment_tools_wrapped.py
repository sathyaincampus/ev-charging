"""
Payment Tools Wrapper - Wraps payment-agent tools with Strands @Tool decorator
This allows the payment tools to work with the Strands SDK
"""

import sys
import os

# Add payment-agent to path
payment_agent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payment-agent')
sys.path.insert(0, payment_agent_path)

from strands import Tool

# Import the raw payment tools
from tools import payment_tools as pt


# Wrap each tool with the @Tool decorator
@Tool
def process_payment(amount: float, wallet_id: str, merchant: str, description: str, payment_method: str = "default") -> dict:
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
    return pt.process_payment(amount, wallet_id, merchant, description, payment_method)


@Tool
def validate_wallet(wallet_id: str) -> dict:
    """
    Validate wallet ID and return wallet details.
    
    Args:
        wallet_id: User's wallet identifier
    
    Returns:
        Wallet status, balance, available payment methods
    """
    return pt.validate_wallet(wallet_id)


@Tool
def get_wallet_balance(wallet_id: str) -> dict:
    """
    Get current wallet balance across all payment methods.
    
    Args:
        wallet_id: User's wallet identifier
    
    Returns:
        Total balance, breakdown by payment method
    """
    return pt.get_wallet_balance(wallet_id)


@Tool
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
    return pt.calculate_fees(amount, payment_method, merchant_type)


@Tool
def process_batch_payments(transactions: list, wallet_id: str) -> dict:
    """
    Process multiple payments in a single batch operation.
    
    Args:
        transactions: List of transaction dicts with amount, merchant, description
        wallet_id: User's wallet identifier
    
    Returns:
        Summary with successful/failed transactions
    """
    return pt.process_batch_payments(transactions, wallet_id)


@Tool
def initiate_refund(transaction_id: str, amount: float, reason: str) -> dict:
    """
    Initiate a refund for a previous transaction.
    
    Args:
        transaction_id: Original transaction ID
        amount: Refund amount
        reason: Refund reason
    
    Returns:
        Refund ID, status, estimated processing time
    """
    return pt.initiate_refund(transaction_id, amount, reason)


@Tool
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
    return pt.add_payment_method(wallet_id, method_type, details)


@Tool
def verify_transaction(transaction_id: str) -> dict:
    """
    Verify the status of a transaction.
    
    Args:
        transaction_id: Transaction ID to verify
    
    Returns:
        Current status, details, and any issues
    """
    return pt.verify_transaction(transaction_id)


@Tool
def generate_receipt(transaction_id: str) -> dict:
    """
    Generate a detailed receipt for a transaction.
    
    Args:
        transaction_id: Transaction ID
    
    Returns:
        Formatted receipt with all transaction details
    """
    return pt.generate_receipt(transaction_id)


@Tool
def get_payment_history(wallet_id: str, limit: int = 10, date_from: str = None, date_to: str = None, merchant: str = None, status: str = None) -> list:
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
    return pt.get_payment_history(wallet_id, limit, date_from, date_to, merchant, status)
