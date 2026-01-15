# Quick script to update stock prices with real-time data
# Run this anytime to refresh all stock and options prices

Write-Host "🔄 Fetching real-time stock prices from Yahoo Finance..." -ForegroundColor Cyan

docker exec trading_inference_api python realtime_price_fetcher.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Success! All prices updated with live market data" -ForegroundColor Green
    Write-Host "🌐 View at: http://localhost:3000" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Error updating prices. Check the logs above." -ForegroundColor Red
}
