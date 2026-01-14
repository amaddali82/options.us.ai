"""
Ranking formula for recommendations
rank = confidence_overall * abs(expected_move_pct) * liquidity_score * freshness_factor
"""

from datetime import datetime, timezone
from typing import Optional


def calculate_freshness_factor(asof: datetime, decay_minutes: int = 5) -> float:
    """
    Calculate freshness factor with exponential decay after decay_minutes
    
    Args:
        asof: When the recommendation was generated
        decay_minutes: Minutes until decay starts (default 5)
        
    Returns:
        Float between 0.1 and 1.0
    """
    now = datetime.now(timezone.utc)
    
    # Make asof timezone-aware if it isn't
    if asof.tzinfo is None:
        asof = asof.replace(tzinfo=timezone.utc)
    
    age_minutes = (now - asof).total_seconds() / 60.0
    
    if age_minutes <= decay_minutes:
        return 1.0
    
    # Exponential decay: e^(-k * (age - decay_minutes))
    # Half-life of 30 minutes after decay starts
    k = 0.0231  # ln(2) / 30
    excess_age = age_minutes - decay_minutes
    
    freshness = max(0.1, min(1.0, pow(2.71828, -k * excess_age)))
    return freshness


def calculate_rank(
    confidence_overall: float,
    expected_move_pct: Optional[float],
    quality: Optional[dict],
    asof: datetime
) -> float:
    """
    Calculate recommendation rank using the formula:
    rank = confidence_overall * abs(expected_move_pct) * liquidity_score * freshness_factor
    
    Args:
        confidence_overall: Overall confidence [0, 1]
        expected_move_pct: Expected percentage move (can be negative for SELL)
        quality: Quality JSON containing liquidity_score
        asof: When recommendation was generated
        
    Returns:
        Rank score (higher is better)
    """
    # Default values
    move_pct = abs(expected_move_pct) if expected_move_pct is not None else 5.0
    liquidity_score = 0.8  # Default
    
    # Extract liquidity_score from quality JSON
    if quality and isinstance(quality, dict):
        liquidity_score = quality.get('liquidity_score', 0.8)
    
    # Calculate freshness
    freshness = calculate_freshness_factor(asof)
    
    # Calculate rank
    rank = confidence_overall * move_pct * liquidity_score * freshness
    
    return round(rank, 6)


def calculate_rank_from_model(recommendation) -> float:
    """
    Calculate rank directly from a recommendation model/dict
    
    Args:
        recommendation: SQLAlchemy model or dict with recommendation data
        
    Returns:
        Rank score
    """
    # Handle both SQLAlchemy models and dicts
    if hasattr(recommendation, 'confidence_overall'):
        # SQLAlchemy model
        confidence = float(recommendation.confidence_overall)
        expected_move = float(recommendation.expected_move_pct) if recommendation.expected_move_pct else None
        quality = recommendation.quality
        asof = recommendation.asof
    else:
        # Dict
        confidence = float(recommendation['confidence_overall'])
        expected_move = float(recommendation['expected_move_pct']) if recommendation.get('expected_move_pct') else None
        quality = recommendation.get('quality')
        asof = recommendation['asof']
    
    return calculate_rank(confidence, expected_move, quality, asof)
