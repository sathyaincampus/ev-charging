"""
Payment Agent - Integrated with Phase 1 Payment Tools
Uses the isolated payment-agent tools for all payment operations
"""

import sys
import os

# Add payment-agent to path for direct tool access
payment_agent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payment-agent')
sys.path.insert(0, payment_agent_path)

from strands import Strands
from utils.config import AWS_REGION, BEDROCK_MODEL_ID

# Import wrapped tools for Strands (with @Tool decorator)
from tools.payment_tools_wrapped import (
    process_payment as process_payment_tool,
    validate_wallet as validate_wallet_tool,
    get_wallet_balance as get_wallet_balance_tool,
    calculate_fees as calculate_fees_tool,
    process_batch_payments as process_batch_payments_tool,
    initiate_refund as initiate_refund_tool,
    add_payment_method as add_payment_method_tool,
    verify_transaction as verify_transaction_tool,
    generate_receipt as generate_receipt_tool,
    get_payment_history as get_payment_history_tool
)

# Import raw tools for direct method calls (without Strands)
from tools import payment_tools as pt


class PaymentAgent:
    """
    Payment Agent integrated with Phase 1 payment tools.
    Provides payment processing capabilities to the coordinator and other agents.
    """
    
    def __init__(self):
        self.strands = Strands(
            model_id=BEDROCK_MODEL_ID,
            region=AWS_REGION
        )
    
    def process_payments(self, transactions: list, wallet_id: str) -> dict:
        """
        Process multiple payment transactions.
        
        Args:
            transactions: List of transaction dicts with amount, merchant, description
            wallet_id: User's wallet identifier
            
        Returns:
            Dict with payment results and tool call details
        """
        if not transactions:
            return {"payments": None, "message": "No payments to process", "tool_results": []}
        
        system_prompt = """You are a payment specialist. Process all transactions securely 
and provide a summary. Use the available payment tools to:
1. Validate the wallet first
2. Calculate fees for transparency
3. Process payments (batch or individual)
4. Generate receipts
5. Provide a clear summary of all transactions"""
        
        user_prompt = f"""
Transactions to process: {transactions}
Wallet ID: {wallet_id}

Process all payments and provide confirmation with transaction IDs."""
        
        # Provide all relevant tools to the agent (wrapped with @Tool decorator)
        available_tools = [
            validate_wallet_tool,
            calculate_fees_tool,
            process_payment_tool,
            process_batch_payments_tool,
            generate_receipt_tool,
            get_payment_history_tool
        ]
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=available_tools,
            max_iterations=10
        )
        
        return {
            "payments": response.final_response,
            "tool_results": [c.result for c in response.tool_calls] if response.tool_calls else []
        }
    
    def process_single_payment(self, amount: float, merchant: str, wallet_id: str, 
                              description: str = "") -> dict:
        """
        Process a single payment transaction.
        
        Args:
            amount: Payment amount in USD
            merchant: Merchant name
            wallet_id: User's wallet identifier
            description: Transaction description
            
        Returns:
            Payment result with transaction details
        """
        result = pt.process_payment(
            amount=amount,
            wallet_id=wallet_id,
            merchant=merchant,
            description=description
        )
        
        return {
            "payments": f"Payment of ${amount:.2f} to {merchant} " + 
                       ("completed successfully" if result.get('success') else "failed"),
            "tool_results": [result]
        }
    
    def validate_user_wallet(self, wallet_id: str) -> dict:
        """
        Validate a user's wallet.
        
        Args:
            wallet_id: User's wallet identifier
            
        Returns:
            Wallet validation result
        """
        result = pt.validate_wallet(wallet_id)
        return {
            "valid": result.get('valid', False),
            "balance": result.get('balance', 0),
            "message": result.get('message', ''),
            "tool_results": [result]
        }
    
    def get_transaction_history(self, wallet_id: str, limit: int = 10) -> dict:
        """
        Get transaction history for a wallet.
        
        Args:
            wallet_id: User's wallet identifier
            limit: Number of transactions to retrieve
            
        Returns:
            Transaction history
        """
        transactions = pt.get_payment_history(wallet_id, limit=limit)
        
        return {
            "transactions": transactions,
            "count": len(transactions),
            "tool_results": transactions
        }
    
    def request_refund(self, transaction_id: str, reason: str, amount: float = None) -> dict:
        """
        Initiate a refund for a transaction.
        
        Args:
            transaction_id: Original transaction ID
            reason: Refund reason
            amount: Refund amount (None for full refund)
            
        Returns:
            Refund result
        """
        result = pt.initiate_refund(
            transaction_id=transaction_id,
            amount=amount or 0,  # Will be determined by the tool
            reason=reason
        )
        
        return {
            "refund": result.get('success', False),
            "refund_id": result.get('refund_id', ''),
            "message": result.get('message', ''),
            "tool_results": [result]
        }
