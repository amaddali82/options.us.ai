"""
Integration test demonstrating real-world usage of targets module.

Shows complete workflow from trade idea to calculated targets with options.
"""

from targets import calculate_full_targets, black_scholes_price
from datetime import datetime, timedelta
import json


def test_trade_scenario_nvda_earnings():
    """Test: NVDA long position ahead of earnings with call option."""
    print("\n" + "="*70)
    print("SCENARIO 1: NVDA Earnings Play (Long + Call)")
    print("="*70)
    
    # Trade setup
    symbol = "NVDA"
    entry_price = 500.00
    predicted_vol = 0.45  # High vol due to earnings
    expected_return = 0.18  # 18% expected move
    
    # Option parameters
    strike = 520.0
    days_to_expiry = 45
    implied_vol = 0.50  # IV spike before earnings
    
    # Calculate targets
    result = calculate_full_targets(
        entry_price=entry_price,
        predicted_sigma=predicted_vol,
        side="BUY",
        mu=expected_return,
        strike=strike,
        time_to_expiry_years=days_to_expiry/365.0,
        risk_free_rate=0.05,
        implied_volatility=implied_vol,
        option_type="CALL",
        target_eta_days=[15, 30],  # TP1 in 2 weeks, TP2 in 1 month
    )
    
    # Display results
    print(f"\n📊 Setup:")
    print(f"   Symbol: {symbol}")
    print(f"   Entry: ${entry_price}")
    print(f"   Expected Return: {expected_return*100:.1f}%")
    print(f"   Predicted Vol: {predicted_vol*100:.0f}%")
    
    print(f"\n🎯 Underlying Targets:")
    tp1_price = result['underlying_targets']['tp1']
    tp2_price = result['underlying_targets']['tp2']
    tp1_conf = result['confidences']['tp1']
    tp2_conf = result['confidences']['tp2']
    
    print(f"   TP1: ${tp1_price:.2f} (+{(tp1_price-entry_price)/entry_price*100:.1f}%) "
          f"[{tp1_conf*100:.1f}% confidence]")
    print(f"   TP2: ${tp2_price:.2f} (+{(tp2_price-entry_price)/entry_price*100:.1f}%) "
          f"[{tp2_conf*100:.1f}% confidence]")
    
    print(f"\n📈 Option: ${strike} CALL, {days_to_expiry} DTE")
    print(f"   IV: {implied_vol*100:.0f}%")
    
    current_option = black_scholes_price(
        S=entry_price, K=strike, T=days_to_expiry/365.0,
        r=0.05, sigma=implied_vol, option_type="CALL"
    )
    print(f"   Entry Premium: ${current_option:.2f}")
    
    print(f"\n💰 Option Targets:")
    for i, ot in enumerate(result['option_targets'], 1):
        dte_left = int(ot['time_remaining_years'] * 365)
        print(f"   TP{i} @ ${ot['underlying_target']:.2f}: "
              f"Premium ${ot['option_premium']:.2f} "
              f"({ot['return_pct']:+.1f}% return, {dte_left} DTE left)")
    
    # Risk/reward analysis
    print(f"\n⚖️  Risk/Reward:")
    stock_tp2_return = (tp2_price - entry_price) / entry_price * 100
    option_tp2_return = result['option_targets'][1]['return_pct']
    print(f"   Stock TP2 Return: {stock_tp2_return:.1f}%")
    print(f"   Option TP2 Return: {option_tp2_return:.1f}%")
    print(f"   Leverage Multiplier: {option_tp2_return/stock_tp2_return:.1f}x")
    
    # Assertions
    assert tp1_price > entry_price
    assert tp2_price > tp1_price
    assert tp1_conf > tp2_conf
    assert result['option_targets'][1]['option_premium'] > result['option_targets'][0]['option_premium']
    
    print("\n✅ All assertions passed!")


def test_trade_scenario_spy_hedge():
    """Test: SPY short with put hedge."""
    print("\n" + "="*70)
    print("SCENARIO 2: SPY Market Correction (Short + Put)")
    print("="*70)
    
    # Trade setup
    symbol = "SPY"
    entry_price = 450.00
    predicted_vol = 0.18
    expected_decline = 0.08  # 8% expected decline
    
    # Put parameters
    strike = 445.0
    days_to_expiry = 60
    implied_vol = 0.22  # VIX elevated
    
    result = calculate_full_targets(
        entry_price=entry_price,
        predicted_sigma=predicted_vol,
        side="SELL",
        mu=expected_decline,
        strike=strike,
        time_to_expiry_years=days_to_expiry/365.0,
        risk_free_rate=0.05,
        implied_volatility=implied_vol,
        option_type="PUT",
        target_eta_days=[20, 40],
    )
    
    print(f"\n📊 Setup:")
    print(f"   Symbol: {symbol}")
    print(f"   Entry: ${entry_price}")
    print(f"   Expected Decline: {expected_decline*100:.1f}%")
    print(f"   Market Vol: {predicted_vol*100:.0f}%")
    
    print(f"\n🎯 Downside Targets:")
    tp1_price = result['underlying_targets']['tp1']
    tp2_price = result['underlying_targets']['tp2']
    
    print(f"   TP1: ${tp1_price:.2f} ({(tp1_price-entry_price)/entry_price*100:.1f}%) "
          f"[{result['confidences']['tp1']*100:.1f}% confidence]")
    print(f"   TP2: ${tp2_price:.2f} ({(tp2_price-entry_price)/entry_price*100:.1f}%) "
          f"[{result['confidences']['tp2']*100:.1f}% confidence]")
    
    current_put = black_scholes_price(
        S=entry_price, K=strike, T=days_to_expiry/365.0,
        r=0.05, sigma=implied_vol, option_type="PUT"
    )
    
    print(f"\n📉 Protective Put: ${strike} PUT, {days_to_expiry} DTE")
    print(f"   Entry Premium: ${current_put:.2f}")
    
    print(f"\n💰 Put Premium Targets:")
    for i, ot in enumerate(result['option_targets'], 1):
        print(f"   TP{i} @ ${ot['underlying_target']:.2f}: "
              f"Premium ${ot['option_premium']:.2f} "
              f"({ot['return_pct']:+.1f}% return)")
    
    # Assertions
    assert tp1_price < entry_price
    assert tp2_price < tp1_price
    assert result['option_targets'][1]['option_premium'] > result['option_targets'][0]['option_premium']
    
    print("\n✅ All assertions passed!")


def test_trade_scenario_aapl_neutral():
    """Test: AAPL moderate volatility, realistic targets."""
    print("\n" + "="*70)
    print("SCENARIO 3: AAPL Swing Trade (Moderate Vol)")
    print("="*70)
    
    # Trade setup
    entry_price = 180.00
    predicted_vol = 0.25
    expected_return = 0.10
    
    # Option setup
    strike = 185.0
    days_to_expiry = 30
    implied_vol = 0.28
    
    result = calculate_full_targets(
        entry_price=entry_price,
        predicted_sigma=predicted_vol,
        side="BUY",
        mu=expected_return,
        strike=strike,
        time_to_expiry_years=days_to_expiry/365.0,
        implied_volatility=implied_vol,
        option_type="CALL",
        target_eta_days=[10, 20],
    )
    
    print(f"\n📊 Setup: AAPL Swing Trade")
    print(f"   Entry: ${entry_price}")
    print(f"   Expected: {expected_return*100:.0f}% in {days_to_expiry} days")
    
    print(f"\n🎯 Targets:")
    for i, (name, price) in enumerate([
        ("TP1", result['underlying_targets']['tp1']),
        ("TP2", result['underlying_targets']['tp2'])
    ], 1):
        conf = result['confidences'][name.lower()]
        gain = (price - entry_price) / entry_price * 100
        print(f"   {name}: ${price:.2f} (+{gain:.1f}%, {conf*100:.1f}% conf)")
    
    print(f"\n📈 ${strike} CALL Targets:")
    for i, ot in enumerate(result['option_targets'], 1):
        days = [10, 20][i-1]
        print(f"   Day {days}: ${ot['option_premium']:.2f} "
              f"({ot['return_pct']:+.0f}% return)")
    
    # Calculate break-even
    current_call = black_scholes_price(
        entry_price, strike, days_to_expiry/365.0, 0.05, implied_vol, "CALL"
    )
    breakeven = entry_price + current_call
    
    print(f"\n⚖️  Analysis:")
    print(f"   Call Premium: ${current_call:.2f}")
    print(f"   Break-Even: ${breakeven:.2f} (+{(breakeven-entry_price)/entry_price*100:.1f}%)")
    print(f"   TP1 exceeds B/E: {result['underlying_targets']['tp1'] > breakeven}")
    
    assert result['underlying_targets']['tp1'] > breakeven
    print("\n✅ All assertions passed!")


def test_json_serialization():
    """Test that results can be serialized to JSON."""
    print("\n" + "="*70)
    print("SCENARIO 4: JSON Serialization Test")
    print("="*70)
    
    result = calculate_full_targets(
        entry_price=100.0,
        predicted_sigma=0.30,
        side="BUY",
        mu=0.12,
        strike=105.0,
        time_to_expiry_years=45/365.0,
        option_type="CALL",
    )
    
    # Convert to JSON
    json_str = json.dumps(result, indent=2)
    
    print("\n📄 JSON Output (sample):")
    print(json_str[:300] + "...")
    
    # Parse back
    parsed = json.loads(json_str)
    
    print("\n✅ JSON serialization successful!")
    print(f"   Keys: {list(parsed.keys())}")
    print(f"   TP1: ${parsed['underlying_targets']['tp1']}")
    print(f"   Options: {len(parsed['option_targets'])} targets")
    
    assert parsed['underlying_targets']['tp1'] == result['underlying_targets']['tp1']
    assert len(parsed['option_targets']) == 2


def run_all_scenarios():
    """Run all integration test scenarios."""
    print("\n" + "="*70)
    print("TARGET UTILITIES - INTEGRATION TESTS")
    print("="*70)
    
    scenarios = [
        test_trade_scenario_nvda_earnings,
        test_trade_scenario_spy_hedge,
        test_trade_scenario_aapl_neutral,
        test_json_serialization,
    ]
    
    for scenario in scenarios:
        try:
            scenario()
        except AssertionError as e:
            print(f"\n❌ FAILED: {scenario.__name__}")
            print(f"   Error: {e}")
            raise
        except Exception as e:
            print(f"\n❌ ERROR in {scenario.__name__}")
            print(f"   {type(e).__name__}: {e}")
            raise
    
    print("\n" + "="*70)
    print("🎉 ALL INTEGRATION TESTS PASSED!")
    print("="*70)
    print(f"\nRan {len(scenarios)} scenarios successfully:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario.__doc__.strip()}")
    print()


if __name__ == "__main__":
    run_all_scenarios()
