"""
Alert Rule Engine

Evaluates trading recommendations against configurable alert rules and
triggers notifications when thresholds are exceeded.

Current rules:
- High confidence alerts (overall confidence + TP1 confidence thresholds)
- Custom user-defined rules (future)
"""

from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

from notification_adapter import NotificationAdapter

logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    min_confidence_overall: float
    min_tp1_confidence: float
    enabled: bool = True
    notification_channels: List[str] = None  # ["email", "sms", "push"]
    recipients: List[str] = None  # List of email addresses or user IDs
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email"]
        if self.recipients is None:
            self.recipients = ["admin@trading.com"]


class AlertRuleEngine:
    """
    Rule engine for evaluating recommendations and triggering alerts
    """
    
    def __init__(self, notification_adapter: NotificationAdapter):
        self.adapter = notification_adapter
        self.rules = self._initialize_default_rules()
        logger.info(f"⚙️  AlertRuleEngine initialized with {len(self.rules)} rules")
    
    def _initialize_default_rules(self) -> List[AlertRule]:
        """Initialize default alert rules"""
        return [
            AlertRule(
                rule_id="high_confidence",
                name="High Confidence Alert",
                description="Alert when both overall confidence and TP1 confidence exceed 80%",
                min_confidence_overall=0.80,
                min_tp1_confidence=0.80,
                enabled=True,
                notification_channels=["email", "push"],
                recipients=["trader@example.com"]
            ),
            AlertRule(
                rule_id="very_high_confidence",
                name="Very High Confidence Alert",
                description="Alert when both overall confidence and TP1 confidence exceed 90%",
                min_confidence_overall=0.90,
                min_tp1_confidence=0.90,
                enabled=True,
                notification_channels=["email", "sms", "push"],
                recipients=["trader@example.com", "manager@example.com"]
            ),
            AlertRule(
                rule_id="moderate_confidence",
                name="Moderate Confidence Alert",
                description="Alert when both overall confidence and TP1 confidence exceed 70%",
                min_confidence_overall=0.70,
                min_tp1_confidence=0.70,
                enabled=False,  # Disabled by default to avoid spam
                notification_channels=["email"],
                recipients=["trader@example.com"]
            )
        ]
    
    async def evaluate_recommendation(
        self,
        reco_id: str,
        symbol: str,
        confidence_overall: float,
        tp1_confidence: float,
        entry_price: float,
        tp1_price: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a recommendation against all active rules
        
        Args:
            reco_id: Recommendation ID
            symbol: Stock symbol
            confidence_overall: Overall confidence score (0.0-1.0)
            tp1_confidence: TP1 confidence score (0.0-1.0)
            entry_price: Entry price
            tp1_price: Target price 1
            metadata: Optional additional metadata
            
        Returns:
            List of triggered alerts with details
        """
        triggered_alerts = []
        
        logger.info(f"🔍 Evaluating recommendation {reco_id} ({symbol})")
        logger.info(f"   Overall Confidence: {confidence_overall:.1%}")
        logger.info(f"   TP1 Confidence: {tp1_confidence:.1%}")
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check if recommendation meets rule thresholds
            if self._evaluate_rule(rule, confidence_overall, tp1_confidence):
                logger.info(f"✅ Rule '{rule.name}' triggered!")
                
                alert_details = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "reco_id": reco_id,
                    "symbol": symbol,
                    "confidence_overall": confidence_overall,
                    "tp1_confidence": tp1_confidence,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Send notifications through configured channels
                await self._send_alert_notifications(
                    rule=rule,
                    symbol=symbol,
                    confidence_overall=confidence_overall,
                    tp1_confidence=tp1_confidence,
                    entry_price=entry_price,
                    tp1_price=tp1_price,
                    reco_id=reco_id
                )
                
                triggered_alerts.append(alert_details)
            else:
                logger.debug(f"❌ Rule '{rule.name}' not triggered")
        
        if not triggered_alerts:
            logger.info(f"ℹ️  No rules triggered for {symbol}")
        else:
            logger.info(f"🚨 {len(triggered_alerts)} alert(s) triggered for {symbol}")
        
        return triggered_alerts
    
    def _evaluate_rule(
        self,
        rule: AlertRule,
        confidence_overall: float,
        tp1_confidence: float
    ) -> bool:
        """
        Evaluate if a single rule is triggered
        
        Args:
            rule: Alert rule to evaluate
            confidence_overall: Overall confidence score
            tp1_confidence: TP1 confidence score
            
        Returns:
            True if rule is triggered, False otherwise
        """
        meets_overall = confidence_overall >= rule.min_confidence_overall
        meets_tp1 = tp1_confidence >= rule.min_tp1_confidence
        
        return meets_overall and meets_tp1
    
    async def _send_alert_notifications(
        self,
        rule: AlertRule,
        symbol: str,
        confidence_overall: float,
        tp1_confidence: float,
        entry_price: float,
        tp1_price: float,
        reco_id: str
    ):
        """
        Send notifications for a triggered alert
        
        Args:
            rule: Triggered alert rule
            symbol: Stock symbol
            confidence_overall: Overall confidence score
            tp1_confidence: TP1 confidence score
            entry_price: Entry price
            tp1_price: Target price 1
            reco_id: Recommendation ID
        """
        # Calculate expected move
        move_pct = ((tp1_price - entry_price) / entry_price) * 100
        
        # Build notification message
        subject = f"🚨 Trading Alert: {symbol} - {rule.name}"
        
        message = f"""
High-confidence trading opportunity detected!

Symbol: {symbol}
Alert Rule: {rule.name}

Confidence Metrics:
- Overall Confidence: {confidence_overall:.1%}
- TP1 Confidence: {tp1_confidence:.1%}

Trade Details:
- Entry Price: ${entry_price:.2f}
- Target Price (TP1): ${tp1_price:.2f}
- Expected Move: {move_pct:+.2f}%

Recommendation ID: {reco_id}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---
This is an automated alert. Review the full recommendation in your trading dashboard.
        """.strip()
        
        # Send to all configured channels
        for channel in rule.notification_channels:
            for recipient in rule.recipients:
                try:
                    if channel == "email":
                        await self.adapter.send_email(
                            to=recipient,
                            subject=subject,
                            body=message
                        )
                    elif channel == "sms":
                        # Shorter message for SMS
                        sms_message = f"Trading Alert: {symbol} - Conf: {confidence_overall:.0%}/{tp1_confidence:.0%}, Entry: ${entry_price:.2f}, Target: ${tp1_price:.2f} ({move_pct:+.1f}%)"
                        await self.adapter.send_sms(
                            to=recipient,
                            message=sms_message
                        )
                    elif channel == "push":
                        await self.adapter.send_push(
                            user_id=recipient,
                            title=subject,
                            body=f"{symbol}: {confidence_overall:.0%} confidence, {move_pct:+.1f}% expected move",
                            data={
                                "reco_id": reco_id,
                                "symbol": symbol,
                                "entry_price": entry_price,
                                "tp1_price": tp1_price
                            }
                        )
                except Exception as e:
                    logger.error(f"❌ Failed to send {channel} notification to {recipient}: {e}")
    
    def add_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.rules.append(rule)
        logger.info(f"➕ Added new rule: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule by ID"""
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        removed = len(self.rules) < original_count
        if removed:
            logger.info(f"➖ Removed rule: {rule_id}")
        return removed
    
    def get_active_rules(self) -> List[AlertRule]:
        """Get all active (enabled) rules"""
        return [r for r in self.rules if r.enabled]
    
    def get_all_rules(self) -> List[AlertRule]:
        """Get all rules (enabled and disabled)"""
        return self.rules
