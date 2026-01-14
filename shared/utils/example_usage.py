"""
Example usage of the targets utility module.

Demonstrates all major functions with realistic scenarios.
"""

from targets import (
    calculate_underlying_targets,
    calculate_target_confidence,
    black_scholes_price,
    calculate_option_target_premiums,
    calculate_full_targets,
)


def example_1_underlying_targets():
    """Example 1: Calculate underlying price targets for a long position."""
    print("=" * 70)
    print("Example 1: Underlying Targets for Long Position")
    print("=" * 70)
    
    entry = 150.0
    sigma = 0.30  # 30% annualized volatility
    
    tp1, tp2 = calculate_underlying_targets(
        entry_price=entry,
        predicted_sigma=sigma,
        side="BUY",
    )
    
    print(f"Entry Price: ${entry}")
    print(f"Predicted Volatility: {sigma * 100:.1f}%")
    print(f"TP1 (0.6σ): ${tp1:.2f} (+{(tp1 - entry) / entry * 100:.1f}%)")
    print(f"TP2 (1.0σ): ${tp2:.2f} (+{(tp2 - entry) / entry * 100:.1f}%)")
    print()


def example_2_short_targets():
    """Example 2: Calculate targets for a short position."""
    print("=" * 70)
    print("Example 2: Underlying Targets for Short Position")
    print("=" * 70)
    
    entry = 200.0
    sigma = 0.25
    
    tp1, tp2 = calculate_underlying_targets(
        entry_price=entry,
        predicted_sigma=sigma,
        side="SELL",
    )
    
    print(f"Entry Price: ${entry}")
    print(f"Predicted Volatility: {sigma * 100:.1f}%")
    print(f"TP1 (0.6σ down): ${tp1:.2f} ({(tp1 - entry) / entry * 100:.1f}%)")
    print(f"TP2 (1.0σ down): ${tp2:.2f} ({(tp2 - entry) / entry * 100:.1f}%)")
    print()


def example_3_confidence():
    """Example 3: Calculate probability of reaching targets."""
    print("=" * 70)
    print("Example 3: Target Confidence Calculation")
    print("=" * 70)
    
    mu = 0.08  # 8% expected return
    sigma = 0.20  # 20% volatility
    
    targets = [0.05, 0.10, 0.15, 0.20]
    
    print(f"Expected Return: {mu * 100:.1f}%")
    print(f"Volatility: {sigma * 100:.1f}%")
    print("\nTarget Return | Confidence")
    print("-" * 30)
    
    for target in targets:
        conf = calculate_target_confidence(mu, sigma, target)
        print(f"{target * 100:>7.1f}%      | {conf * 100:>5.1f}%")
    print()


def example_4_black_scholes():
    """Example 4: Price options using Black-Scholes."""
    print("=" * 70)
    print("Example 4: Black-Scholes Option Pricing")
    print("=" * 70)
    
    S = 100.0  # Spot price
    strikes = [95, 100, 105]
    T = 45 / 365.0  # 45 days to expiry
    r = 0.05
    sigma = 0.30
    
    print(f"Underlying: ${S}")
    print(f"Time to Expiry: 45 days")
    print(f"IV: {sigma * 100:.0f}%")
    print(f"Risk-free Rate: {r * 100:.1f}%")
    print("\nStrike | Call Price | Put Price")
    print("-" * 40)
    
    for K in strikes:
        call = black_scholes_price(S, K, T, r, sigma, "CALL")
        put = black_scholes_price(S, K, T, r, sigma, "PUT")
        moneyness = "ITM" if K < S else ("ATM" if K == S else "OTM")
        print(f"${K:>3} {moneyness} | ${call:>9.2f}  | ${put:>8.2f}")
    print()


def example_5_option_targets():
    """Example 5: Calculate option premium targets at underlying price levels."""
    print("=" * 70)
    print("Example 5: Option Target Premiums")
    print("=" * 70)
    
    current_price = 100.0
    underlying_targets = [110.0, 120.0, 130.0]
    strike = 105.0
    T = 60 / 365.0  # 60 days
    r = 0.05
    iv = 0.35
    
    current_option = black_scholes_price(current_price, strike, T, r, iv, "CALL")
    
    print(f"Setup: $105 CALL, 60 DTE")
    print(f"Current Underlying: ${current_price}")
    print(f"Current Option Price: ${current_option:.2f}")
    print(f"IV: {iv * 100:.0f}%")
    print("\nOption Premium Targets (no time decay):")
    
    targets = calculate_option_target_premiums(
        current_underlying_price=current_price,
        underlying_targets=underlying_targets,
        strike=strike,
        time_to_expiry_years=T,
        risk_free_rate=r,
        implied_volatility=iv,
        option_type="CALL",
    )
    
    print("\nUnderlying | Option Premium | Return %")
    print("-" * 45)
    for t in targets:
        print(
            f"${t['underlying_target']:>6.2f}   | "
            f"${t['option_premium']:>13.2f}  | "
            f"{t['return_pct']:>6.1f}%"
        )
    print()


def example_6_option_targets_with_decay():
    """Example 6: Option targets accounting for time decay."""
    print("=" * 70)
    print("Example 6: Option Targets with Time Decay")
    print("=" * 70)
    
    current_price = 100.0
    underlying_targets = [110.0, 120.0]
    strike = 105.0
    T = 90 / 365.0  # 90 days
    r = 0.05
    iv = 0.30
    time_to_targets = [30, 60]  # Days to reach each target
    
    current_option = black_scholes_price(current_price, strike, T, r, iv, "CALL")
    
    print(f"Setup: $105 CALL, 90 DTE")
    print(f"Current Underlying: ${current_price}")
    print(f"Current Option Price: ${current_option:.2f}")
    print(f"\nAssuming TP1 in 30 days, TP2 in 60 days:")
    
    targets = calculate_option_target_premiums(
        current_underlying_price=current_price,
        underlying_targets=underlying_targets,
        strike=strike,
        time_to_expiry_years=T,
        risk_free_rate=r,
        implied_volatility=iv,
        option_type="CALL",
        time_decay_days=time_to_targets,
    )
    
    print("\nTarget | Days | DTE Left | Premium | Return %")
    print("-" * 55)
    for i, t in enumerate(targets):
        dte_left = int(t['time_remaining_years'] * 365)
        print(
            f"${t['underlying_target']:>5.2f} | "
            f"{time_to_targets[i]:>4} | "
            f"{dte_left:>8} | "
            f"${t['option_premium']:>6.2f}  | "
            f"{t['return_pct']:>6.1f}%"
        )
    print()


def example_7_complete_workflow():
    """Example 7: Complete target calculation workflow."""
    print("=" * 70)
    print("Example 7: Complete Workflow (Underlying + Option)")
    print("=" * 70)
    
    # Long NVDA position with call option
    result = calculate_full_targets(
        entry_price=500.0,
        predicted_sigma=0.40,  # High volatility stock
        side="BUY",
        mu=0.15,  # 15% expected return
        strike=520.0,
        time_to_expiry_years=60 / 365.0,
        risk_free_rate=0.05,
        implied_volatility=0.45,  # IV higher than historical vol
        option_type="CALL",
        target_eta_days=[20, 45],
    )
    
    print("Position: Long NVDA @ $500")
    print(f"Expected Return: 15%")
    print(f"Predicted Vol: 40%")
    print()
    
    print("Underlying Targets:")
    print(f"  TP1: ${result['underlying_targets']['tp1']} "
          f"(Confidence: {result['confidences']['tp1'] * 100:.1f}%)")
    print(f"  TP2: ${result['underlying_targets']['tp2']} "
          f"(Confidence: {result['confidences']['tp2'] * 100:.1f}%)")
    print()
    
    print("Option: $520 CALL, 60 DTE")
    print("Option Targets:")
    for i, ot in enumerate(result['option_targets'], 1):
        print(f"  TP{i} @ ${ot['underlying_target']}: "
              f"Premium ${ot['option_premium']:.2f} "
              f"({ot['return_pct']:+.1f}% return)")
    print()


def example_8_put_position():
    """Example 8: Short position with protective put."""
    print("=" * 70)
    print("Example 8: Short Position with Put Option")
    print("=" * 70)
    
    result = calculate_full_targets(
        entry_price=180.0,
        predicted_sigma=0.28,
        side="SELL",
        mu=0.06,
        strike=175.0,
        time_to_expiry_years=45 / 365.0,
        option_type="PUT",
    )
    
    print("Position: Short Stock @ $180")
    print(f"Expected Decline: 6%")
    print(f"Volatility: 28%")
    print()
    
    print("Underlying Targets (downside):")
    print(f"  TP1: ${result['underlying_targets']['tp1']} "
          f"(Confidence: {result['confidences']['tp1'] * 100:.1f}%)")
    print(f"  TP2: ${result['underlying_targets']['tp2']} "
          f"(Confidence: {result['confidences']['tp2'] * 100:.1f}%)")
    print()
    
    print("Put Option: $175 PUT, 45 DTE")
    print("Put Premium Targets:")
    for i, ot in enumerate(result['option_targets'], 1):
        print(f"  TP{i} @ ${ot['underlying_target']}: "
              f"Premium ${ot['option_premium']:.2f} "
              f"({ot['return_pct']:+.1f}% return)")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TARGET CALCULATION UTILITIES - USAGE EXAMPLES")
    print("=" * 70 + "\n")
    
    example_1_underlying_targets()
    example_2_short_targets()
    example_3_confidence()
    example_4_black_scholes()
    example_5_option_targets()
    example_6_option_targets_with_decay()
    example_7_complete_workflow()
    example_8_put_position()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
