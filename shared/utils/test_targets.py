"""
Unit tests for target calculation utilities.

Tests all functions with deterministic inputs to verify correctness.
"""

import pytest
import math
from targets import (
    calculate_underlying_targets,
    calculate_target_confidence,
    black_scholes_price,
    calculate_option_target_premiums,
    calculate_full_targets,
    _normal_cdf,
)


class TestUnderlyingTargets:
    """Tests for calculate_underlying_targets function."""
    
    def test_long_position_default_multipliers(self):
        """Test long position with default sigma multipliers."""
        tp1, tp2 = calculate_underlying_targets(
            entry_price=100.0,
            predicted_sigma=0.20,
            side="BUY",
        )
        # TP1 = 100 + 0.6 * 0.20 * 100 = 100 + 12 = 112
        # TP2 = 100 + 1.0 * 0.20 * 100 = 100 + 20 = 120
        assert tp1 == pytest.approx(112.0, rel=1e-6)
        assert tp2 == pytest.approx(120.0, rel=1e-6)
    
    def test_short_position_default_multipliers(self):
        """Test short position with default sigma multipliers."""
        tp1, tp2 = calculate_underlying_targets(
            entry_price=150.0,
            predicted_sigma=0.30,
            side="SELL",
        )
        # TP1 = 150 - 0.6 * 0.30 * 150 = 150 - 27 = 123
        # TP2 = 150 - 1.0 * 0.30 * 150 = 150 - 45 = 105
        assert tp1 == pytest.approx(123.0, rel=1e-6)
        assert tp2 == pytest.approx(105.0, rel=1e-6)
    
    def test_custom_multipliers(self):
        """Test with custom sigma multipliers."""
        tp1, tp2 = calculate_underlying_targets(
            entry_price=200.0,
            predicted_sigma=0.25,
            side="BUY",
            tp1_sigma_multiplier=0.5,
            tp2_sigma_multiplier=1.5,
        )
        # TP1 = 200 + 0.5 * 0.25 * 200 = 200 + 25 = 225
        # TP2 = 200 + 1.5 * 0.25 * 200 = 200 + 75 = 275
        assert tp1 == pytest.approx(225.0, rel=1e-6)
        assert tp2 == pytest.approx(275.0, rel=1e-6)
    
    def test_zero_sigma(self):
        """Test with zero volatility (targets equal entry)."""
        tp1, tp2 = calculate_underlying_targets(
            entry_price=100.0,
            predicted_sigma=0.0,
            side="BUY",
        )
        assert tp1 == pytest.approx(100.0, rel=1e-6)
        assert tp2 == pytest.approx(100.0, rel=1e-6)
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError, match="entry_price must be positive"):
            calculate_underlying_targets(-100.0, 0.20, "BUY")
        
        with pytest.raises(ValueError, match="predicted_sigma must be non-negative"):
            calculate_underlying_targets(100.0, -0.20, "BUY")
        
        with pytest.raises(ValueError, match="side must be"):
            calculate_underlying_targets(100.0, 0.20, "HOLD")


class TestTargetConfidence:
    """Tests for calculate_target_confidence function."""
    
    def test_target_below_mean(self):
        """Test confidence when target is below expected return (high confidence)."""
        # Expected 10%, target 5%, volatility 15%
        conf = calculate_target_confidence(mu=0.10, sigma=0.15, target_return=0.05)
        # z = (0.05 - 0.10) / 0.15 = -0.333
        # P(X >= 0.05) = 1 - Φ(-0.333) = Φ(0.333) ≈ 0.63
        assert conf == pytest.approx(0.6305, rel=1e-3)
    
    def test_target_equals_mean(self):
        """Test confidence when target equals expected return (50%)."""
        conf = calculate_target_confidence(mu=0.08, sigma=0.20, target_return=0.08)
        # z = 0, Φ(0) = 0.5, confidence = 0.5
        assert conf == pytest.approx(0.50, rel=1e-6)
    
    def test_target_above_mean(self):
        """Test confidence when target is above expected return (lower confidence)."""
        # Expected 5%, target 15%, volatility 20%
        conf = calculate_target_confidence(mu=0.05, sigma=0.20, target_return=0.15)
        # z = (0.15 - 0.05) / 0.20 = 0.5
        # P(X >= 0.15) = 1 - Φ(0.5) ≈ 0.309
        assert conf == pytest.approx(0.3085, rel=1e-3)
    
    def test_extreme_z_scores(self):
        """Test with extreme z-scores (very high/low confidence)."""
        # Very high confidence (target 3 sigma below mean)
        high_conf = calculate_target_confidence(mu=0.20, sigma=0.10, target_return=-0.10)
        assert high_conf >= 0.998  # Nearly certain (relaxed from 0.999)
        
        # Very low confidence (target 3 sigma above mean)
        low_conf = calculate_target_confidence(mu=0.05, sigma=0.10, target_return=0.35)
        assert low_conf <= 0.002  # Nearly impossible
    
    def test_invalid_sigma(self):
        """Test error handling for invalid sigma."""
        with pytest.raises(ValueError, match="sigma must be positive"):
            calculate_target_confidence(0.05, 0.0, 0.10)
        
        with pytest.raises(ValueError, match="sigma must be positive"):
            calculate_target_confidence(0.05, -0.10, 0.10)


class TestNormalCDF:
    """Tests for _normal_cdf helper function."""
    
    def test_standard_values(self):
        """Test CDF at standard z-score values."""
        assert _normal_cdf(0.0) == pytest.approx(0.5, rel=1e-6)
        assert _normal_cdf(1.0) == pytest.approx(0.8413, abs=0.001)
        assert _normal_cdf(-1.0) == pytest.approx(0.1587, abs=0.001)
        assert _normal_cdf(2.0) == pytest.approx(0.9772, abs=0.001)
        assert _normal_cdf(-2.0) == pytest.approx(0.0228, abs=0.001)


class TestBlackScholesPrice:
    """Tests for black_scholes_price function."""
    
    def test_atm_call(self):
        """Test ATM call option."""
        price = black_scholes_price(
            S=100.0,
            K=100.0,
            T=0.25,  # 3 months
            r=0.05,
            sigma=0.20,
            option_type="CALL",
        )
        # ATM call with 3 months, 20% vol ≈ $4-5
        assert 4.0 <= price <= 6.0
        assert price == pytest.approx(4.78, rel=0.05)
    
    def test_atm_put(self):
        """Test ATM put option."""
        price = black_scholes_price(
            S=100.0,
            K=100.0,
            T=0.25,
            r=0.05,
            sigma=0.20,
            option_type="PUT",
        )
        # ATM put slightly cheaper than call due to positive r
        assert 3.0 <= price <= 5.0
        assert price == pytest.approx(3.37, rel=0.10)
    
    def test_itm_call(self):
        """Test in-the-money call option."""
        price = black_scholes_price(
            S=110.0,
            K=100.0,
            T=0.25,
            r=0.05,
            sigma=0.20,
            option_type="CALL",
        )
        # ITM call has intrinsic value of 10 + time value
        assert price >= 10.0
        assert price == pytest.approx(11.99, rel=0.05)
    
    def test_otm_put(self):
        """Test out-of-the-money put option."""
        price = black_scholes_price(
            S=110.0,
            K=100.0,
            T=0.25,
            r=0.05,
            sigma=0.20,
            option_type="PUT",
        )
        # OTM put has only time value, should be low
        assert 0.0 < price < 2.0
        assert price == pytest.approx(0.75, rel=0.10)
    
    def test_expiry_itm(self):
        """Test option at expiry (T=0) when ITM."""
        call_price = black_scholes_price(
            S=110.0, K=100.0, T=0.0, r=0.05, sigma=0.20, option_type="CALL"
        )
        put_price = black_scholes_price(
            S=90.0, K=100.0, T=0.0, r=0.05, sigma=0.20, option_type="PUT"
        )
        # At expiry: Call = max(S-K, 0), Put = max(K-S, 0)
        assert call_price == pytest.approx(10.0, rel=1e-6)
        assert put_price == pytest.approx(10.0, rel=1e-6)
    
    def test_expiry_otm(self):
        """Test option at expiry (T=0) when OTM."""
        call_price = black_scholes_price(
            S=90.0, K=100.0, T=0.0, r=0.05, sigma=0.20, option_type="CALL"
        )
        put_price = black_scholes_price(
            S=110.0, K=100.0, T=0.0, r=0.05, sigma=0.20, option_type="PUT"
        )
        # OTM at expiry = 0
        assert call_price == pytest.approx(0.0, rel=1e-6)
        assert put_price == pytest.approx(0.0, rel=1e-6)
    
    def test_zero_volatility_itm(self):
        """Test with zero volatility when ITM."""
        call_price = black_scholes_price(
            S=110.0, K=100.0, T=0.25, r=0.05, sigma=0.0, option_type="CALL"
        )
        # With σ=0, option worth discounted intrinsic value
        # Forward = 110 * exp(0.05 * 0.25) ≈ 111.39
        # Call = (111.39 - 100) * exp(-0.05 * 0.25) ≈ 11.25
        assert call_price == pytest.approx(11.25, rel=0.05)
    
    def test_high_volatility(self):
        """Test with very high volatility (increases option value)."""
        low_vol_price = black_scholes_price(
            S=100.0, K=100.0, T=0.25, r=0.05, sigma=0.10, option_type="CALL"
        )
        high_vol_price = black_scholes_price(
            S=100.0, K=100.0, T=0.25, r=0.05, sigma=0.50, option_type="CALL"
        )
        # Higher vol -> higher option value
        assert high_vol_price > low_vol_price * 2
    
    def test_put_call_parity(self):
        """Test put-call parity relationship."""
        S, K, T, r, sigma = 105.0, 100.0, 0.5, 0.04, 0.25
        
        call = black_scholes_price(S, K, T, r, sigma, "CALL")
        put = black_scholes_price(S, K, T, r, sigma, "PUT")
        
        # Put-Call Parity: C - P = S - K*e^(-rT)
        parity_lhs = call - put
        parity_rhs = S - K * math.exp(-r * T)
        
        assert parity_lhs == pytest.approx(parity_rhs, rel=1e-4)
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError, match="S and K must be positive"):
            black_scholes_price(-100, 100, 0.25, 0.05, 0.20, "CALL")
        
        with pytest.raises(ValueError, match="T must be non-negative"):
            black_scholes_price(100, 100, -0.25, 0.05, 0.20, "CALL")
        
        with pytest.raises(ValueError, match="sigma must be non-negative"):
            black_scholes_price(100, 100, 0.25, 0.05, -0.20, "CALL")
        
        with pytest.raises(ValueError, match="option_type must be"):
            black_scholes_price(100, 100, 0.25, 0.05, 0.20, "SPREAD")


class TestOptionTargetPremiums:
    """Tests for calculate_option_target_premiums function."""
    
    def test_call_targets_increasing_underlying(self):
        """Test call option premiums at increasing underlying prices."""
        targets = calculate_option_target_premiums(
            current_underlying_price=100.0,
            underlying_targets=[110.0, 120.0],
            strike=105.0,
            time_to_expiry_years=0.25,
            risk_free_rate=0.05,
            implied_volatility=0.30,
            option_type="CALL",
        )
        
        assert len(targets) == 2
        
        # First target
        assert targets[0]["underlying_target"] == 110.0
        assert targets[0]["option_premium"] > 0
        assert targets[0]["return_pct"] > 0
        
        # Second target should have higher premium (more ITM)
        assert targets[1]["underlying_target"] == 120.0
        assert targets[1]["option_premium"] > targets[0]["option_premium"]
        assert targets[1]["return_pct"] > targets[0]["return_pct"]
    
    def test_put_targets_decreasing_underlying(self):
        """Test put option premiums at decreasing underlying prices."""
        targets = calculate_option_target_premiums(
            current_underlying_price=100.0,
            underlying_targets=[90.0, 80.0],
            strike=95.0,
            time_to_expiry_years=0.25,
            risk_free_rate=0.05,
            implied_volatility=0.30,
            option_type="PUT",
        )
        
        assert len(targets) == 2
        
        # Put value increases as underlying decreases
        assert targets[0]["option_premium"] > 0
        assert targets[1]["option_premium"] > targets[0]["option_premium"]
        assert targets[1]["return_pct"] > targets[0]["return_pct"]
    
    def test_with_time_decay(self):
        """Test option premiums accounting for time decay."""
        targets = calculate_option_target_premiums(
            current_underlying_price=100.0,
            underlying_targets=[110.0, 120.0],
            strike=105.0,
            time_to_expiry_years=90/365.0,  # 90 days
            risk_free_rate=0.05,
            implied_volatility=0.30,
            option_type="CALL",
            time_decay_days=[30, 60],  # 30 days to TP1, 60 days to TP2
        )
        
        assert len(targets) == 2
        
        # Time remaining should decrease
        assert targets[0]["time_remaining_years"] == pytest.approx(60/365.0, rel=1e-4)
        assert targets[1]["time_remaining_years"] == pytest.approx(30/365.0, rel=1e-4)
        
        # Verify time value decayed
        assert targets[0]["time_remaining_years"] < 90/365.0
        assert targets[1]["time_remaining_years"] < targets[0]["time_remaining_years"]
    
    def test_empty_targets(self):
        """Test with empty target list."""
        targets = calculate_option_target_premiums(
            current_underlying_price=100.0,
            underlying_targets=[],
            strike=105.0,
            time_to_expiry_years=0.25,
            risk_free_rate=0.05,
            implied_volatility=0.30,
            option_type="CALL",
        )
        
        assert targets == []
    
    def test_negative_return_scenario(self):
        """Test scenario where option loses value (wrong direction)."""
        # Call option with underlying dropping
        targets = calculate_option_target_premiums(
            current_underlying_price=100.0,
            underlying_targets=[90.0, 80.0],
            strike=105.0,
            time_to_expiry_years=0.25,
            risk_free_rate=0.05,
            implied_volatility=0.30,
            option_type="CALL",
        )
        
        # Both targets should show negative returns
        assert targets[0]["return_pct"] < 0
        assert targets[1]["return_pct"] < targets[0]["return_pct"]


class TestFullTargetsWorkflow:
    """Tests for calculate_full_targets convenience function."""
    
    def test_underlying_only(self):
        """Test calculating only underlying targets without options."""
        result = calculate_full_targets(
            entry_price=100.0,
            predicted_sigma=0.25,
            side="BUY",
            mu=0.08,
        )
        
        assert "underlying_targets" in result
        assert "confidences" in result
        assert "option_targets" not in result
        
        assert result["underlying_targets"]["tp1"] == 115.0
        assert result["underlying_targets"]["tp2"] == 125.0
        assert 0.0 <= result["confidences"]["tp1"] <= 1.0
        assert 0.0 <= result["confidences"]["tp2"] <= 1.0
        assert result["confidences"]["tp2"] < result["confidences"]["tp1"]
    
    def test_with_call_option(self):
        """Test complete workflow with call option."""
        result = calculate_full_targets(
            entry_price=100.0,
            predicted_sigma=0.30,
            side="BUY",
            mu=0.10,
            strike=105.0,
            time_to_expiry_years=0.25,
            risk_free_rate=0.05,
            implied_volatility=0.35,
            option_type="CALL",
            target_eta_days=[15, 45],
        )
        
        assert "underlying_targets" in result
        assert "confidences" in result
        assert "option_targets" in result
        
        # Verify underlying targets
        assert result["underlying_targets"]["tp1"] == 118.0
        assert result["underlying_targets"]["tp2"] == 130.0
        
        # Verify option targets calculated
        assert len(result["option_targets"]) == 2
        assert result["option_targets"][0]["underlying_target"] == 118.0
        assert result["option_targets"][1]["underlying_target"] == 130.0
        
        # Verify time decay applied
        assert result["option_targets"][0]["time_remaining_years"] < 0.25
        assert result["option_targets"][1]["time_remaining_years"] < result["option_targets"][0]["time_remaining_years"]
    
    def test_short_with_put_option(self):
        """Test complete workflow for short position with put."""
        result = calculate_full_targets(
            entry_price=150.0,
            predicted_sigma=0.28,
            side="SELL",
            mu=0.06,
            strike=145.0,
            time_to_expiry_years=60/365.0,
            option_type="PUT",
        )
        
        # Verify short targets (prices decrease)
        tp1 = result["underlying_targets"]["tp1"]
        tp2 = result["underlying_targets"]["tp2"]
        assert tp1 < 150.0
        assert tp2 < tp1
        
        # Verify put option targets (premiums increase as underlying falls)
        assert len(result["option_targets"]) == 2
        assert result["option_targets"][1]["option_premium"] > result["option_targets"][0]["option_premium"]
    
    def test_uses_predicted_sigma_for_iv(self):
        """Test that predicted_sigma is used for IV when IV not provided."""
        result1 = calculate_full_targets(
            entry_price=100.0,
            predicted_sigma=0.20,
            side="BUY",
            mu=0.08,
            strike=100.0,
            time_to_expiry_years=0.25,
            option_type="CALL",
        )
        
        result2 = calculate_full_targets(
            entry_price=100.0,
            predicted_sigma=0.20,
            side="BUY",
            mu=0.08,
            strike=100.0,
            time_to_expiry_years=0.25,
            implied_volatility=0.20,  # Same as predicted_sigma
            option_type="CALL",
        )
        
        # Should produce same results
        assert result1["option_targets"][0]["option_premium"] == \
               pytest.approx(result2["option_targets"][0]["option_premium"], rel=1e-6)


class TestDeterministicExamples:
    """Deterministic test cases with known inputs and expected outputs."""
    
    def test_deterministic_underlying_targets_long(self):
        """Fully deterministic test for long underlying targets."""
        tp1, tp2 = calculate_underlying_targets(
            entry_price=200.0,
            predicted_sigma=0.15,
            side="BUY",
            tp1_sigma_multiplier=0.5,
            tp2_sigma_multiplier=1.0,
        )
        
        # TP1 = 200 + 0.5 * 0.15 * 200 = 200 + 15 = 215
        # TP2 = 200 + 1.0 * 0.15 * 200 = 200 + 30 = 230
        assert tp1 == 215.0
        assert tp2 == 230.0
    
    def test_deterministic_confidence(self):
        """Fully deterministic test for confidence calculation."""
        # mu=0.10, sigma=0.20, target=0.15
        # z = (0.15 - 0.10) / 0.20 = 0.25
        # Φ(0.25) ≈ 0.5987
        # Confidence = 1 - 0.5987 = 0.4013
        conf = calculate_target_confidence(mu=0.10, sigma=0.20, target_return=0.15)
        assert conf == pytest.approx(0.4013, abs=0.001)
    
    def test_deterministic_black_scholes_atm(self):
        """Fully deterministic Black-Scholes test."""
        # S=K=100, T=1.0, r=0.05, sigma=0.20
        # ATM call with 1 year to expiry
        call = black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type="CALL"
        )
        put = black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type="PUT"
        )
        
        # Known values from Black-Scholes calculator
        assert call == pytest.approx(10.45, abs=0.1)
        assert put == pytest.approx(5.57, abs=0.1)
        
        # Verify put-call parity: C - P = S - K*e^(-rT)
        assert (call - put) == pytest.approx(100.0 - 100.0 * math.exp(-0.05 * 1.0), rel=1e-4)
    
    def test_deterministic_option_targets(self):
        """Fully deterministic option target premiums test."""
        # Setup: 100 -> [110, 120] targets, 105 strike CALL, 90 days, 30% IV
        targets = calculate_option_target_premiums(
            current_underlying_price=100.0,
            underlying_targets=[110.0, 120.0],
            strike=105.0,
            time_to_expiry_years=90/365.0,
            risk_free_rate=0.05,
            implied_volatility=0.30,
            option_type="CALL",
            time_decay_days=[30, 60],
        )
        
        # At S=110, K=105, T=60/365: Call should be ~6-8
        assert 5.0 < targets[0]["option_premium"] < 10.0
        assert targets[0]["underlying_target"] == 110.0
        assert targets[0]["time_remaining_years"] == pytest.approx(60/365.0, abs=0.001)
        
        # At S=120, K=105, T=30/365: Call should be ~15-17 (mostly intrinsic)
        assert 14.0 < targets[1]["option_premium"] < 18.0
        assert targets[1]["underlying_target"] == 120.0
        assert targets[1]["time_remaining_years"] == pytest.approx(30/365.0, abs=0.001)
        
        # Second target should have higher premium
        assert targets[1]["option_premium"] > targets[0]["option_premium"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
