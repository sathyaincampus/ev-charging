#!/bin/bash

echo "🔄 AWS Credentials Refresh Helper"
echo "=================================="
echo ""

# Check if root .env exists
if [ -f "../.env" ]; then
    echo "📋 Found credentials in root .env file"
    echo "   Copying to ev-concierge/.env..."
    
    # Extract AWS credentials from root .env
    AWS_ACCESS_KEY_ID=$(grep "^AWS_ACCESS_KEY_ID=" ../.env | cut -d '=' -f2- | tr -d '"')
    AWS_SECRET_ACCESS_KEY=$(grep "^AWS_SECRET_ACCESS_KEY=" ../.env | cut -d '=' -f2- | tr -d '"')
    AWS_SESSION_TOKEN=$(grep "^AWS_SESSION_TOKEN=" ../.env | cut -d '=' -f2- | tr -d '"')
    AWS_REGION=$(grep "^AWS.*REGION=" ../.env | cut -d '=' -f2- | tr -d '"')
    
    if [ -z "$AWS_REGION" ]; then
        AWS_REGION="us-west-2"
    fi
    
    # Update local .env
    cat > .env << EOF
# AWS Credentials (Auto-synced from root .env)
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
EOF
    
    if [ ! -z "$AWS_SESSION_TOKEN" ]; then
        echo "AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN" >> .env
    fi
    
    cat >> .env << EOF
AWS_REGION=$AWS_REGION
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Charging Networks (Optional - uses mocks if not provided)
EVGO_API_KEY=
CHARGEPOINT_API_KEY=
ELECTRIFY_AMERICA_API_KEY=
TESLA_API_KEY=

# Food & Amenities (Optional)
STARBUCKS_API_KEY=
UBEREATS_API_KEY=

# Payment (Optional)
STRIPE_API_KEY=

# Maps & Weather (Optional)
GOOGLE_MAPS_API_KEY=
OPENWEATHER_API_KEY=

# Demo Mode (set to true to use mock data)
USE_MOCK_DATA=true
EOF
    
    echo "✅ Credentials synced!"
    echo ""
    
    # Test credentials
    if command -v python3 &> /dev/null; then
        echo "🧪 Testing credentials..."
        python3 test_credentials.py
    fi
else
    echo "⚠️  Root .env file not found"
    echo ""
    echo "Please either:"
    echo "1. Run 'aws configure' to set up AWS CLI credentials"
    echo "2. Manually edit ev-concierge/.env with your AWS credentials"
    echo ""
    echo "See AWS_SETUP.md for detailed instructions"
fi
