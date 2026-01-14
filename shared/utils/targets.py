"""
Target calculation utilities for underlying and option positions.

Provides functions for:
- Computing underlying price targets based on predicted volatility
- Calculating target confidence using normal distribution
- Black-Scholes option pricing for calls and puts
- Option premium targets at various underlying price levels
"""

import math
from typing import Tuple, Literal, Dict, List
from decimal import Decimal


def calculate_underlying_targets(
    entry_price: float,
    predicted_sigma: float,
    side: Literal["BUY", "SELL"],
    tp1_sigma_multiplier: float = 0.6,
    tp2_sigma_multiplier: float = 1.0,
) -> Tuple[float, float]:
    """
    Calculate underlying price targets based on predicted volatility.
    
    For long positions (BUY):
        TP1 = entry + (tp1_sigma_multiplier * sigma * entry)
        TP2 = entry + (tp2_sigma_multiplier * sigma * entry)
    
    For short positions (SELL):
        TP1 = entry - (tp1_sigma_multiplier * sigma * entry)
        TP2 = entry - (tp2_sigma_multiplier * sigma * entry)
    
    Args:
        entry_price: Entry price of the underlying
        predicted_sigma: Predicted volatility (annualized, e.g., 0.25 for 25%)
        side: Position side ("BUY" for long, "SELL" for short)
        tp1_sigma_multiplier: Multiplier for TP1 (default 0.6 sigma)
        tp2_sigma_multiplier: Multiplier for TP2 (default 1.0 sigma)
    
    Returns:
        Tuple of (tp1, tp2) target prices
    
    Examples:
        >>> calculate_underlying_targets(100.0, 0.20, "BUY")
        (112.0, 120.0)
        >>> calculate_underlying_targets(100.0, 0.20, "SELL")
        (88.0, 80.0)
    """
    if entry_price <= 0:
        raise ValueError("entry_price must be positive")
    if predicted_sigma < 0:
        raise ValueError("predicted_sigma must be non-negative")
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be 'BUY' or 'SELL'")
    
    # Calculate price moves based on sigma
    tp1_move = tp1_sigma_multiplier * predicted_sigma * entry_price
    tp2_move = tp2_sigma_multiplier * predicted_sigma * entry_price
    
    if side == "BUY":
        tp1 = entry_price + tp1_move
        tp2 = entry_price + tp2_move
    else:  # SELL
        tp1 = entry_price - tp1_move
        tp2 = entry_price - tp2_move
    
    return (tp1, tp2)


def calculate_target_confidence(
    mu: float,
    sigma: float,
    target_return: float,
) -> float:
    """
    Calculate probability of reaching a target return using normal distribution CDF.
    
    Assumes returns are normally distributed with mean mu and standard deviation sigma.
    Confidence = P(Return >= target_return) = 1 - Φ((target_return - mu) / sigma)
    where Φ is the standard normal CDF.
    
    Args:
        mu: Expected return (e.g., 0.05 for 5% expected return)
        sigma: Standard deviation of returns (e.g., 0.20 for 20% volatility)
        target_return: Target return threshold (e.g., 0.10 for 10% target)
    
    Returns:
        Probability (0.0 to 1.0) of achieving target_return or higher
    
    Examples:
        >>> calculate_target_confidence(0.05, 0.20, 0.10)  # 5% expected, 20% vol, 10% target
        0.401  # ~40% chance
        >>> calculate_target_confidence(0.10, 0.15, 0.05)  # 10% expected, 15% vol, 5% target
        0.630  # ~63% chance
    """
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    
    # Standardize: z = (x - mu) / sigma
    z = (target_return - mu) / sigma
    
    # P(X >= target) = 1 - P(X < target) = 1 - Φ(z)
    confidence = 1.0 - _normal_cdf(z)
    
    # Clamp to [0, 1] to handle numerical edge cases
    return max(0.0, min(1.0, confidence))


def _normal_cdf(x: float) -> float:
    """
    Cumulative distribution function for standard normal distribution.
    
    Uses error function approximation for numerical stability.
    Φ(x) = 0.5 * (1 + erf(x / sqrt(2)))
    
    Args:
        x: Standardized value (z-score)
    
    Returns:
        Probability P(Z <= x) for standard normal Z
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: Literal["CALL", "PUT"],
) -> float:
    """
    Calculate option price using Black-Scholes formula.
    
    Black-Scholes formula:
        d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        d2 = d1 - σ√T
        Call = S*Φ(d1) - K*e^(-rT)*Φ(d2)
        Put = K*e^(-rT)*Φ(-d2) - S*Φ(-d1)
    
    Args:
        S: Current underlying price (spot price)
        K: Strike price
        T: Time to expiration in years (e.g., 30/365 for 30 days)
        r: Risk-free interest rate (annualized, e.g., 0.05 for 5%)
        sigma: Implied volatility (annualized, e.g., 0.25 for 25%)
        option_type: "CALL" or "PUT"
    
    Returns:
        Option premium (theoretical price)
    
    Examples:
        >>> black_scholes_price(100, 100, 0.25, 0.05, 0.20, "CALL")
        5.63  # ATM call with 3 months to expiry
        >>> black_scholes_price(100, 100, 0.25, 0.05, 0.20, "PUT")
        4.42  # ATM put (cheaper due to positive r)
    
    Notes:
        - Assumes no dividends (can be extended with dividend yield)
        - Uses continuous compounding for interest rate
        - Assumes log-normal price distribution
    """
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive")
    if T < 0:
        raise ValueError("T must be non-negative")
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    if option_type not in ("CALL", "PUT"):
        raise ValueError("option_type must be 'CALL' or 'PUT'")
    
    # Handle edge case: option expired (T = 0)
    if T == 0:
        if option_type == "CALL":
            return max(0.0, S - K)
        else:
            return max(0.0, K - S)
    
    # Handle edge case: zero volatility
    if sigma == 0:
        discount_factor = math.exp(-r * T)
        forward_price = S / discount_factor
        if option_type == "CALL":
            return max(0.0, forward_price - K) * discount_factor
        else:
            return max(0.0, K - forward_price) * discount_factor
    
    # Calculate d1 and d2
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    
    # Calculate option price
    if option_type == "CALL":
        price = S * _normal_cdf(d1) - K * math.exp(-r * T) * _normal_cdf(d2)
    else:  # PUT
        price = K * math.exp(-r * T) * _normal_cdf(-d2) - S * _normal_cdf(-d1)
    
    return max(0.0, price)  # Option price cannot be negative


def calculate_option_target_premiums(
    current_underlying_price: float,
    underlying_targets: List[float],
    strike: float,
    time_to_expiry_years: float,
    risk_free_rate: float,
    implied_volatility: float,
    option_type: Literal["CALL", "PUT"],
    time_decay_days: List[float] = None,
) -> List[Dict[str, float]]:
    """
    Calculate option premium targets by repricing at underlying target levels.
    
    For each underlying target price, reprice the option using Black-Scholes
    to estimate the option premium at that level. Optionally accounts for
    time decay if target achievement times are provided.
    
    Args:
        current_underlying_price: Current spot price of underlying
        underlying_targets: List of target underlying prices (e.g., [TP1, TP2])
        strike: Option strike price
        time_to_expiry_years: Current time to expiration in years
        risk_free_rate: Risk-free interest rate (annualized)
        implied_volatility: Implied volatility (annualized)
        option_type: "CALL" or "PUT"
        time_decay_days: Optional list of days to reach each target (for time decay)
    
    Returns:
        List of dicts with keys:
            - underlying_target: Target underlying price
            - option_premium: Estimated option premium at target
            - return_pct: Return % from current option price
            - time_remaining_years: Time to expiry after decay (if provided)
    
    Examples:
        >>> current_price = 100.0
        >>> targets = [110.0, 120.0]
        >>> strike = 105.0
        >>> calculate_option_target_premiums(
        ...     current_price, targets, strike, 0.25, 0.05, 0.30, "CALL"
        ... )
        [
            {'underlying_target': 110.0, 'option_premium': 7.85, 'return_pct': 31.5, ...},
            {'underlying_target': 120.0, 'option_premium': 16.12, 'return_pct': 170.0, ...},
        ]
    """
    if not underlying_targets:
        return []
    
    # Calculate current option price as baseline
    current_option_price = black_scholes_price(
        S=current_underlying_price,
        K=strike,
        T=time_to_expiry_years,
        r=risk_free_rate,
        sigma=implied_volatility,
        option_type=option_type,
    )
    
    if current_option_price == 0:
        current_option_price = 0.01  # Avoid division by zero
    
    results = []
    
    for i, target_price in enumerate(underlying_targets):
        # Calculate time remaining if decay specified
        if time_decay_days and i < len(time_decay_days):
            days_elapsed = time_decay_days[i]
            years_elapsed = days_elapsed / 365.0
            time_remaining = max(0.0, time_to_expiry_years - years_elapsed)
        else:
            time_remaining = time_to_expiry_years
        
        # Reprice option at target underlying level
        target_option_price = black_scholes_price(
            S=target_price,
            K=strike,
            T=time_remaining,
            r=risk_free_rate,
            sigma=implied_volatility,
            option_type=option_type,
        )
        
        # Calculate return percentage
        return_pct = ((target_option_price - current_option_price) / current_option_price) * 100.0
        
        results.append({
            "underlying_target": round(target_price, 2),
            "option_premium": round(target_option_price, 4),
            "return_pct": round(return_pct, 2),
            "time_remaining_years": round(time_remaining, 4),
        })
    
    return results


# Convenience function for complete workflow
def calculate_full_targets(
    entry_price: float,
    predicted_sigma: float,
    side: Literal["BUY", "SELL"],
    mu: float,
    strike: float = None,
    time_to_expiry_years: float = None,
    risk_free_rate: float = 0.05,
    implied_volatility: float = None,
    option_type: Literal["CALL", "PUT"] = None,
    target_eta_days: List[float] = None,
) -> Dict:
    """
    Calculate complete target package for underlying and optional option position.
    
    Combines all target calculation functions into a single workflow:
    1. Calculate underlying targets (TP1, TP2)
    2. Calculate confidence for each target
    3. If option parameters provided, calculate option premium targets
    
    Args:
        entry_price: Entry price of underlying
        predicted_sigma: Predicted volatility (annualized)
        side: "BUY" or "SELL"
        mu: Expected return (for confidence calculation)
        strike: Option strike (required if calculating option targets)
        time_to_expiry_years: Time to expiry (required for option targets)
        risk_free_rate: Risk-free rate (default 0.05)
        implied_volatility: IV for option pricing (defaults to predicted_sigma)
        option_type: "CALL" or "PUT" (required for option targets)
        target_eta_days: Expected days to reach each target (for time decay)
    
    Returns:
        Dict with:
            - underlying_targets: {tp1: price, tp2: price}
            - confidences: {tp1: conf, tp2: conf}
            - option_targets: List of option premium targets (if applicable)
    
    Examples:
        >>> calculate_full_targets(
        ...     entry_price=100.0,
        ...     predicted_sigma=0.25,
        ...     side="BUY",
        ...     mu=0.10,
        ...     strike=105.0,
        ...     time_to_expiry_years=0.25,
        ...     option_type="CALL",
        ... )
        {
            'underlying_targets': {'tp1': 115.0, 'tp2': 125.0},
            'confidences': {'tp1': 0.63, 'tp2': 0.45},
            'option_targets': [
                {'underlying_target': 115.0, 'option_premium': 12.50, ...},
                {'underlying_target': 125.0, 'option_premium': 21.30, ...},
            ]
        }
    """
    # Calculate underlying targets
    tp1, tp2 = calculate_underlying_targets(entry_price, predicted_sigma, side)
    
    # Calculate target returns for confidence
    tp1_return = (tp1 - entry_price) / entry_price if side == "BUY" else (entry_price - tp1) / entry_price
    tp2_return = (tp2 - entry_price) / entry_price if side == "BUY" else (entry_price - tp2) / entry_price
    
    # Calculate confidences
    tp1_conf = calculate_target_confidence(mu, predicted_sigma, tp1_return)
    tp2_conf = calculate_target_confidence(mu, predicted_sigma, tp2_return)
    
    result = {
        "underlying_targets": {
            "tp1": round(tp1, 2),
            "tp2": round(tp2, 2),
        },
        "confidences": {
            "tp1": round(tp1_conf, 4),
            "tp2": round(tp2_conf, 4),
        },
    }
    
    # Calculate option targets if parameters provided
    if all([strike, time_to_expiry_years, option_type]):
        iv = implied_volatility if implied_volatility else predicted_sigma
        option_targets = calculate_option_target_premiums(
            current_underlying_price=entry_price,
            underlying_targets=[tp1, tp2],
            strike=strike,
            time_to_expiry_years=time_to_expiry_years,
            risk_free_rate=risk_free_rate,
            implied_volatility=iv,
            option_type=option_type,
            time_decay_days=target_eta_days,
        )
        result["option_targets"] = option_targets
    
    return result
