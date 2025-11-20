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
        print("\n" + "="*70)
        print("💳 PAYMENT AGENT CALLED")
        print("="*70)
        print(f"📋 Transactions to process: {len(transactions)}")
        for i, txn in enumerate(transactions, 1):
            print(f"   {i}. ${txn.get('amount', 0):.2f} to {txn.get('merchant', 'Unknown')}")
        print(f"👛 Wallet ID: {wallet_id}")
        print("="*70 + "\n")
        
        if not transactions:
            print("⚠️  No transactions to process\n")
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
        
        print("🔧 Payment tools available:")
        for tool in available_tools:
            print(f"   - {tool.name}")
        print()
        
        response = self.strands.run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=available_tools,
            max_iterations=10
        )
        
        # Log the results
        print("\n" + "="*70)
        print("💳 PAYMENT AGENT RESULTS")
        print("="*70)
        print(f"🔧 Tools called: {len(response.tool_calls)}")
        
        total_charged = 0
        payment_count = 0
        
        for call in response.tool_calls:
            print(f"\n   📞 {call.tool_name}:")
            
            # Extract payment info from results
            if call.tool_name == 'process_batch_payments' and isinstance(call.result, dict):
                successful = call.result.get('successful', [])
                failed = call.result.get('failed', [])
                
                print(f"      ✅ Successful: {len(successful)}")
                print(f"      ❌ Failed: {len(failed)}")
                
                for payment in successful:
                    if isinstance(payment, dict):
                        amount = payment.get('amount', 0)
                        merchant = payment.get('merchant', 'Unknown')
                        txn_id = payment.get('transaction_id', 'N/A')
                        total_charged += amount
                        payment_count += 1
                        print(f"         💰 ${amount:.2f} to {merchant} ({txn_id})")
            
            elif call.tool_name == 'validate_wallet' and isinstance(call.result, dict):
                valid = call.result.get('valid', False)
                balance = call.result.get('balance', 0)
                print(f"      Valid: {valid}, Balance: ${balance:.2f}")
            
            elif call.tool_name == 'calculate_fees' and isinstance(call.result, dict):
                amount = call.result.get('amount', 0)
                fee = call.result.get('fee', 0)
                total = call.result.get('total', 0)
                print(f"      Amount: ${amount:.2f}, Fee: ${fee:.2f}, Total: ${total:.2f}")
            
            elif call.tool_name == 'generate_receipt' and isinstance(call.result, dict):
                receipt_id = call.result.get('receipt_id', 'N/A')
                print(f"      Receipt: {receipt_id}")
        
        print(f"\n💵 TOTAL CHARGED: ${total_charged:.2f}")
        print(f"📊 PAYMENTS PROCESSED: {payment_count}")
        print("="*70 + "\n")
        
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
