# Real-Time Stock Price Updates

## 🎯 Overview
The application now fetches **real-time stock prices from Yahoo Finance** instead of using hardcoded values. All stock prices, options strikes, premiums, and targets are automatically recalculated based on live market data.

## ✅ What Was Updated

### Real-Time Data Source
- **Source**: Yahoo Finance API (via yfinance library)
- **Coverage**: All 54 stock symbols in the database
- **Data Fetched**: Current closing prices, updated multiple times per day
- **No API Key Required**: Free access to Yahoo Finance data

### Automatic Calculations
When prices are updated, the system automatically:
1. ✅ Updates stock entry prices with live market data
2. ✅ Recalculates TP1 and TP2 targets based on new prices
3. ✅ Updates option strikes to match current stock prices
4. ✅ Recalculates option premiums using Black-Scholes model
5. ✅ Updates option Greeks (Delta, Gamma, Theta, Vega)
6. ✅ Adjusts option target premiums

## 🚀 How to Update Prices

### Manual Update (Anytime)

**Windows (PowerShell):**
```powershell
cd c:\options.usa.ai\scripts
.\update_prices.ps1
```

**Linux/Mac (Bash):**
```bash
cd /path/to/options.usa.ai/scripts
./update_prices.sh
```

**Direct Command:**
```bash
docker exec trading_inference_api python realtime_price_fetcher.py
```

### Automatic Updates

#### Option 1: Scheduled Task (Windows)
Create a Windows Task Scheduler job to run daily:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 4:30 PM ET (after market close)
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-File "C:\options.usa.ai\scripts\update_prices.ps1"`

#### Option 2: Cron Job (Linux/Mac)
Add to crontab to run daily at 4:30 PM ET:
```bash
crontab -e
# Add this line:
30 16 * * 1-5 cd /path/to/options.usa.ai/scripts && ./update_prices.sh
```

#### Option 3: API Endpoint
Create an endpoint in the FastAPI application:
```python
@app.post("/admin/update-prices")
async def update_prices():
    """Trigger real-time price update"""
    subprocess.run(["python", "realtime_price_fetcher.py"])
    return {"status": "success", "message": "Prices updated"}
```

## 📊 Verified Real-Time Prices

### Example Current Prices (as of latest update):
- **AAPL**: $259.96 ✅ (Yahoo Finance)
- **NVDA**: $183.14 ✅ (Yahoo Finance)
- **MSFT**: $459.38 ✅ (Yahoo Finance)
- **META**: $615.52 ✅ (Yahoo Finance)
- **TSLA**: $439.20 ✅ (Yahoo Finance)
- **GOOGL**: $335.84 ✅ (Yahoo Finance)

All 54 symbols are now fetched from live market data!

## 🔧 Technical Details

### Dependencies Installed
- `yfinance`: Python library for Yahoo Finance API
- `asyncpg`: Async PostgreSQL driver (already installed)

### Script Location
- **Main Script**: `scripts/realtime_price_fetcher.py`
- **Quick Update Scripts**: 
  - Windows: `scripts/update_prices.ps1`
  - Linux/Mac: `scripts/update_prices.sh`

### Update Process
1. Connects to Yahoo Finance API
2. Fetches current prices for all symbols (with 0.2s rate limiting)
3. Updates database `recommendations.entry_price`
4. Recalculates all target prices based on side (BUY/SELL/HOLD)
5. Updates option strikes to be ~5% OTM
6. Recalculates option premiums and Greeks
7. Updates option target premiums

### Error Handling
- Failed symbols are logged but don't stop the update
- Rate limiting prevents API throttling
- Database transactions ensure atomic updates

## 🎨 UI Impact

After updating prices:
1. Refresh the browser at http://localhost:3000
2. You'll see current market prices for all stocks
3. Options strikes and premiums reflect current market conditions
4. Target prices are recalculated for realistic gains/losses

## 📝 Notes

- **Market Hours**: Best to update after market close (4:00 PM ET)
- **Update Frequency**: Run as often as needed - daily, hourly, or on-demand
- **Data Accuracy**: Yahoo Finance data is typically accurate within seconds of market close
- **No Cost**: 100% free, no API keys or subscriptions required
- **Backup**: Original hardcoded values saved in `realistic_market_update.py` for reference

## 🚨 Troubleshooting

### If prices don't update:
1. Check if Docker containers are running: `docker ps`
2. Verify yfinance is installed: `docker exec trading_inference_api pip list | grep yfinance`
3. Check logs: `docker logs trading_inference_api`
4. Manually run: `docker exec trading_inference_api python realtime_price_fetcher.py`

### If a specific symbol fails:
- Symbol may be delisted or have data issues on Yahoo Finance
- Check symbol format (should be valid ticker symbol)
- Script will log failures and continue with other symbols

## 📈 Future Enhancements

Potential improvements:
- [ ] Add real-time streaming updates (WebSocket)
- [ ] Fetch historical data for backtesting
- [ ] Add multiple data source fallbacks (Alpha Vantage, Polygon.io)
- [ ] Cache prices with TTL to reduce API calls
- [ ] Add price change alerts/notifications
- [ ] Track price history in database

---

**Last Updated**: January 14, 2026
**Data Source**: Yahoo Finance (yfinance library)
**Update Method**: On-demand or scheduled
