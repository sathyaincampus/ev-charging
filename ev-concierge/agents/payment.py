"""
Payment Agent - Integrated with Phase 1 Payment Tools
Uses the isolated payment-agent tools for all payment operations
"""

import sys
import os
import json
import asyncio

# Add payment-agent to path for direct tool access
payment_agent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'payment-agent')
sys.path.insert(0, payment_agent_path)

from strands.models import BedrockModel
from strands import Agent
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

# Import raw tools for direct method calls (without Strands) using absolute path
import importlib.util
payment_tools_path = os.path.join(payment_agent_path, 'tools', 'payment_tools.py')
spec = importlib.util.spec_from_file_location("payment_tools_raw", payment_tools_path)
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


class PaymentAgent:
    """
    Payment Agent integrated with Phase 1 payment tools.
    Provides payment processing capabilities to the coordinator and other agents.
    """
    
    def __init__(self):
        self.model = BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
            temperature=0.7
        )
    
    def process_payments(self, transactions: list, wallet_id: str) -> dict:
        """Synchronous wrapper for async process_payments"""
        if not transactions:
            print("⚠️  No transactions to process\n")
            return {"payments": None, "message": "No payments to process", "tool_results": []}
        
        return asyncio.run(self.process_payments_async(transactions, wallet_id))
    
    async def process_payments_async(self, transactions: list, wallet_id: str) -> dict:
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
            # Get tool name from function name or __name__
            tool_name = getattr(tool, '__name__', str(tool))
            print(f"   - {tool_name}")
        print()
        
        # Create agent with tools
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=available_tools
        )
        
        # Stream response and collect results
        response_text = ""
        tool_results = []
        
        print(f"💳 Payment Agent: Starting Bedrock API stream...")
        
        try:
            async for event in agent.stream_async(user_prompt):
                if isinstance(event, dict):
                    if 'data' in event:
                        response_text += str(event['data'])
                    
                    # Extract tool results from message
                    if 'message' in event:
                        message = event['message']
                        if isinstance(message, dict) and 'content' in message:
                            for content_block in message['content']:
                                if isinstance(content_block, dict) and 'toolResult' in content_block:
                                    tool_result = content_block['toolResult']
                                    if 'content' in tool_result:
                                        for content_item in tool_result['content']:
                                            if 'text' in content_item:
                                                try:
                                                    result_json = json.loads(content_item['text'])
                                                    tool_results.append(result_json)
                                                except:
                                                    pass
        except Exception as e:
            print(f"❌ Payment Agent Error: {e}")
            import traceback
            traceback.print_exc()
            response_text = f"Error: {str(e)}"
        
        # Log the results
        print("\n" + "="*70)
        print("💳 PAYMENT AGENT RESULTS")
        print("="*70)
        print(f"🔧 Tools called: {len(tool_results)}")
        
        total_charged = 0
        payment_count = 0
        
        for result in tool_results:
            if isinstance(result, dict):
                # Check for batch payment results
                if 'successful' in result:
                    successful = result.get('successful', [])
                    failed = result.get('failed', [])
                    
                    print(f"\n   📞 process_batch_payments:")
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
                
                # Check for wallet validation
                elif 'valid' in result and 'balance' in result:
                    print(f"\n   📞 validate_wallet:")
                    print(f"      Valid: {result.get('valid')}, Balance: ${result.get('balance', 0):.2f}")
                
                # Check for fee calculation
                elif 'fee' in result and 'total' in result:
                    print(f"\n   📞 calculate_fees:")
                    print(f"      Amount: ${result.get('amount', 0):.2f}, Fee: ${result.get('fee', 0):.2f}, Total: ${result.get('total', 0):.2f}")
                
                # Check for receipt
                elif 'receipt_id' in result:
                    print(f"\n   📞 generate_receipt:")
                    print(f"      Receipt: {result.get('receipt_id')}")
        
        print(f"\n💵 TOTAL CHARGED: ${total_charged:.2f}")
        print(f"📊 PAYMENTS PROCESSED: {payment_count}")
        print("="*70 + "\n")
        
        return {
            "payments": response_text,
            "tool_results": tool_results
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
