import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
USE_MOCK_DATA = os.getenv('USE_MOCK_DATA', 'true').lower() == 'true'

# API Keys
EVGO_API_KEY = os.getenv('EVGO_API_KEY')
CHARGEPOINT_API_KEY = os.getenv('CHARGEPOINT_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
OPENCHARGEMAP_API_KEY = os.getenv('OPENCHARGEMAP_API_KEY', '')

# OpenChargeMap Configuration
OPENCHARGEMAP_BASE_URL = 'https://api.openchargemap.io/v3'
