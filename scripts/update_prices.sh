#!/bin/bash
# Quick script to update stock prices with real-time data
# Run this anytime to refresh all stock and options prices

echo "🔄 Fetching real-time stock prices from Yahoo Finance..."
docker exec trading_inference_api python realtime_price_fetcher.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! All prices updated with live market data"
    echo "🌐 View at: http://localhost:3000"
else
    echo ""
    echo "❌ Error updating prices. Check the logs above."
fi
