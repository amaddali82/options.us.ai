"""
Realistic recommendation generator for multiple symbols and horizons.
Generates recommendations with targets, stops, and options conforming to Pydantic schemas.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone, date
from typing import List, Dict, Tuple, Optional
from decimal import Decimal

# Symbol universe with realistic current prices (Jan 2025)
SYMBOL_UNIVERSE = {
    # Mega Cap Tech
    "AAPL": 225.50, "MSFT": 428.75, "GOOGL": 178.25, "AMZN": 185.40, "META": 525.80,
    "NVDA": 725.60, "TSLA": 267.40, "NFLX": 495.30, "AMD": 162.45, "CRM": 285.20,
    
    # Tech & Software
    "ORCL": 125.75, "ADBE": 487.30, "INTC": 51.25, "CSCO": 58.40, "QCOM": 158.90,
    "AVGO": 1342.50, "NOW": 852.40, "SNOW": 125.80, "PLTR": 32.60, "U": 28.90,
    
    # Finance
    "JPM": 168.50, "BAC": 34.20, "GS": 408.50, "MS": 98.40, "C": 58.60,
    "WFC": 52.30, "BLK": 788.20, "SCHW": 72.50, "V": 275.80, "MA": 445.60,
    
    # Healthcare & Biotech
    "JNJ": 162.40, "UNH": 528.70, "PFE": 28.50, "ABBV": 168.30, "TMO": 542.80,
    "LLY": 628.50, "MRNA": 78.20, "GILD": 82.40, "REGN": 942.30, "VRTX": 428.60,
    
    # Consumer & Retail
    "WMT": 168.50, "HD": 368.20, "NKE": 108.40, "SBUX": 98.20, "TGT": 152.30,
    "COST": 728.50, "MCD": 288.40, "DIS": 98.60, "PYPL": 62.80, "SQ": 78.40,
    
    # Energy & Commodities
    "XOM": 102.50, "CVX": 148.30, "COP": 118.20, "SLB": 52.40, "OXY": 58.30,
    
    # Industrials & Aerospace
    "BA": 218.50, "CAT": 328.40, "GE": 168.20, "LMT": 468.30, "RTX": 102.50,
    
    # Semiconductors
    "TSM": 142.30, "MU": 98.20, "AMAT": 188.50, "LRCX": 842.30, "KLAC": 628.40,
    
    # Crypto & Fintech
    "COIN": 182.30, "HOOD": 18.20, "SOFI": 8.50, "MSTR": 428.50,
    
    # EVs & Clean Energy
    "RIVN": 12.40, "LCID": 3.20, "F": 12.80, "GM": 42.30, "ENPH": 98.40
}

HORIZONS = ["intraday", "swing", "position"]
HORIZON_DAYS = {"intraday": 1, "swing": 7, "position": 14}

# Event catalysts for rationale
EVENT_TAGS = [
    "earnings_beat", "earnings_miss", "guidance_raise", "guidance_lower",
    "product_launch", "regulatory_approval", "partnership_announced", "acquisition_rumor",
    "analyst_upgrade", "analyst_downgrade", "sector_rotation", "technical_breakout",
    "technical_breakdown", "volume_surge", "short_squeeze", "institutional_buying",
    "insider_buying", "insider_selling", "dividend_increase", "share_buyback",
    "management_change", "legal_settlement", "patent_granted", "clinical_trial_success",
    "market_share_gain", "margin_expansion", "debt_reduction", "capacity_expansion"
]

SECTOR_THEMES = {
    "tech": ["AI adoption", "Cloud growth", "Digital transformation", "Cybersecurity demand"],
    "finance": ["Rate cuts expected", "Credit quality improving", "M&A activity", "Regulatory clarity"],
    "healthcare": ["Drug pipeline", "Medicare pricing", "Hospital utilization", "Biotech innovation"],
    "energy": ["Oil price recovery", "Refining margins", "Energy transition", "OPEC+ discipline"],
    "consumer": ["Consumer spending", "Brand strength", "E-commerce shift", "Price power"]
}


def get_sector(symbol: str) -> str:
    """Categorize symbol by sector"""
    tech = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX", "AMD", "CRM", 
            "ORCL", "ADBE", "INTC", "CSCO", "QCOM", "AVGO", "NOW", "SNOW", "PLTR", "U",
            "TSM", "MU", "AMAT", "LRCX", "KLAC", "COIN", "HOOD", "SOFI", "MSTR"]
    finance = ["JPM", "BAC", "GS", "MS", "C", "WFC", "BLK", "SCHW", "V", "MA"]
    healthcare = ["JNJ", "UNH", "PFE", "ABBV", "TMO", "LLY", "MRNA", "GILD", "REGN", "VRTX"]
    energy = ["XOM", "CVX", "COP", "SLB", "OXY"]
    consumer = ["WMT", "HD", "NKE", "SBUX", "TGT", "COST", "MCD", "DIS", "PYPL", "SQ"]
    
    if symbol in tech:
        return "tech"
    elif symbol in finance:
        return "finance"
    elif symbol in healthcare:
        return "healthcare"
    elif symbol in energy:
        return "energy"
    elif symbol in consumer:
        return "consumer"
    else:
        return "industrials"


def calculate_implied_vol(symbol: str, sector: str) -> float:
    """Estimate implied volatility based on sector and symbol characteristics"""
    base_iv = {
        "tech": 0.35,
        "finance": 0.25,
        "healthcare": 0.40,
        "energy": 0.32,
        "consumer": 0.22,
        "industrials": 0.28
    }
    
    # High volatility stocks
    high_vol = ["TSLA", "NVDA", "MRNA", "COIN", "RIVN", "LCID", "SNOW", "PLTR", "MSTR"]
    
    iv = base_iv.get(sector, 0.30)
    if symbol in high_vol:
        iv *= 1.4
    
    # Add random variation
    iv *= random.uniform(0.85, 1.15)
    return round(iv, 2)


def calculate_greeks(option_type: str, delta_target: float, iv: float, dte: int) -> Dict:
    """Simulate option Greeks based on delta, IV, and DTE"""
    # Delta is provided (target delta bucket)
    delta = delta_target if option_type == "CALL" else -delta_target
    
    # Gamma: higher for ATM, decreases with DTE
    gamma = (0.02 if abs(delta_target - 0.5) < 0.15 else 0.01) * (30 / max(dte, 7))
    gamma = round(gamma, 3)
    
    # Theta: time decay, increases closer to expiry
    theta = -0.15 * (iv / 0.30) * (30 / max(dte, 7))
    theta = round(theta, 2)
    
    # Vega: sensitivity to IV, higher for longer DTE
    vega = 0.15 * (dte / 30) * (1 if abs(delta_target - 0.5) < 0.2 else 0.7)
    vega = round(vega, 2)
    
    # Rho: small, increases with DTE
    rho = 0.05 * (dte / 30) * delta_target
    rho = round(rho, 2)
    
    return {
        "delta": round(delta, 2),
        "gamma": gamma,
        "theta": theta,
        "vega": vega,
        "rho": rho
    }


def get_option_expiry(horizon: str, base_date: datetime) -> date:
    """Calculate option expiry based on horizon"""
    if horizon == "intraday":
        # 2-5 days out (nearest weekly)
        days_out = random.randint(2, 5)
        expiry_dt = base_date + timedelta(days=days_out)
    elif horizon == "swing":
        # 1-2 weeks out
        days_out = random.randint(7, 14)
        expiry_dt = base_date + timedelta(days=days_out)
    else:  # position
        # 2-6 weeks out
        days_out = random.randint(14, 42)
        expiry_dt = base_date + timedelta(days=days_out)
    
    # Round to nearest Friday
    days_until_friday = (4 - expiry_dt.weekday()) % 7
    expiry_dt = expiry_dt + timedelta(days=days_until_friday)
    
    return expiry_dt.date()


def calculate_option_strike(entry_price: float, side: str, delta_target: float) -> float:
    """Calculate strike price based on desired delta"""
    # Approximate strike based on delta
    # For CALL (long): delta 0.60 -> strike ~2-3% OTM, delta 0.40 -> strike ~5-7% OTM
    # For PUT (short): delta 0.40 -> strike ~5-7% OTM (below spot)
    
    if side == "BUY":  # CALL
        if delta_target >= 0.60:
            strike_pct = random.uniform(0.98, 1.02)  # Near ATM
        elif delta_target >= 0.50:
            strike_pct = random.uniform(1.02, 1.05)  # Slightly OTM
        else:
            strike_pct = random.uniform(1.05, 1.10)  # More OTM
    else:  # SELL -> PUT
        if delta_target >= 0.40:
            strike_pct = random.uniform(0.92, 0.96)  # Moderately OTM
        elif delta_target >= 0.30:
            strike_pct = random.uniform(0.88, 0.92)  # More OTM
        else:
            strike_pct = random.uniform(0.85, 0.88)  # Deep OTM
    
    strike = entry_price * strike_pct
    
    # Round to standard option strike increments
    # Most stocks use $5 increments, some use $2.50 or $1
    if strike < 25:
        # Low priced stocks: $0.50 or $1 increments
        strike = round(strike / 0.5) * 0.5
    elif strike < 50:
        # $1 increments
        strike = round(strike / 1) * 1
    elif strike < 100:
        # $2.50 or $5 increments
        strike = round(strike / 2.5) * 2.5
    else:
        # $5 increments for most stocks
        strike = round(strike / 5) * 5
    
    return strike


def estimate_option_price(entry_price: float, strike: float, iv: float, dte: int, option_type: str) -> float:
    """Rough option pricing estimate (simplified Black-Scholes approximation)"""
    moneyness = strike / entry_price
    
    # Intrinsic value
    if option_type == "CALL":
        intrinsic = max(0, entry_price - strike)
    else:  # PUT
        intrinsic = max(0, strike - entry_price)
    
    # Time value (very simplified)
    time_value = entry_price * iv * (dte / 365) ** 0.5 * 0.4
    
    # Adjust for moneyness
    if option_type == "CALL":
        if moneyness > 1.05:  # OTM
            time_value *= 0.6
        elif moneyness < 0.95:  # ITM
            time_value *= 0.8
    else:  # PUT
        if moneyness < 0.95:  # OTM
            time_value *= 0.6
        elif moneyness > 1.05:  # ITM
            time_value *= 0.8
    
    price = intrinsic + time_value
    
    # Round to reasonable increments
    if price < 1:
        price = round(price, 2)
    elif price < 10:
        price = round(price, 1)
    else:
        price = round(price / 0.5) * 0.5
    
    return max(0.05, price)  # Minimum $0.05


def generate_rationale(symbol: str, side: str, sector: str, event_tags: List[str]) -> Dict:
    """Generate realistic rationale with thesis, catalysts, and risks"""
    sector_themes = SECTOR_THEMES.get(sector, ["Market momentum", "Technical setup"])
    
    if side == "BUY":
        thesis_templates = [
            f"Strong {random.choice(sector_themes).lower()} supports upside",
            f"Technical breakout with {random.choice(['volume confirmation', 'momentum shift', 'trend reversal'])}",
            f"Undervalued relative to {random.choice(['peers', 'historical multiples', 'growth trajectory'])}",
            f"Positive {random.choice(['fundamental shift', 'catalyst setup', 'sentiment change'])}"
        ]
        risk_templates = [
            f"Macro {random.choice(['headwinds', 'uncertainty', 'volatility'])}",
            f"{random.choice(['Valuation', 'Technical', 'Momentum'])} stretched",
            f"Sector {random.choice(['rotation risk', 'correlation', 'weakness'])}",
            f"{random.choice(['Execution', 'Competition', 'Regulatory'])} concerns"
        ]
    else:  # SELL
        thesis_templates = [
            f"Overextended rally due for {random.choice(['correction', 'pullback', 'consolidation'])}",
            f"Weakening {random.choice(sector_themes).lower()} signals downside",
            f"Technical {random.choice(['breakdown', 'reversal pattern', 'divergence'])} confirmed",
            f"Negative {random.choice(['fundamentals', 'sentiment shift', 'momentum loss'])}"
        ]
        risk_templates = [
            f"Short squeeze potential on {random.choice(['high SI', 'momentum', 'news'])}",
            f"Strong {random.choice(['support level', 'institutional buying', 'dip buying'])}",
            f"Sector {random.choice(['strength persists', 'rotation into', 'leadership'])}",
            f"Market {random.choice(['momentum', 'sentiment', 'breadth'])} remains strong"
        ]
    
    thesis = random.choice(thesis_templates)
    
    # Select 2-4 catalysts from event_tags
    catalysts = [tag.replace("_", " ").title() for tag in event_tags]
    
    # Generate 2-3 risks
    risks = random.sample(risk_templates, k=random.randint(2, 3))
    
    # Sentiment score
    sentiment = round(random.uniform(0.65, 0.90) if side == "BUY" else random.uniform(-0.90, -0.65), 2)
    
    return {
        "thesis": thesis,
        "catalysts": catalysts,
        "risks": risks,
        "sentiment_score": sentiment,
        "event_tags": event_tags
    }


def generate_quality_metrics(symbol: str, sector: str) -> Dict:
    """Generate quality metrics for the recommendation"""
    # Liquidity score based on symbol (mega caps have higher liquidity)
    mega_caps = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
    
    if symbol in mega_caps:
        liquidity = round(random.uniform(0.92, 0.98), 2)
    elif symbol in list(SYMBOL_UNIVERSE.keys())[:30]:
        liquidity = round(random.uniform(0.85, 0.92), 2)
    else:
        liquidity = round(random.uniform(0.70, 0.85), 2)
    
    return {
        "liquidity_score": liquidity,
        "data_quality": random.choice(["high", "high", "medium"]),
        "model_version": f"v{random.randint(2, 3)}.{random.randint(0, 5)}",
        "signal_strength": round(random.uniform(0.65, 0.95), 2)
    }


def generate_recommendation(
    symbol: str,
    entry_price: float,
    horizon: str,
    asof: Optional[datetime] = None,
    include_option: bool = True
) -> Dict:
    """
    Generate a single realistic recommendation
    
    Returns dict compatible with database models
    """
    if asof is None:
        asof = datetime.now(timezone.utc)
    
    # Determine side (60% BUY, 30% SELL, 10% HOLD)
    side_choice = random.choices(["BUY", "SELL", "HOLD"], weights=[60, 30, 10])[0]
    
    # Skip options for HOLD
    if side_choice == "HOLD":
        include_option = False
    
    # Base confidence
    confidence_overall = round(random.uniform(0.68, 0.94), 2)
    
    # Expected move based on horizon and volatility
    sector = get_sector(symbol)
    iv = calculate_implied_vol(symbol, sector)
    
    horizon_days = HORIZON_DAYS[horizon]
    daily_move = iv / (252 ** 0.5)  # Annualized to daily
    expected_move_pct = daily_move * (horizon_days ** 0.5) * (3 if side_choice == "BUY" else -3)
    expected_move_pct = round(expected_move_pct * 100, 2)  # To percentage
    
    # Generate 2 targets
    if side_choice == "BUY":
        tp1_pct = random.uniform(0.03, 0.06) if horizon == "intraday" else random.uniform(0.05, 0.10)
        tp2_pct = tp1_pct + random.uniform(0.03, 0.08)
    elif side_choice == "SELL":
        tp1_pct = -random.uniform(0.03, 0.06) if horizon == "intraday" else -random.uniform(0.05, 0.10)
        tp2_pct = tp1_pct - random.uniform(0.03, 0.08)
    else:  # HOLD
        tp1_pct = random.uniform(0.01, 0.03)
        tp2_pct = -random.uniform(0.01, 0.03)
    
    tp1_value = round(entry_price * (1 + tp1_pct), 2)
    tp2_value = round(entry_price * (1 + tp2_pct), 2)
    
    # Stop loss
    if side_choice == "BUY":
        stop_pct = -random.uniform(0.03, 0.08)
    elif side_choice == "SELL":
        stop_pct = random.uniform(0.03, 0.08)
    else:  # HOLD
        stop_pct = -random.uniform(0.02, 0.04)
    
    stop_value = round(entry_price * (1 + stop_pct), 2)
    
    # ETA in minutes
    if horizon == "intraday":
        eta1 = random.randint(60, 300)
        eta2 = random.randint(300, 480)
    elif horizon == "swing":
        eta1 = random.randint(1440, 4320)  # 1-3 days
        eta2 = random.randint(4320, 10080)  # 3-7 days
    else:  # position
        eta1 = random.randint(7200, 14400)  # 5-10 days
        eta2 = random.randint(14400, 28800)  # 10-20 days
    
    # Event tags and rationale
    num_events = random.randint(2, 4)
    event_tags = random.sample(EVENT_TAGS, k=num_events)
    rationale = generate_rationale(symbol, side_choice, sector, event_tags)
    quality = generate_quality_metrics(symbol, sector)
    
    reco_id = uuid.uuid4()
    
    reco = {
        "reco_id": reco_id,
        "asof": asof,
        "symbol": symbol,
        "horizon": horizon,
        "side": side_choice,
        "entry_price": entry_price,
        "confidence_overall": confidence_overall,
        "expected_move_pct": expected_move_pct,
        "rationale": rationale,
        "quality": quality,
        "targets": [
            {
                "ordinal": 1,
                "name": "TP1",
                "target_type": "price",
                "value": tp1_value,
                "confidence": round(confidence_overall - random.uniform(0.05, 0.10), 2),
                "eta_minutes": eta1
            },
            {
                "ordinal": 2,
                "name": "TP2",
                "target_type": "price",
                "value": tp2_value,
                "confidence": round(confidence_overall - random.uniform(0.12, 0.18), 2),
                "eta_minutes": eta2
            }
        ],
        "stop": {
            "stop_type": random.choice(["hard", "trailing", "mental"]),
            "value": stop_value,
            "confidence": round(confidence_overall - random.uniform(0.02, 0.05), 2)
        }
    }
    
    # Add option idea if requested and not HOLD
    if include_option and side_choice != "HOLD":
        option_type = "CALL" if side_choice == "BUY" else "PUT"
        expiry = get_option_expiry(horizon, asof)
        dte = (expiry - asof.date()).days
        
        # Delta target based on conviction
        if confidence_overall >= 0.85:
            delta_target = random.uniform(0.55, 0.65)
        elif confidence_overall >= 0.75:
            delta_target = random.uniform(0.45, 0.55)
        else:
            delta_target = random.uniform(0.35, 0.45)
        
        strike = calculate_option_strike(entry_price, side_choice, delta_target)
        option_entry_price = estimate_option_price(entry_price, strike, iv, dte, option_type)
        
        # Greeks
        greeks = calculate_greeks(option_type, delta_target, iv, dte)
        
        # Option targets (premium) - calculate based on underlying price movement and time decay
        # When underlying moves to TP1/TP2, option value increases significantly
        # Account for intrinsic value gain and remaining time value
        
        if side_choice == "BUY":  # CALL
            # For calls: as underlying rises, option gains intrinsic + time value
            # TP1: underlying at tp1_value, option gains (tp1_value - strike) + remaining time value
            tp1_intrinsic_gain = max(0, tp1_value - strike) - max(0, entry_price - strike)
            tp2_intrinsic_gain = max(0, tp2_value - strike) - max(0, entry_price - strike)
            
            # Time decay factor (less time value at TP due to time passing)
            time_decay_tp1 = 0.85  # Assume 15% time decay to TP1
            time_decay_tp2 = 0.70  # Assume 30% time decay to TP2
            
            opt_tp1 = option_entry_price + tp1_intrinsic_gain + (option_entry_price * 0.20 * time_decay_tp1)
            opt_tp2 = option_entry_price + tp2_intrinsic_gain + (option_entry_price * 0.30 * time_decay_tp2)
            
        else:  # PUT
            # For puts: as underlying falls, option gains intrinsic + time value
            tp1_intrinsic_gain = max(0, strike - tp1_value) - max(0, strike - entry_price)
            tp2_intrinsic_gain = max(0, strike - tp2_value) - max(0, strike - entry_price)
            
            time_decay_tp1 = 0.85
            time_decay_tp2 = 0.70
            
            opt_tp1 = option_entry_price + tp1_intrinsic_gain + (option_entry_price * 0.20 * time_decay_tp1)
            opt_tp2 = option_entry_price + tp2_intrinsic_gain + (option_entry_price * 0.30 * time_decay_tp2)
        
        # Ensure targets are reasonable (at least 25% gain for TP1, 50% for TP2)
        opt_tp1 = max(opt_tp1, option_entry_price * 1.25)
        opt_tp2 = max(opt_tp2, option_entry_price * 1.50)
        
        opt_tp1 = round(opt_tp1, 2)
        opt_tp2 = round(opt_tp2, 2)
        
        reco["option_idea"] = {
            "option_type": option_type,
            "expiry": expiry,
            "strike": strike,
            "option_entry_price": option_entry_price,
            "greeks": greeks,
            "iv": {
                "implied_vol": iv,
                "iv_rank": round(random.uniform(0.30, 0.75), 2)
            },
            "notes": f"{delta_target*100:.0f}Δ {option_type} for {horizon} play",
            "option_targets": [
                {
                    "ordinal": 1,
                    "name": "Premium TP1",
                    "value": opt_tp1,
                    "confidence": round(confidence_overall * 0.85, 2),  # 85% of underlying confidence
                    "eta_minutes": eta1
                },
                {
                    "ordinal": 2,
                    "name": "Premium TP2",
                    "value": opt_tp2,
                    "confidence": round(confidence_overall * 0.70, 2),  # 70% of underlying confidence
                    "eta_minutes": eta2
                }
            ]
        }
    
    return reco


def generate_batch(
    num_recommendations: int = 50,
    symbols: Optional[List[str]] = None,
    option_pct: float = 0.65,
    asof: Optional[datetime] = None
) -> List[Dict]:
    """
    Generate a batch of recommendations
    
    Args:
        num_recommendations: Number of recommendations to generate
        symbols: List of symbols (if None, randomly samples from SYMBOL_UNIVERSE)
        option_pct: Percentage that should include options (0.0-1.0)
        asof: Timestamp for recommendations (default: now)
    
    Returns:
        List of recommendation dicts ready for database insertion
    """
    if asof is None:
        asof = datetime.now(timezone.utc)
    
    if symbols is None:
        # Sample from universe
        symbols = random.choices(list(SYMBOL_UNIVERSE.keys()), k=num_recommendations)
    
    recommendations = []
    
    for symbol in symbols:
        entry_price = SYMBOL_UNIVERSE.get(symbol, 100.0)
        
        # Randomly select horizon
        horizon = random.choice(HORIZONS)
        
        # Determine if this reco should have options
        include_option = random.random() < option_pct
        
        reco = generate_recommendation(
            symbol=symbol,
            entry_price=entry_price,
            horizon=horizon,
            asof=asof,
            include_option=include_option
        )
        
        recommendations.append(reco)
    
    return recommendations


def generate_for_symbol_set(
    symbols: List[str],
    horizons: Optional[List[str]] = None,
    asof: Optional[datetime] = None
) -> List[Dict]:
    """
    Generate one recommendation per symbol per horizon
    
    Args:
        symbols: List of symbols
        horizons: List of horizons (default: all)
        asof: Timestamp
        
    Returns:
        List of recommendations
    """
    if horizons is None:
        horizons = HORIZONS
    
    if asof is None:
        asof = datetime.now(timezone.utc)
    
    recommendations = []
    
    for symbol in symbols:
        entry_price = SYMBOL_UNIVERSE.get(symbol, 100.0)
        
        for horizon in horizons:
            # 70% have options
            include_option = random.random() < 0.70
            
            reco = generate_recommendation(
                symbol=symbol,
                entry_price=entry_price,
                horizon=horizon,
                asof=asof,
                include_option=include_option
            )
            
            recommendations.append(reco)
    
    return recommendations


if __name__ == "__main__":
    # Test generation
    print("Generating 10 sample recommendations...")
    
    test_symbols = ["AAPL", "NVDA", "TSLA", "JPM", "MRNA", "XOM", "BA", "NFLX", "V", "HD"]
    recos = generate_batch(10, symbols=test_symbols, option_pct=0.70)
    
    print(f"\nGenerated {len(recos)} recommendations:")
    for r in recos:
        opt_str = f"+ {r['option_idea']['option_type']}" if "option_idea" in r else ""
        print(f"  {r['symbol']:6} {r['side']:4} {r['horizon']:9} @ ${r['entry_price']:7.2f} "
              f"conf={r['confidence_overall']:.2f} {opt_str}")
    
    print("\n✅ Generator working correctly!")
