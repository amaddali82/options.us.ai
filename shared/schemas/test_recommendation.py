"""
Test validation rules for recommendation schemas
Demonstrates strong typing and validation features
"""

from recommendation import (
    Recommendation, Target, Stop, OptionIdea, OptionTarget, Greeks, OptionType,
    get_recommendation_schema, get_all_schemas
)
from datetime import date
import json


def test_validation_rules():
    """Test various validation rules"""
    print("=" * 60)
    print("TESTING VALIDATION RULES")
    print("=" * 60)
    
    # Test 1: Valid BUY recommendation
    print("\n✅ Test 1: Valid BUY recommendation with options")
    try:
        rec = Recommendation(
            symbol="aapl",  # Will be converted to uppercase
            recommendation_type="BUY",
            confidence_overall=0.85,
            current_price=175.50,
            targets=[
                Target(price=180.00, confidence=0.80),
                Target(price=185.00, confidence=0.60),
            ],
            stop_loss=Stop(price=170.00, confidence=0.90, stop_type="hard"),
            option_idea=OptionIdea(
                option_type=OptionType.CALL,
                symbol="AAPL",
                expiry=date(2026, 3, 20),
                strike=180.0,
                entry_premium=5.50,
                greeks=Greeks(delta=0.60, gamma=0.02, theta=-0.04, vega=0.15),
                implied_volatility=0.30,
                option_targets=[
                    OptionTarget(premium=8.00, confidence=0.75),
                    OptionTarget(premium=10.50, confidence=0.55),
                ]
            ),
            reasoning="Strong technical setup with positive momentum indicators",
        )
        print(f"   Symbol: {rec.symbol} (auto-uppercased)")
        print(f"   Targets sorted: {[t.price for t in rec.targets]}")
        print(f"   ✅ Validation passed!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Invalid - targets not sorted
    print("\n❌ Test 2: Targets must be sorted (BUY = ascending)")
    try:
        rec = Recommendation(
            symbol="TSLA",
            recommendation_type="BUY",
            confidence_overall=0.75,
            current_price=200.00,
            targets=[
                Target(price=220.00, confidence=0.80),
                Target(price=210.00, confidence=0.70),  # Wrong order!
            ],
            reasoning="Test unsorted targets",
        )
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 3: Invalid - target below current price for BUY
    print("\n❌ Test 3: BUY targets must be above current price")
    try:
        rec = Recommendation(
            symbol="MSFT",
            recommendation_type="BUY",
            confidence_overall=0.80,
            current_price=375.00,
            targets=[
                Target(price=370.00, confidence=0.85),  # Below current!
            ],
            reasoning="Test invalid target direction",
        )
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 4: Invalid - expiry in the past
    print("\n❌ Test 4: Option expiry must be in future")
    try:
        option = OptionIdea(
            option_type=OptionType.PUT,
            symbol="SPY",
            expiry=date(2025, 1, 1),  # Past date!
            strike=450.0,
            entry_premium=10.0,
            greeks=Greeks(delta=-0.40),
            implied_volatility=0.25,
            option_targets=[
                OptionTarget(premium=15.0, confidence=0.70),
            ]
        )
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 5: Invalid - confidence out of bounds
    print("\n❌ Test 5: Confidence must be in [0, 1]")
    try:
        target = Target(price=100.0, confidence=1.5)  # > 1.0!
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 6: Invalid - negative price
    print("\n❌ Test 6: Prices must be positive")
    try:
        target = Target(price=-50.0, confidence=0.8)  # Negative!
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 7: Invalid - option targets not sorted
    print("\n❌ Test 7: Option targets must be sorted by premium")
    try:
        option = OptionIdea(
            option_type=OptionType.CALL,
            symbol="NVDA",
            expiry=date(2026, 4, 17),
            strike=500.0,
            entry_premium=20.0,
            greeks=Greeks(delta=0.55),
            implied_volatility=0.40,
            option_targets=[
                OptionTarget(premium=30.0, confidence=0.70),
                OptionTarget(premium=25.0, confidence=0.80),  # Wrong order!
            ]
        )
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 8: Invalid - first target below entry
    print("\n❌ Test 8: First option target must be above entry premium")
    try:
        option = OptionIdea(
            option_type=OptionType.CALL,
            symbol="AMD",
            expiry=date(2026, 5, 15),
            strike=150.0,
            entry_premium=10.0,
            greeks=Greeks(delta=0.50),
            implied_volatility=0.35,
            option_targets=[
                OptionTarget(premium=8.0, confidence=0.70),  # Below entry!
            ]
        )
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 9: Invalid - option symbol doesn't match recommendation
    print("\n❌ Test 9: Option symbol must match recommendation symbol")
    try:
        rec = Recommendation(
            symbol="AAPL",
            recommendation_type="BUY",
            confidence_overall=0.80,
            current_price=175.00,
            targets=[Target(price=180.00, confidence=0.75)],
            option_idea=OptionIdea(
                option_type=OptionType.CALL,
                symbol="TSLA",  # Doesn't match!
                expiry=date(2026, 3, 20),
                strike=180.0,
                entry_premium=5.0,
                greeks=Greeks(delta=0.60),
                implied_volatility=0.30,
                option_targets=[OptionTarget(premium=8.0, confidence=0.70)]
            ),
            reasoning="Test symbol mismatch",
        )
        print("   ❌ Should have failed!")
    except ValueError as e:
        print(f"   ✅ Caught validation error: {str(e)[:80]}...")
    
    # Test 10: Valid SELL recommendation
    print("\n✅ Test 10: Valid SELL recommendation")
    try:
        rec = Recommendation(
            symbol="XYZ",
            recommendation_type="SELL",
            confidence_overall=0.70,
            current_price=100.00,
            targets=[
                Target(price=95.00, confidence=0.75),  # Descending for SELL
                Target(price=90.00, confidence=0.60),
            ],
            stop_loss=Stop(price=105.00, confidence=0.85, stop_type="hard"),
            reasoning="Bearish technical setup",
        )
        print(f"   Targets (descending): {[t.price for t in rec.targets]}")
        print(f"   Stop above current: ${rec.stop_loss.price:.2f} > ${rec.current_price:.2f}")
        print(f"   ✅ Validation passed!")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_json_schema_export():
    """Test JSON schema export functionality"""
    print("\n" + "=" * 60)
    print("TESTING JSON SCHEMA EXPORT")
    print("=" * 60)
    
    # Get single schema
    rec_schema = get_recommendation_schema()
    print(f"\n✅ Recommendation schema exported")
    print(f"   Properties: {len(rec_schema.get('properties', {}))} fields")
    print(f"   Required: {len(rec_schema.get('required', []))} fields")
    
    # Get all schemas
    all_schemas = get_all_schemas()
    print(f"\n✅ All schemas exported")
    print(f"   Models: {list(all_schemas.keys())}")
    
    # Pretty print a sample
    print("\n📋 Sample - Target schema:")
    target_schema = all_schemas['Target']
    print(f"   Title: {target_schema.get('title')}")
    print(f"   Properties: {list(target_schema.get('properties', {}).keys())}")
    
    # Save to file
    with open('test_schemas.json', 'w') as f:
        json.dump(all_schemas, f, indent=2, default=str)
    print(f"\n✅ Schemas saved to test_schemas.json")


def test_complex_scenario():
    """Test a complex real-world scenario"""
    print("\n" + "=" * 60)
    print("COMPLEX REAL-WORLD SCENARIO")
    print("=" * 60)
    
    rec = Recommendation(
        symbol="NVDA",
        recommendation_type="BUY",
        confidence_overall=0.88,
        current_price=495.50,
        entry_price=498.00,
        targets=[
            Target(price=520.00, confidence=0.85, timeframe_days=10, 
                   reasoning="First resistance breakout"),
            Target(price=545.00, confidence=0.70, timeframe_days=20,
                   reasoning="Fibonacci 1.618 extension"),
            Target(price=575.00, confidence=0.55, timeframe_days=35,
                   reasoning="Major psychological level"),
            Target(price=600.00, confidence=0.40, timeframe_days=50,
                   reasoning="Long-term target"),
        ],
        stop_loss=Stop(
            price=475.00,
            confidence=0.92,
            stop_type="trailing",
            reasoning="Below breakout support with volume confirmation"
        ),
        option_idea=OptionIdea(
            option_type=OptionType.CALL,
            symbol="NVDA",
            expiry=date(2026, 3, 20),
            strike=510.0,
            entry_premium=28.50,
            contracts=3,
            greeks=Greeks(
                delta=0.62,
                gamma=0.018,
                theta=-0.42,
                vega=0.95,
                rho=0.35
            ),
            implied_volatility=0.45,
            option_targets=[
                OptionTarget(
                    premium=42.00,
                    confidence=0.80,
                    profit_percentage=47.4,
                    underlying_price=525.00
                ),
                OptionTarget(
                    premium=58.50,
                    confidence=0.60,
                    profit_percentage=105.3,
                    underlying_price=550.00
                ),
                OptionTarget(
                    premium=78.00,
                    confidence=0.40,
                    profit_percentage=173.7,
                    underlying_price=580.00
                ),
            ],
            stop_loss_premium=18.00,
            max_loss_dollars=3150.00,  # (28.50 - 18.00) * 100 * 3 contracts
            reasoning="High delta calls to leverage upside with defined risk. Strong momentum play."
        ),
        timeframe="1-2 months",
        risk_reward_ratio=4.2,
        catalysts=[
            "Q4 earnings in 2 weeks - expecting beat",
            "New AI chip announcement",
            "Major cloud provider partnerships",
            "Analyst upgrades from 3 major firms"
        ],
        risks=[
            "Semiconductor sector rotation",
            "China export restrictions",
            "Profit taking after strong run",
            "High valuation concerns"
        ],
        reasoning="""
        NVDA showing exceptional strength with bullish technical setup:
        - Breakout above 490 resistance on strong volume
        - RSI at 68 showing momentum without overbought
        - MACD crossover confirming trend
        - 50-day MA providing strong support at 475
        
        Fundamental catalysts aligned:
        - Q4 earnings expected to beat by 8-12%
        - AI chip demand accelerating across cloud providers
        - Gross margins expanding to 75%+
        
        Options strategy provides 4:1 risk/reward with defined downside.
        Target 1 offers conservative 47% gain, Target 3 gives 174% upside.
        """,
        indicators_used=["RSI", "MACD", "Volume Profile", "Moving Averages", "Fibonacci"],
        analyst="AI Trading Intelligence v1.0"
    )
    
    print(f"\n📊 Complete Trading Recommendation")
    print(f"   Symbol: {rec.symbol}")
    print(f"   Action: {rec.recommendation_type}")
    print(f"   Overall Confidence: {rec.confidence_overall:.1%}")
    print(f"   Current: ${rec.current_price:.2f} → Entry: ${rec.entry_price:.2f}")
    print(f"\n   🎯 Price Targets ({len(rec.targets)}):")
    for i, t in enumerate(rec.targets, 1):
        print(f"      T{i}: ${t.price:.2f} ({t.confidence:.0%} confidence, {t.timeframe_days}d)")
    print(f"\n   🛑 Stop Loss: ${rec.stop_loss.price:.2f} ({rec.stop_loss.stop_type})")
    print(f"\n   📈 Options Strategy:")
    print(f"      {rec.option_idea.option_type.value} ${rec.option_idea.strike} exp {rec.option_idea.expiry}")
    print(f"      Entry: ${rec.option_idea.entry_premium:.2f}")
    print(f"      Contracts: {rec.option_idea.contracts}")
    print(f"      Delta: {rec.option_idea.greeks.delta:.2f}")
    print(f"      IV: {rec.option_idea.implied_volatility:.1%}")
    print(f"\n   💰 Option Targets ({len(rec.option_idea.option_targets)}):")
    for i, t in enumerate(rec.option_idea.option_targets, 1):
        print(f"      T{i}: ${t.premium:.2f} (+{t.profit_percentage:.1f}%, {t.confidence:.0%} conf)")
    print(f"\n   📊 Risk Management:")
    print(f"      Risk/Reward: {rec.risk_reward_ratio:.1f}:1")
    print(f"      Max Loss: ${rec.option_idea.max_loss_dollars:,.2f}")
    print(f"\n   🚀 Catalysts: {len(rec.catalysts)}")
    for cat in rec.catalysts:
        print(f"      • {cat}")
    print(f"\n   ⚠️  Risks: {len(rec.risks)}")
    for risk in rec.risks:
        print(f"      • {risk}")
    
    # Export to JSON
    json_output = rec.model_dump_json(indent=2)
    print(f"\n   ✅ Full recommendation JSON: {len(json_output)} bytes")
    
    # Save to file
    with open('sample_recommendation.json', 'w') as f:
        f.write(json_output)
    print(f"   ✅ Saved to sample_recommendation.json")


if __name__ == "__main__":
    test_validation_rules()
    test_json_schema_export()
    test_complex_scenario()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
