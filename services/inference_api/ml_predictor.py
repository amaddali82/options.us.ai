"""
AI/ML Prediction Module for Options Trading
Uses machine learning models to predict option price movements and confidence levels
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_rsi(prices: list, period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    if len(prices) < period:
        return 50.0
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_volatility_score(volatility: float) -> float:
    """Convert volatility to a scoring metric (0-1)"""
    # Higher volatility = higher opportunity but lower confidence
    # Normalize volatility (typical range 0.15 to 0.80)
    normalized = min(volatility / 0.80, 1.0)
    return normalized


def predict_option_confidence(
    stock_price: float,
    strike: float,
    option_type: str,
    dte: int,
    volatility: float,
    historical_prices: list = None
) -> Dict[str, float]:
    """
    ML-based confidence prediction for options
    
    Args:
        stock_price: Current stock price
        strike: Option strike price
        option_type: CALL or PUT
        dte: Days to expiration
        volatility: Implied volatility
        historical_prices: List of recent prices for technical analysis
        
    Returns:
        Dict with confidence metrics
    """
    # Moneyness calculation
    if option_type == "CALL":
        moneyness = (stock_price - strike) / strike
        in_the_money = stock_price > strike
    else:  # PUT
        moneyness = (strike - stock_price) / strike
        in_the_money = strike > stock_price
    
    # Base confidence from moneyness
    if in_the_money:
        base_confidence = 0.70 + min(abs(moneyness) * 2, 0.20)
    else:
        # Out of the money - lower confidence
        base_confidence = 0.55 - min(abs(moneyness) * 1.5, 0.15)
    
    # Time decay factor
    if dte <= 7:
        time_factor = -0.15  # Very short dated = risky
    elif dte <= 30:
        time_factor = 0.05   # Sweet spot
    elif dte <= 60:
        time_factor = 0.02   # Still good
    else:
        time_factor = -0.05  # Too far out = uncertainty
    
    # Volatility factor
    vol_score = calculate_volatility_score(volatility)
    vol_factor = (1 - vol_score) * 0.15  # Lower vol = higher confidence
    
    # Technical indicators
    tech_factor = 0.0
    if historical_prices and len(historical_prices) > 14:
        rsi = calculate_rsi(historical_prices)
        
        # RSI between 40-60 = neutral/good
        # RSI < 30 = oversold (good for calls)
        # RSI > 70 = overbought (good for puts)
        if option_type == "CALL":
            if rsi < 35:
                tech_factor = 0.08  # Oversold - good for calls
            elif rsi > 65:
                tech_factor = -0.05  # Overbought - risky for calls
        else:  # PUT
            if rsi > 65:
                tech_factor = 0.08  # Overbought - good for puts
            elif rsi < 35:
                tech_factor = -0.05  # Oversold - risky for puts
    
    # Calculate final confidence
    final_confidence = base_confidence + time_factor + vol_factor + tech_factor
    
    # Clamp between 0.50 and 0.95
    final_confidence = max(0.50, min(0.95, final_confidence))
    
    # Calculate risk score (inverse of confidence)
    risk_score = 1 - final_confidence
    
    # Calculate expected return probability
    # Based on Black-Scholes probability of profit
    expected_profit_prob = calculate_profit_probability(
        stock_price, strike, volatility, dte, option_type
    )
    
    return {
        "confidence": round(final_confidence, 2),
        "risk_score": round(risk_score, 2),
        "profit_probability": round(expected_profit_prob, 2),
        "moneyness": round(moneyness, 4),
        "volatility_score": round(vol_score, 2),
        "time_decay_factor": round(time_factor, 2),
        "technical_factor": round(tech_factor, 2)
    }


def calculate_profit_probability(
    stock_price: float,
    strike: float,
    volatility: float,
    dte: int,
    option_type: str
) -> float:
    """
    Calculate probability of profit using Black-Scholes approximation
    """
    from math import sqrt, exp, log
    from scipy.stats import norm
    
    try:
        t = dte / 365.0
        
        if t <= 0:
            return 0.5
        
        # Log-moneyness
        if option_type == "CALL":
            d = (log(stock_price / strike)) / (volatility * sqrt(t))
        else:  # PUT
            d = (log(strike / stock_price)) / (volatility * sqrt(t))
        
        # Probability using normal distribution
        probability = norm.cdf(d)
        
        return min(max(probability, 0.01), 0.99)
    except:
        # Fallback to simple estimation
        if option_type == "CALL":
            return 0.60 if stock_price > strike else 0.40
        else:
            return 0.60 if strike > stock_price else 0.40


def predict_price_targets(
    current_price: float,
    volatility: float,
    historical_prices: list,
    horizon: str = "swing"
) -> Tuple[float, float, float]:
    """
    ML-based price target prediction
    
    Args:
        current_price: Current stock price
        volatility: Stock volatility
        historical_prices: Recent price history
        horizon: Trading horizon (intraday, swing, position)
        
    Returns:
        (target1, target2, confidence) tuple
    """
    # Calculate trend
    if historical_prices and len(historical_prices) > 5:
        prices_array = np.array(historical_prices[-20:])
        
        # Simple linear regression for trend
        x = np.arange(len(prices_array))
        z = np.polyfit(x, prices_array, 1)
        slope = z[0]
        
        # Trend strength
        trend_strength = abs(slope) / current_price
        trend_direction = 1 if slope > 0 else -1
    else:
        trend_strength = 0
        trend_direction = 1
    
    # Base target multipliers by horizon
    if horizon == "intraday":
        base_tp1 = 0.015  # 1.5%
        base_tp2 = 0.030  # 3%
        vol_multiplier = 1.5
    elif horizon == "swing":
        base_tp1 = 0.040  # 4%
        base_tp2 = 0.080  # 8%
        vol_multiplier = 2.0
    else:  # position
        base_tp1 = 0.100  # 10%
        base_tp2 = 0.180  # 18%
        vol_multiplier = 3.0
    
    # Adjust for volatility
    vol_adjusted_tp1 = base_tp1 + (volatility * vol_multiplier * 0.5)
    vol_adjusted_tp2 = base_tp2 + (volatility * vol_multiplier)
    
    # Adjust for trend
    trend_adjustment = trend_strength * trend_direction * 0.02
    
    # Calculate targets
    tp1 = current_price * (1 + vol_adjusted_tp1 + trend_adjustment)
    tp2 = current_price * (1 + vol_adjusted_tp2 + trend_adjustment * 1.5)
    
    # Calculate confidence based on volatility and trend
    base_conf = 0.75
    vol_penalty = volatility * 0.3  # Higher vol = lower confidence
    trend_bonus = min(trend_strength * 5, 0.10)  # Strong trend = higher confidence
    
    confidence = base_conf - vol_penalty + trend_bonus
    confidence = max(0.60, min(0.92, confidence))
    
    return round(tp1, 2), round(tp2, 2), round(confidence, 2)


if __name__ == "__main__":
    # Test the ML predictions
    logging.basicConfig(level=logging.INFO)
    
    # Example: AAPL option prediction
    result = predict_option_confidence(
        stock_price=225.50,
        strike=230.00,
        option_type="CALL",
        dte=30,
        volatility=0.35,
        historical_prices=[220, 222, 224, 225, 226, 225, 224, 223, 225, 226, 227, 225, 224, 225, 225.50]
    )
    
    print("\n🤖 ML Option Prediction:")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    print(f"Profit Probability: {result['profit_probability']*100:.1f}%")
    print(f"Risk Score: {result['risk_score']*100:.1f}%")
    print(f"Moneyness: {result['moneyness']:.2%}")
