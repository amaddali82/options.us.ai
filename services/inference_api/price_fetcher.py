"""
Real-time stock price fetcher and recommendation updater
Uses yfinance to fetch live prices and recalculate targets/confidence
"""
import yfinance as yf
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
import time
import asyncio

logger = logging.getLogger(__name__)


def fetch_single_price_with_retry(symbol: str, max_retries: int = 3) -> Optional[float]:
    """
    Fetch a single stock price with retry logic and exponential backoff
    
    Args:
        symbol: Stock symbol to fetch
        max_retries: Maximum number of retry attempts
        
    Returns:
        Current price or None if all attempts fail
    """
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)
            price = None
            
            # Method 1: Try history with longer period to get most recent price
            try:
                # Get last 5 days to ensure we catch most recent trading day
                hist = ticker.history(period='5d')
                if not hist.empty:
                    # Get the most recent close price
                    price = hist['Close'].iloc[-1]
                    if price and price > 0:
                        return float(price)
            except Exception as e:
                logger.debug(f"{symbol} history method failed: {str(e)[:50]}")
            
            # Method 2: Fallback to fast_info
            if not price:
                try:
                    if hasattr(ticker, 'fast_info'):
                        fast_info = ticker.fast_info
                        price = fast_info.get('lastPrice') or fast_info.get('previousClose')
                        if price and price > 0:
                            return float(price)
                except Exception as e:
                    logger.debug(f"{symbol} fast_info method failed: {str(e)[:50]}")
            
            # Method 3: Fallback to info dict (slower but more reliable)
            if not price:
                try:
                    info = ticker.info
                    price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                    if price and price > 0:
                        return float(price)
                except Exception as e:
                    logger.debug(f"{symbol} info method failed: {str(e)[:50]}")
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {symbol}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
    
    return None


def fetch_stock_prices(symbols: List[str], delay: float = 0.5) -> Dict[str, float]:
    """
    Fetch current stock prices for multiple symbols with rate limiting and retry logic
    
    Args:
        symbols: List of stock symbols
        delay: Delay between requests in seconds (default 0.5)
        
    Returns:
        Dict mapping symbol to current price
    """
    prices = {}
    
    # Process symbols individually with retry logic for better reliability
    for i, symbol in enumerate(symbols):
        try:
            price = fetch_single_price_with_retry(symbol, max_retries=3)
            
            if price:
                prices[symbol] = price
                logger.info(f"Fetched {symbol}: ${price:.2f}")
            else:
                logger.warning(f"No price found for {symbol} after all retry attempts")
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)[:100]}")
        
        # Rate limiting delay between symbols
        if i < len(symbols) - 1:
            time.sleep(delay)
        
    return prices


def calculate_technical_targets(symbol: str, current_price: float, horizon: str) -> tuple:
    """
    Calculate target prices based on technical analysis
    
    Args:
        symbol: Stock symbol
        current_price: Current stock price
        horizon: intraday, swing, or position
        
    Returns:
        (tp1, tp2, confidence) tuple
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        if horizon == "intraday":
            hist = ticker.history(period="5d", interval="15m")
        elif horizon == "swing":
            hist = ticker.history(period="1mo", interval="1d")
        else:  # position
            hist = ticker.history(period="3mo", interval="1d")
        
        if hist.empty:
            # Fallback to percentage-based targets
            return calculate_percentage_targets(current_price, horizon)
        
        # Calculate volatility
        returns = hist['Close'].pct_change()
        volatility = returns.std()
        
        # Calculate support and resistance
        high = hist['High'].max()
        low = hist['Low'].min()
        
        # Determine targets based on volatility and price action
        if horizon == "intraday":
            tp1 = current_price * (1 + volatility * 1.5)
            tp2 = current_price * (1 + volatility * 2.5)
            confidence = min(0.75 + (volatility * 5), 0.92)
        elif horizon == "swing":
            tp1 = current_price * (1 + volatility * 2.0)
            tp2 = current_price * (1 + volatility * 3.5)
            confidence = min(0.70 + (volatility * 4), 0.88)
        else:  # position
            tp1 = current_price * (1 + volatility * 3.0)
            tp2 = current_price * (1 + volatility * 5.0)
            confidence = min(0.68 + (volatility * 3), 0.85)
        
        # Ensure reasonable bounds
        tp1 = min(tp1, high * 1.05)
        tp2 = min(tp2, high * 1.15)
        
        return round(tp1, 2), round(tp2, 2), round(confidence, 2)
        
    except Exception as e:
        logger.error(f"Error calculating targets for {symbol}: {e}")
        return calculate_percentage_targets(current_price, horizon)


def calculate_percentage_targets(current_price: float, horizon: str) -> tuple:
    """Fallback percentage-based target calculation"""
    if horizon == "intraday":
        tp1 = current_price * 1.02  # 2%
        tp2 = current_price * 1.04  # 4%
        confidence = 0.75
    elif horizon == "swing":
        tp1 = current_price * 1.05  # 5%
        tp2 = current_price * 1.10  # 10%
        confidence = 0.72
    else:  # position
        tp1 = current_price * 1.10  # 10%
        tp2 = current_price * 1.20  # 20%
        confidence = 0.70
    
    return round(tp1, 2), round(tp2, 2), confidence


def calculate_option_metrics(
    stock_price: float,
    strike: float,
    option_type: str,
    expiry_date: datetime,
    volatility: float = 0.35
) -> Dict:
    """
    Calculate option entry price and targets based on current stock price
    
    Args:
        stock_price: Current stock price
        strike: Option strike price
        option_type: CALL or PUT
        expiry_date: Option expiration date
        volatility: Implied volatility (default 35%)
        
    Returns:
        Dict with option_entry_price, tp1, tp2, confidence
    """
    # Days to expiration
    now = datetime.now(timezone.utc)
    dte = (expiry_date.replace(tzinfo=timezone.utc) - now).days
    
    if dte <= 0:
        dte = 1
    
    # Calculate intrinsic value
    if option_type == "CALL":
        intrinsic = max(0, stock_price - strike)
    else:  # PUT
        intrinsic = max(0, strike - stock_price)
    
    # Calculate time value (simplified Black-Scholes approximation)
    time_value = stock_price * volatility * (dte / 365) ** 0.5 * 0.4
    
    option_entry_price = intrinsic + time_value
    
    # Calculate option targets (25% and 50% gains)
    opt_tp1 = option_entry_price * 1.25
    opt_tp2 = option_entry_price * 1.50
    
    # Confidence based on moneyness and time
    moneyness = abs(stock_price - strike) / strike
    time_factor = min(dte / 30, 1.0)  # Normalize to 30 days
    
    confidence = 0.70 + (time_factor * 0.15) - (moneyness * 0.1)
    confidence = max(0.60, min(0.90, confidence))
    
    return {
        "option_entry_price": round(option_entry_price, 2),
        "tp1": round(opt_tp1, 2),
        "tp2": round(opt_tp2, 2),
        "confidence": round(confidence, 2),
        "current_stock_price": stock_price
    }


def get_current_volatility(symbol: str) -> float:
    """Fetch current implied volatility from market data"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Try to get implied volatility from options data
        options = ticker.options
        if options:
            # Get nearest expiry
            nearest_exp = options[0]
            opt_chain = ticker.option_chain(nearest_exp)
            
            # Average IV from calls
            if not opt_chain.calls.empty and 'impliedVolatility' in opt_chain.calls.columns:
                iv = opt_chain.calls['impliedVolatility'].median()
                if iv and iv > 0:
                    return float(iv)
        
        # Fallback: calculate historical volatility
        hist = ticker.history(period="1mo")
        if not hist.empty:
            returns = hist['Close'].pct_change()
            hv = returns.std() * (252 ** 0.5)  # Annualized
            return float(hv)
            
    except Exception as e:
        logger.error(f"Error fetching volatility for {symbol}: {e}")
    
    # Default fallback
    return 0.35


if __name__ == "__main__":
    # Test the price fetcher
    logging.basicConfig(level=logging.INFO)
    
    symbols = ["AAPL", "MSFT", "NVDA", "TSLA"]
    prices = fetch_stock_prices(symbols)
    
    print("\nFetched Prices:")
    for symbol, price in prices.items():
        print(f"{symbol}: ${price:.2f}")
        
        # Test target calculation
        tp1, tp2, conf = calculate_technical_targets(symbol, price, "swing")
        print(f"  TP1: ${tp1:.2f}, TP2: ${tp2:.2f}, Confidence: {conf:.2%}")
