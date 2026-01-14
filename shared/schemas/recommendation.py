"""
Trading Recommendation Models with Options Support
Pydantic v2 models with strong typing and validation
"""

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Literal
from datetime import date, datetime
from enum import Enum
from decimal import Decimal


class OptionType(str, Enum):
    """Option type: Call or Put"""
    CALL = "CALL"
    PUT = "PUT"


class Target(BaseModel):
    """
    Price target for underlying asset with confidence level
    Part of a multi-target ladder strategy
    """
    price: float = Field(
        ...,
        gt=0,
        description="Target price for the underlying asset"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence level for reaching this target (0.0 to 1.0)"
    )
    timeframe_days: Optional[int] = Field(
        None,
        gt=0,
        description="Expected timeframe to reach target in days"
    )
    reasoning: Optional[str] = Field(
        None,
        max_length=500,
        description="Brief explanation for this target level"
    )

    @field_validator('price')
    @classmethod
    def validate_price_precision(cls, v: float) -> float:
        """Ensure price has reasonable precision (max 4 decimal places)"""
        return round(v, 4)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 185.50,
                "confidence": 0.75,
                "timeframe_days": 30,
                "reasoning": "Strong support at this level with bullish momentum"
            }
        }
    )


class Stop(BaseModel):
    """
    Stop-loss level with confidence
    """
    price: float = Field(
        ...,
        gt=0,
        description="Stop-loss price level"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in stop level holding (0.0 to 1.0)"
    )
    stop_type: Literal["hard", "trailing", "mental"] = Field(
        default="hard",
        description="Type of stop: hard (automatic), trailing (dynamic), or mental"
    )
    reasoning: Optional[str] = Field(
        None,
        max_length=300,
        description="Reason for this stop level"
    )

    @field_validator('price')
    @classmethod
    def validate_price_precision(cls, v: float) -> float:
        """Ensure price has reasonable precision"""
        return round(v, 4)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 165.00,
                "confidence": 0.85,
                "stop_type": "hard",
                "reasoning": "Below key support with high volume"
            }
        }
    )


class Greeks(BaseModel):
    """
    Option Greeks for risk assessment
    """
    delta: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Delta: rate of change of option price with respect to underlying"
    )
    gamma: Optional[float] = Field(
        None,
        ge=0.0,
        description="Gamma: rate of change of delta"
    )
    theta: Optional[float] = Field(
        None,
        description="Theta: time decay per day"
    )
    vega: Optional[float] = Field(
        None,
        ge=0.0,
        description="Vega: sensitivity to volatility changes"
    )
    rho: Optional[float] = Field(
        None,
        description="Rho: sensitivity to interest rate changes"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "delta": 0.65,
                "gamma": 0.025,
                "theta": -0.05,
                "vega": 0.18,
                "rho": 0.08
            }
        }
    )


class OptionTarget(BaseModel):
    """
    Premium target for options with confidence level
    """
    premium: float = Field(
        ...,
        gt=0,
        description="Target option premium (price per contract)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in reaching this premium target (0.0 to 1.0)"
    )
    profit_percentage: Optional[float] = Field(
        None,
        description="Expected profit percentage at this target"
    )
    underlying_price: Optional[float] = Field(
        None,
        gt=0,
        description="Expected underlying price at this premium target"
    )

    @field_validator('premium')
    @classmethod
    def validate_premium_precision(cls, v: float) -> float:
        """Ensure premium has reasonable precision"""
        return round(v, 4)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "premium": 8.50,
                "confidence": 0.70,
                "profit_percentage": 45.5,
                "underlying_price": 182.00
            }
        }
    )


class OptionIdea(BaseModel):
    """
    Options trading idea with detailed specifications
    Must include 1-3 option targets
    """
    option_type: OptionType = Field(
        ...,
        description="Type of option: CALL or PUT"
    )
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Underlying symbol (e.g., AAPL, SPY)"
    )
    expiry: date = Field(
        ...,
        description="Option expiration date (YYYY-MM-DD)"
    )
    strike: float = Field(
        ...,
        gt=0,
        description="Strike price"
    )
    entry_premium: float = Field(
        ...,
        gt=0,
        description="Recommended entry premium (price per contract)"
    )
    contracts: Optional[int] = Field(
        default=1,
        gt=0,
        description="Suggested number of contracts"
    )
    greeks: Greeks = Field(
        ...,
        description="Option Greeks at entry"
    )
    implied_volatility: float = Field(
        ...,
        gt=0,
        le=5.0,
        description="Implied volatility (as decimal, e.g., 0.35 for 35%)"
    )
    option_targets: List[OptionTarget] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="1-3 premium targets with confidence levels"
    )
    stop_loss_premium: Optional[float] = Field(
        None,
        gt=0,
        description="Stop loss at this premium level"
    )
    max_loss_dollars: Optional[float] = Field(
        None,
        description="Maximum loss in dollars for risk management"
    )
    reasoning: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed reasoning for this option trade"
    )

    @field_validator('symbol')
    @classmethod
    def validate_symbol_uppercase(cls, v: str) -> str:
        """Ensure symbol is uppercase"""
        return v.upper().strip()

    @field_validator('expiry')
    @classmethod
    def validate_expiry_future(cls, v: date) -> date:
        """Ensure expiry is in the future"""
        if v <= date.today():
            raise ValueError(f"Expiry date must be in the future, got {v}")
        return v

    @field_validator('strike', 'entry_premium')
    @classmethod
    def validate_price_precision(cls, v: float) -> float:
        """Ensure prices have reasonable precision"""
        return round(v, 4)

    @model_validator(mode='after')
    def validate_targets_sorted(self) -> 'OptionIdea':
        """Ensure option targets are sorted by premium (ascending)"""
        if len(self.option_targets) > 1:
            premiums = [t.premium for t in self.option_targets]
            if premiums != sorted(premiums):
                raise ValueError("Option targets must be sorted by premium in ascending order")
        return self

    @model_validator(mode='after')
    def validate_entry_vs_targets(self) -> 'OptionIdea':
        """Ensure first target is above entry premium"""
        if self.option_targets and self.option_targets[0].premium <= self.entry_premium:
            raise ValueError(
                f"First target premium ({self.option_targets[0].premium}) must be "
                f"greater than entry premium ({self.entry_premium})"
            )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "option_type": "CALL",
                "symbol": "AAPL",
                "expiry": "2026-02-20",
                "strike": 180.00,
                "entry_premium": 5.80,
                "contracts": 2,
                "greeks": {
                    "delta": 0.65,
                    "gamma": 0.025,
                    "theta": -0.05,
                    "vega": 0.18
                },
                "implied_volatility": 0.32,
                "option_targets": [
                    {"premium": 8.50, "confidence": 0.75},
                    {"premium": 11.20, "confidence": 0.55},
                    {"premium": 14.80, "confidence": 0.35}
                ],
                "stop_loss_premium": 4.20,
                "reasoning": "Bullish setup with strong technical momentum"
            }
        }
    )


class Recommendation(BaseModel):
    """
    Complete trading recommendation with multi-target ladder
    Can include optional options strategy
    """
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Primary underlying symbol"
    )
    recommendation_type: Literal["BUY", "SELL", "HOLD"] = Field(
        ...,
        description="Primary recommendation action"
    )
    confidence_overall: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in this recommendation (0.0 to 1.0)"
    )
    current_price: float = Field(
        ...,
        gt=0,
        description="Current price of the underlying asset"
    )
    entry_price: Optional[float] = Field(
        None,
        gt=0,
        description="Recommended entry price for underlying (if different from current)"
    )
    targets: List[Target] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="1-5 price targets forming a ladder strategy"
    )
    stop_loss: Optional[Stop] = Field(
        None,
        description="Stop-loss configuration"
    )
    option_idea: Optional[OptionIdea] = Field(
        None,
        description="Optional options strategy for this recommendation"
    )
    timeframe: Optional[str] = Field(
        None,
        description="Overall timeframe for the trade (e.g., '1-3 months', 'swing', 'day')"
    )
    risk_reward_ratio: Optional[float] = Field(
        None,
        gt=0,
        description="Risk/reward ratio for the trade"
    )
    catalysts: Optional[List[str]] = Field(
        default_factory=list,
        max_length=10,
        description="Key catalysts or events supporting this recommendation"
    )
    risks: Optional[List[str]] = Field(
        default_factory=list,
        max_length=10,
        description="Key risks to monitor"
    )
    reasoning: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Comprehensive reasoning for this recommendation"
    )
    indicators_used: Optional[List[str]] = Field(
        default_factory=list,
        description="Technical indicators used in analysis"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when recommendation was generated"
    )
    analyst: Optional[str] = Field(
        None,
        description="Analyst or system that generated this recommendation"
    )

    @field_validator('symbol')
    @classmethod
    def validate_symbol_uppercase(cls, v: str) -> str:
        """Ensure symbol is uppercase"""
        return v.upper().strip()

    @field_validator('current_price', 'entry_price')
    @classmethod
    def validate_price_precision(cls, v: Optional[float]) -> Optional[float]:
        """Ensure prices have reasonable precision"""
        return round(v, 4) if v is not None else None

    @model_validator(mode='after')
    def validate_targets_sorted(self) -> 'Recommendation':
        """Ensure targets are sorted by price"""
        if len(self.targets) > 1:
            prices = [t.price for t in self.targets]
            # For BUY recommendations, targets should be ascending
            # For SELL recommendations, targets should be descending
            if self.recommendation_type == "BUY":
                if prices != sorted(prices):
                    raise ValueError("For BUY recommendations, targets must be sorted by price in ascending order")
            elif self.recommendation_type == "SELL":
                if prices != sorted(prices, reverse=True):
                    raise ValueError("For SELL recommendations, targets must be sorted by price in descending order")
        return self

    @model_validator(mode='after')
    def validate_targets_vs_current_price(self) -> 'Recommendation':
        """Ensure targets make sense relative to current price and recommendation type"""
        if self.recommendation_type == "BUY":
            # For BUY, all targets should be above current price
            for target in self.targets:
                if target.price <= self.current_price:
                    raise ValueError(
                        f"For BUY recommendation, target price {target.price} "
                        f"must be above current price {self.current_price}"
                    )
        elif self.recommendation_type == "SELL":
            # For SELL, all targets should be below current price
            for target in self.targets:
                if target.price >= self.current_price:
                    raise ValueError(
                        f"For SELL recommendation, target price {target.price} "
                        f"must be below current price {self.current_price}"
                    )
        return self

    @model_validator(mode='after')
    def validate_stop_loss_direction(self) -> 'Recommendation':
        """Ensure stop loss is in correct direction"""
        if self.stop_loss:
            if self.recommendation_type == "BUY" and self.stop_loss.price >= self.current_price:
                raise ValueError(
                    f"For BUY recommendation, stop loss {self.stop_loss.price} "
                    f"must be below current price {self.current_price}"
                )
            elif self.recommendation_type == "SELL" and self.stop_loss.price <= self.current_price:
                raise ValueError(
                    f"For SELL recommendation, stop loss {self.stop_loss.price} "
                    f"must be above current price {self.current_price}"
                )
        return self

    @model_validator(mode='after')
    def validate_option_symbol_match(self) -> 'Recommendation':
        """Ensure option_idea symbol matches recommendation symbol"""
        if self.option_idea and self.option_idea.symbol != self.symbol:
            raise ValueError(
                f"Option symbol {self.option_idea.symbol} must match "
                f"recommendation symbol {self.symbol}"
            )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "recommendation_type": "BUY",
                "confidence_overall": 0.82,
                "current_price": 175.50,
                "entry_price": 176.00,
                "targets": [
                    {"price": 182.00, "confidence": 0.85, "timeframe_days": 15},
                    {"price": 188.50, "confidence": 0.70, "timeframe_days": 30},
                    {"price": 195.00, "confidence": 0.55, "timeframe_days": 45}
                ],
                "stop_loss": {
                    "price": 168.00,
                    "confidence": 0.90,
                    "stop_type": "hard"
                },
                "timeframe": "1-2 months",
                "risk_reward_ratio": 3.5,
                "reasoning": "Strong bullish momentum with positive technical setup",
                "analyst": "AI Trading System v1.0"
            }
        }
    )


# Helper function for JSON schema export
def get_recommendation_schema() -> dict:
    """
    Get the JSON schema for the Recommendation model
    
    Returns:
        dict: JSON schema representation of the Recommendation model
    """
    return Recommendation.model_json_schema()


def get_all_schemas() -> dict:
    """
    Get JSON schemas for all models
    
    Returns:
        dict: Dictionary containing schemas for all models
    """
    return {
        "Recommendation": Recommendation.model_json_schema(),
        "Target": Target.model_json_schema(),
        "Stop": Stop.model_json_schema(),
        "OptionIdea": OptionIdea.model_json_schema(),
        "OptionTarget": OptionTarget.model_json_schema(),
        "Greeks": Greeks.model_json_schema(),
    }


def export_schemas_to_file(filepath: str = "recommendation_schemas.json") -> None:
    """
    Export all schemas to a JSON file
    
    Args:
        filepath: Path to output JSON file
    """
    import json
    
    schemas = get_all_schemas()
    with open(filepath, 'w') as f:
        json.dump(schemas, f, indent=2, default=str)
    print(f"Schemas exported to {filepath}")


# Example usage and validation
if __name__ == "__main__":
    # Example: Create a complete recommendation with options
    example_recommendation = Recommendation(
        symbol="AAPL",
        recommendation_type="BUY",
        confidence_overall=0.82,
        current_price=175.50,
        entry_price=176.00,
        targets=[
            Target(price=182.00, confidence=0.85, timeframe_days=15, reasoning="First resistance level"),
            Target(price=188.50, confidence=0.70, timeframe_days=30, reasoning="Key technical level"),
            Target(price=195.00, confidence=0.55, timeframe_days=45, reasoning="Fibonacci extension"),
        ],
        stop_loss=Stop(
            price=168.00,
            confidence=0.90,
            stop_type="hard",
            reasoning="Below major support"
        ),
        option_idea=OptionIdea(
            option_type=OptionType.CALL,
            symbol="AAPL",
            expiry=date(2026, 2, 20),
            strike=180.00,
            entry_premium=5.80,
            contracts=2,
            greeks=Greeks(delta=0.65, gamma=0.025, theta=-0.05, vega=0.18),
            implied_volatility=0.32,
            option_targets=[
                OptionTarget(premium=8.50, confidence=0.75, profit_percentage=46.5),
                OptionTarget(premium=11.20, confidence=0.55, profit_percentage=93.1),
                OptionTarget(premium=14.80, confidence=0.35, profit_percentage=155.2),
            ],
            stop_loss_premium=4.20,
            reasoning="Leveraged play on bullish momentum with defined risk"
        ),
        timeframe="1-2 months",
        risk_reward_ratio=3.5,
        catalysts=["Q1 earnings release", "New product launch", "Positive analyst upgrades"],
        risks=["Market volatility", "Tech sector rotation", "Macro headwinds"],
        reasoning="Strong bullish momentum supported by technical breakout, positive fundamentals, and upcoming catalysts. RSI showing strength without being overbought.",
        indicators_used=["RSI", "MACD", "Volume", "Support/Resistance"],
        analyst="AI Trading System v1.0"
    )
    
    # Validate and print
    print("✅ Recommendation created successfully!")
    print(f"\n📊 {example_recommendation.symbol} - {example_recommendation.recommendation_type}")
    print(f"   Confidence: {example_recommendation.confidence_overall:.1%}")
    print(f"   Current Price: ${example_recommendation.current_price:.2f}")
    print(f"   Targets: {len(example_recommendation.targets)}")
    if example_recommendation.option_idea:
        print(f"   Option: {example_recommendation.option_idea.option_type.value} ${example_recommendation.option_idea.strike} exp {example_recommendation.option_idea.expiry}")
    
    # Export schema
    print(f"\n📋 JSON Schema available via get_recommendation_schema()")
