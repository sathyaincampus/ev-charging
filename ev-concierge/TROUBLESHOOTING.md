# Troubleshooting Guide

## Python 3.14 Compatibility Issues

If you encounter pyarrow build errors with Python 3.14, use one of these solutions:

### Solution 1: Use the provided installation script (Recommended)
```bash
cd ev-concierge
bash install_deps.sh
```

### Solution 2: Use Python 3.11 or 3.12
Python 3.14 is very new and some packages don't have pre-built wheels yet. Consider using Python 3.11 or 3.12:

```bash
# Using pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Or using conda
conda create -n ev-concierge python=3.12
conda activate ev-concierge
```

### Solution 3: Install without pyarrow
```bash
pip install boto3 python-dotenv pydantic requests
pip install --no-deps streamlit
pip install altair blinker cachetools click importlib-metadata numpy packaging pillow protobuf rich tenacity toml tornado typing-extensions tzlocal validators watchdog
```

## Gradio vs Streamlit Error

If you see `ModuleNotFoundError: No module named 'gradio'`, this means:
- The old `app.py` uses Gradio
- The new `app_streamlit.py` uses Streamlit
- Use `start_streamlit.sh` or the updated `start.sh` to run the Streamlit version

## AWS Credentials

Make sure your AWS credentials are configured:
```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

## Quick Start Commands

```bash
# Option 1: Use the main start script (now uses Streamlit)
cd ev-concierge
bash start.sh

# Option 2: Use the Streamlit-specific script
cd ev-concierge
bash start_streamlit.sh

# Option 3: Manual start
cd ev-concierge
source venv/bin/activate
bash install_deps.sh
streamlit run app_streamlit.py
```
