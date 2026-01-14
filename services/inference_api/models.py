"""
SQLAlchemy 2.0 models for recommendations
"""

from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, CheckConstraint, Index, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database_async import Base


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    reco_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asof = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    symbol = Column(Text, nullable=False, index=True)
    horizon = Column(Text, nullable=False)
    side = Column(Text, nullable=False)
    entry_price = Column(Numeric(18, 4), nullable=False)
    confidence_overall = Column(Numeric(3, 2), nullable=False)
    expected_move_pct = Column(Numeric(8, 4))
    rationale = Column(JSONB)
    quality = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    targets = relationship("RecoTarget", back_populates="recommendation", lazy="selectin")
    option_idea = relationship("OptionIdea", back_populates="recommendation", uselist=False, lazy="selectin")
    
    __table_args__ = (
        CheckConstraint("side IN ('BUY', 'SELL', 'HOLD')", name="check_side"),
        CheckConstraint("confidence_overall >= 0 AND confidence_overall <= 1", name="check_confidence"),
        Index("idx_recommendations_symbol_asof", "symbol", asof.desc()),
        Index("idx_recommendations_horizon_confidence", "horizon", confidence_overall.desc()),
        Index("idx_recommendations_side", "side"),
        Index("idx_recommendations_asof", asof.desc()),
    )


class RecoTarget(Base):
    __tablename__ = "reco_targets"
    
    reco_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.reco_id", ondelete="CASCADE"), primary_key=True)
    ordinal = Column(Integer, nullable=False, primary_key=True)
    name = Column(Text)
    target_type = Column(Text, nullable=False, default="price")
    value = Column(Numeric(18, 4), nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    eta_minutes = Column(Integer)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationship
    recommendation = relationship("Recommendation", back_populates="targets")
    
    __table_args__ = (
        CheckConstraint("ordinal > 0", name="check_ordinal_positive"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="check_target_confidence"),
        CheckConstraint("eta_minutes > 0", name="check_eta_positive"),
        Index("idx_reco_targets_reco_id", "reco_id"),
        Index("idx_reco_targets_reco_ordinal", "reco_id", "ordinal"),
    )


class OptionIdea(Base):
    __tablename__ = "option_ideas"
    
    reco_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.reco_id", ondelete="CASCADE"), primary_key=True)
    option_type = Column(Text, nullable=False)
    expiry = Column(Date, nullable=False)
    strike = Column(Numeric(18, 4), nullable=False)
    option_entry_price = Column(Numeric(18, 4), nullable=False)
    greeks = Column(JSONB)
    iv = Column(JSONB)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="option_idea")
    option_targets = relationship("OptionTarget", back_populates="option_idea", lazy="selectin")
    
    __table_args__ = (
        CheckConstraint("option_type IN ('CALL', 'PUT')", name="check_option_type"),
        CheckConstraint("expiry > CURRENT_DATE", name="check_expiry_future"),
        Index("idx_option_ideas_reco_id", "reco_id"),
    )


class OptionTarget(Base):
    __tablename__ = "option_targets"
    
    reco_id = Column(UUID(as_uuid=True), ForeignKey("option_ideas.reco_id", ondelete="CASCADE"), primary_key=True)
    ordinal = Column(Integer, nullable=False, primary_key=True)
    name = Column(Text)
    value = Column(Numeric(18, 4), nullable=False)
    confidence = Column(Numeric(3, 2), nullable=False)
    eta_minutes = Column(Integer)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationship
    option_idea = relationship("OptionIdea", back_populates="option_targets")
    
    __table_args__ = (
        CheckConstraint("ordinal > 0", name="check_option_ordinal_positive"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="check_option_target_confidence"),
        CheckConstraint("eta_minutes > 0", name="check_option_eta_positive"),
        Index("idx_option_targets_reco_id", "reco_id"),
        Index("idx_option_targets_reco_ordinal", "reco_id", "ordinal"),
    )
