-- Migration: 001_create_recommendations_tables
-- Description: Create core tables for storing trading recommendations with multi-targets and options
-- Created: 2026-01-14

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main recommendations table
CREATE TABLE recommendations (
    reco_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asof TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    symbol TEXT NOT NULL,
    horizon TEXT NOT NULL,  -- e.g., 'day', 'swing', '1-2 months'
    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL', 'HOLD')),
    entry_price NUMERIC(18, 4) NOT NULL,
    confidence_overall NUMERIC(3, 2) NOT NULL CHECK (confidence_overall >= 0 AND confidence_overall <= 1),
    expected_move_pct NUMERIC(8, 4),  -- Expected percentage move
    rationale JSONB,  -- Detailed reasoning, catalysts, risks
    quality JSONB,  -- Quality metrics, indicators used, analyst info
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation targets (ladder strategy)
CREATE TABLE reco_targets (
    reco_id UUID NOT NULL REFERENCES recommendations(reco_id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    name TEXT,  -- e.g., 'Target 1', 'First Resistance'
    target_type TEXT NOT NULL DEFAULT 'price',  -- 'price', 'percentage', 'technical'
    value NUMERIC(18, 4) NOT NULL,  -- Target price or value
    confidence NUMERIC(3, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    eta_minutes INTEGER CHECK (eta_minutes > 0),  -- Estimated time to achieve in minutes
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reco_id, ordinal)
);

-- Option ideas (optional strategy for each recommendation)
CREATE TABLE option_ideas (
    reco_id UUID NOT NULL REFERENCES recommendations(reco_id) ON DELETE CASCADE,
    option_type TEXT NOT NULL CHECK (option_type IN ('CALL', 'PUT')),
    expiry DATE NOT NULL CHECK (expiry > CURRENT_DATE),
    strike NUMERIC(18, 4) NOT NULL,
    option_entry_price NUMERIC(18, 4) NOT NULL,
    greeks JSONB,  -- delta, gamma, theta, vega, rho
    iv JSONB,  -- implied volatility details
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reco_id),
    UNIQUE (reco_id)
);

-- Option premium targets
CREATE TABLE option_targets (
    reco_id UUID NOT NULL REFERENCES option_ideas(reco_id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    name TEXT,  -- e.g., 'Target 1', 'Take Profit 1'
    value NUMERIC(18, 4) NOT NULL,  -- Premium target
    confidence NUMERIC(3, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    eta_minutes INTEGER CHECK (eta_minutes > 0),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reco_id, ordinal)
);

-- Indexes for performance

-- Primary query patterns: symbol with recent recommendations
CREATE INDEX idx_recommendations_symbol_asof 
ON recommendations(symbol, asof DESC);

-- Filter by horizon and confidence
CREATE INDEX idx_recommendations_horizon_confidence 
ON recommendations(horizon, confidence_overall DESC);

-- Filter by side (BUY/SELL/HOLD)
CREATE INDEX idx_recommendations_side 
ON recommendations(side);

-- Time-based queries
CREATE INDEX idx_recommendations_asof 
ON recommendations(asof DESC);

-- Foreign key indexes for joins
CREATE INDEX idx_reco_targets_reco_id 
ON reco_targets(reco_id);

CREATE INDEX idx_option_ideas_reco_id 
ON option_ideas(reco_id);

CREATE INDEX idx_option_targets_reco_id 
ON option_targets(reco_id);

-- Composite index for target lookups
CREATE INDEX idx_reco_targets_reco_ordinal 
ON reco_targets(reco_id, ordinal);

CREATE INDEX idx_option_targets_reco_ordinal 
ON option_targets(reco_id, ordinal);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_recommendations_updated_at
    BEFORE UPDATE ON recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_option_ideas_updated_at
    BEFORE UPDATE ON option_ideas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE recommendations IS 'Main trading recommendations with confidence and expected moves';
COMMENT ON TABLE reco_targets IS 'Multi-target ladder strategy for recommendations (1-5 targets)';
COMMENT ON TABLE option_ideas IS 'Optional options strategy for each recommendation';
COMMENT ON TABLE option_targets IS 'Premium targets for options strategies (1-3 targets)';

COMMENT ON COLUMN recommendations.asof IS 'Timestamp when recommendation was generated';
COMMENT ON COLUMN recommendations.horizon IS 'Trading timeframe (e.g., day, swing, 1-2 months)';
COMMENT ON COLUMN recommendations.side IS 'Trading direction: BUY, SELL, or HOLD';
COMMENT ON COLUMN recommendations.confidence_overall IS 'Overall confidence score [0.0, 1.0]';
COMMENT ON COLUMN recommendations.rationale IS 'JSON with reasoning, catalysts, risks, indicators_used';
COMMENT ON COLUMN recommendations.quality IS 'JSON with quality metrics, analyst info, validation data';

COMMENT ON COLUMN reco_targets.ordinal IS 'Target number in sequence (1, 2, 3...)';
COMMENT ON COLUMN reco_targets.eta_minutes IS 'Estimated time to achieve target in minutes';

COMMENT ON COLUMN option_ideas.greeks IS 'JSON with delta, gamma, theta, vega, rho';
COMMENT ON COLUMN option_ideas.iv IS 'JSON with implied volatility details';
