-- Migration: 002_add_sample_data
-- Description: Insert sample recommendations for testing and demonstration
-- Created: 2026-01-14

-- Sample Recommendation 1: AAPL BUY with options
INSERT INTO recommendations (
    reco_id,
    symbol,
    horizon,
    side,
    entry_price,
    confidence_overall,
    expected_move_pct,
    rationale,
    quality
) VALUES (
    'a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid,
    'AAPL',
    '1-2 months',
    'BUY',
    175.50,
    0.85,
    8.50,
    jsonb_build_object(
        'reasoning', 'Strong bullish momentum with technical breakout above 170 resistance. RSI at 68 showing strength without overbought conditions.',
        'catalysts', jsonb_build_array('Q1 earnings expected beat', 'New product announcement', 'Positive analyst upgrades'),
        'risks', jsonb_build_array('Market volatility', 'Tech sector rotation'),
        'indicators_used', jsonb_build_array('RSI', 'MACD', 'Volume', 'Support/Resistance')
    ),
    jsonb_build_object(
        'analyst', 'AI Trading System v1.0',
        'risk_reward_ratio', 3.5,
        'stop_loss', jsonb_build_object('price', 168.00, 'confidence', 0.90, 'type', 'hard')
    )
);

-- Targets for AAPL
INSERT INTO reco_targets (reco_id, ordinal, name, target_type, value, confidence, eta_minutes, notes) VALUES
    ('a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid, 1, 'Target 1', 'price', 182.00, 0.85, 21600, 'First resistance level'),
    ('a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid, 2, 'Target 2', 'price', 188.50, 0.70, 43200, 'Key technical level'),
    ('a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid, 3, 'Target 3', 'price', 195.00, 0.55, 64800, 'Fibonacci extension');

-- Option idea for AAPL
INSERT INTO option_ideas (
    reco_id,
    option_type,
    expiry,
    strike,
    option_entry_price,
    greeks,
    iv,
    notes
) VALUES (
    'a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid,
    'CALL',
    '2026-02-20',
    180.00,
    5.80,
    jsonb_build_object('delta', 0.65, 'gamma', 0.025, 'theta', -0.05, 'vega', 0.18, 'rho', 0.08),
    jsonb_build_object('value', 0.32, 'percentile_rank', 65),
    'Leveraged play with defined risk, 2:1 contracts recommended'
);

-- Option targets for AAPL
INSERT INTO option_targets (reco_id, ordinal, name, value, confidence, eta_minutes, notes) VALUES
    ('a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid, 1, 'Take Profit 1', 8.50, 0.75, 21600, '46.5% gain'),
    ('a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid, 2, 'Take Profit 2', 11.20, 0.55, 43200, '93.1% gain'),
    ('a1b2c3d4-e5f6-4a5b-9c8d-1e2f3a4b5c6d'::uuid, 3, 'Take Profit 3', 14.80, 0.35, 64800, '155.2% gain');

-- Sample Recommendation 2: TSLA SELL (bearish)
INSERT INTO recommendations (
    reco_id,
    symbol,
    horizon,
    side,
    entry_price,
    confidence_overall,
    expected_move_pct,
    rationale,
    quality
) VALUES (
    'b2c3d4e5-f6a7-4b5c-9d8e-2f3a4b5c6d7e'::uuid,
    'TSLA',
    'swing',
    'SELL',
    245.00,
    0.72,
    -6.80,
    jsonb_build_object(
        'reasoning', 'Bearish divergence on daily chart with weakening momentum. Breaking below key support at 250.',
        'catalysts', jsonb_build_array('Earnings miss expected', 'Production concerns', 'Competitive pressure'),
        'risks', jsonb_build_array('Short squeeze potential', 'Positive news catalyst'),
        'indicators_used', jsonb_build_array('RSI', 'MACD', 'Volume', 'Trend Lines')
    ),
    jsonb_build_object(
        'analyst', 'AI Trading System v1.0',
        'risk_reward_ratio', 2.8,
        'stop_loss', jsonb_build_object('price', 255.00, 'confidence', 0.88, 'type', 'hard')
    )
);

-- Targets for TSLA (descending for SELL)
INSERT INTO reco_targets (reco_id, ordinal, name, target_type, value, confidence, eta_minutes, notes) VALUES
    ('b2c3d4e5-f6a7-4b5c-9d8e-2f3a4b5c6d7e'::uuid, 1, 'Target 1', 'price', 235.00, 0.80, 10080, 'First support breakdown'),
    ('b2c3d4e5-f6a7-4b5c-9d8e-2f3a4b5c6d7e'::uuid, 2, 'Target 2', 'price', 225.00, 0.65, 20160, 'Major support level');

-- Sample Recommendation 3: MSFT HOLD (neutral)
INSERT INTO recommendations (
    reco_id,
    symbol,
    horizon,
    side,
    entry_price,
    confidence_overall,
    expected_move_pct,
    rationale,
    quality
) VALUES (
    'c3d4e5f6-a7b8-4c5d-9e8f-3a4b5c6d7e8f'::uuid,
    'MSFT',
    'swing',
    'HOLD',
    380.00,
    0.70,
    0.50,
    jsonb_build_object(
        'reasoning', 'Consolidating in tight range. Awaiting clearer directional signal before entry.',
        'catalysts', jsonb_build_array('Upcoming Azure growth data', 'Cloud competition analysis'),
        'risks', jsonb_build_array('Sector weakness', 'Valuation concerns'),
        'indicators_used', jsonb_build_array('Bollinger Bands', 'Volume', 'ATR')
    ),
    jsonb_build_object(
        'analyst', 'AI Trading System v1.0',
        'risk_reward_ratio', 1.5
    )
);

-- Minimal targets for HOLD recommendation
INSERT INTO reco_targets (reco_id, ordinal, name, target_type, value, confidence, eta_minutes, notes) VALUES
    ('c3d4e5f6-a7b8-4c5d-9e8f-3a4b5c6d7e8f'::uuid, 1, 'Upside Target', 'price', 390.00, 0.60, 30240, 'If breaks above resistance'),
    ('c3d4e5f6-a7b8-4c5d-9e8f-3a4b5c6d7e8f'::uuid, 2, 'Downside Target', 'price', 370.00, 0.60, 30240, 'If breaks below support');

-- Sample Recommendation 4: NVDA with complex option strategy
INSERT INTO recommendations (
    reco_id,
    symbol,
    horizon,
    side,
    entry_price,
    confidence_overall,
    expected_move_pct,
    rationale,
    quality
) VALUES (
    'd4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid,
    'NVDA',
    '1-2 months',
    'BUY',
    495.50,
    0.88,
    12.50,
    jsonb_build_object(
        'reasoning', 'Exceptional momentum in AI chip sector. Technical breakout with strong volume confirmation.',
        'catalysts', jsonb_build_array('Q4 earnings beat expected', 'AI chip demand surge', 'Major partnerships'),
        'risks', jsonb_build_array('Valuation stretched', 'Semiconductor cycle', 'China restrictions'),
        'indicators_used', jsonb_build_array('RSI', 'MACD', 'Volume Profile', 'Fibonacci')
    ),
    jsonb_build_object(
        'analyst', 'AI Trading System v1.0',
        'risk_reward_ratio', 4.2,
        'stop_loss', jsonb_build_object('price', 475.00, 'confidence', 0.92, 'type', 'trailing')
    )
);

-- Targets for NVDA
INSERT INTO reco_targets (reco_id, ordinal, name, target_type, value, confidence, eta_minutes, notes) VALUES
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 1, 'Target 1', 'price', 520.00, 0.85, 14400, 'Breakout continuation'),
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 2, 'Target 2', 'price', 545.00, 0.70, 28800, 'Fib extension'),
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 3, 'Target 3', 'price', 575.00, 0.55, 43200, 'Psychological level'),
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 4, 'Target 4', 'price', 600.00, 0.40, 57600, 'Major milestone');

-- Option idea for NVDA
INSERT INTO option_ideas (
    reco_id,
    option_type,
    expiry,
    strike,
    option_entry_price,
    greeks,
    iv,
    notes
) VALUES (
    'd4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid,
    'CALL',
    '2026-03-20',
    510.00,
    28.50,
    jsonb_build_object('delta', 0.62, 'gamma', 0.018, 'theta', -0.42, 'vega', 0.95, 'rho', 0.35),
    jsonb_build_object('value', 0.45, 'percentile_rank', 72),
    'High conviction setup, 3 contracts for leveraged exposure with defined risk'
);

-- Option targets for NVDA
INSERT INTO option_targets (reco_id, ordinal, name, value, confidence, eta_minutes, notes) VALUES
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 1, 'Take Profit 1', 42.00, 0.80, 14400, '47.4% gain'),
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 2, 'Take Profit 2', 58.50, 0.60, 28800, '105.3% gain'),
    ('d4e5f6a7-b8c9-4d5e-9f0a-4b5c6d7e8f9a'::uuid, 3, 'Take Profit 3', 78.00, 0.40, 43200, '173.7% gain');
