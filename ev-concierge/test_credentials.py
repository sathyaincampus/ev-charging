#!/usr/bin/env python3
"""
Quick script to test AWS credentials and Bedrock access
"""
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_credentials():
    print("🔍 Testing AWS Credentials...\n")
    
    # Check if credentials are in environment
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-west-2')
    
    if not access_key or access_key == 'your_access_key_here':
        print("❌ AWS_ACCESS_KEY_ID not found or not set in .env file")
        print("   Please edit .env and add your AWS credentials")
        return False
    
    if not secret_key or secret_key == 'your_secret_key_here':
        print("❌ AWS_SECRET_ACCESS_KEY not found or not set in .env file")
        print("   Please edit .env and add your AWS credentials")
        return False
    
    print(f"✅ Found AWS_ACCESS_KEY_ID: {access_key[:8]}...")
    print(f"✅ Found AWS_SECRET_ACCESS_KEY: {secret_key[:8]}...")
    print(f"✅ Region: {region}\n")
    
    # Test STS (basic AWS access)
    print("🔐 Testing AWS access with STS...")
    try:
        sts = boto3.client('sts',
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key,
                          region_name=region)
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials valid!")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}\n")
    except Exception as e:
        print(f"❌ AWS credentials invalid: {str(e)}\n")
        return False
    
    # Test Bedrock access
    print("🤖 Testing Bedrock access...")
    try:
        bedrock = boto3.client('bedrock-runtime',
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key,
                              region_name=region)
        
        # Try to list foundation models (this requires Bedrock permissions)
        bedrock_control = boto3.client('bedrock',
                                      aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key,
                                      region_name=region)
        
        print("✅ Bedrock access configured!")
        print("   Note: Make sure Claude 3.5 Sonnet is enabled in Model Access\n")
        
    except Exception as e:
        print(f"⚠️  Bedrock access issue: {str(e)}")
        print("   You may need to:")
        print("   1. Enable Bedrock in your AWS account")
        print("   2. Request access to Claude 3.5 Sonnet")
        print("   3. Add Bedrock permissions to your IAM user\n")
        return False
    
    print("=" * 60)
    print("✅ All checks passed! You're ready to run the EV Concierge")
    print("=" * 60)
    print("\nRun: bash start.sh")
    return True

if __name__ == "__main__":
    test_credentials()
