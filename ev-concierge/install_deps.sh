#!/bin/bash

echo "📦 Installing EV Concierge dependencies..."

# Install core dependencies first
pip install boto3>=1.34.0 python-dotenv>=1.0.0 pydantic>=2.0.0 requests>=2.31.0

# Try to install streamlit
echo "📥 Installing Streamlit..."
if pip install streamlit>=1.28.0; then
    echo "✅ Streamlit installed successfully"
else
    echo "⚠️  Standard installation failed, trying without pyarrow..."
    # Install streamlit without pyarrow dependency
    pip install --no-deps streamlit>=1.28.0
    # Install streamlit's other dependencies manually
    pip install altair blinker cachetools click importlib-metadata \
                numpy packaging pillow protobuf pyarrow-hotfix \
                rich tenacity toml tornado typing-extensions \
                tzlocal validators watchdog
fi

echo "✅ Dependencies installed!"
