#!/bin/bash

echo "=========================================="
echo "🚗 EV Concierge - OpenChargeMap Demo"
echo "=========================================="
echo ""
echo "✅ OpenChargeMap API Key: Configured"
echo "✅ USE_MOCK_DATA: false (using real data)"
echo ""
echo "Starting Streamlit app..."
echo ""
echo "📍 Try these routes to see real charging stations:"
echo "   • Los Angeles → San Francisco (380 miles)"
echo "   • Los Angeles → San Diego (120 miles)"
echo "   • San Francisco → Seattle (800 miles)"
echo ""
echo "🎯 Set battery to 30-40% to trigger charging search"
echo ""

streamlit run app_streamlit.py
