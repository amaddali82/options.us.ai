-- Initialize the Trading Intelligence database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    recommendation VARCHAR(10) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    reasoning TEXT,
    indicators_used TEXT[],
    timeframe VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_symbol ON recommendations(symbol);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_at ON recommendations(created_at DESC);

-- Create sample data (optional)
INSERT INTO recommendations (symbol, recommendation, confidence, reasoning, indicators_used, timeframe)
VALUES 
    ('AAPL', 'BUY', 0.85, 'Strong upward momentum with positive technical indicators', ARRAY['RSI', 'MACD'], '1d'),
    ('TSLA', 'HOLD', 0.70, 'Neutral signals, waiting for clearer trend', ARRAY['RSI', 'EMA'], '1d'),
    ('MSFT', 'BUY', 0.78, 'Bullish pattern formation with volume confirmation', ARRAY['BOLLINGER_BANDS', 'SMA'], '1d')
ON CONFLICT DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger
DROP TRIGGER IF EXISTS update_recommendations_updated_at ON recommendations;
CREATE TRIGGER update_recommendations_updated_at
    BEFORE UPDATE ON recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
