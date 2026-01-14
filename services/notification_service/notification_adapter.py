"""
Notification Adapter - Internal interface for sending notifications

This adapter provides a unified interface for sending notifications across
multiple channels (email, SMS, push). In the current implementation, all
notifications are logged rather than sent to external providers.

Future implementations will integrate with:
- SendGrid/AWS SES for email
- Twilio for SMS
- Firebase Cloud Messaging for push notifications
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationAdapterInterface(ABC):
    """Abstract base class for notification adapters"""
    
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """Send email notification"""
        pass
    
    @abstractmethod
    async def send_sms(self, to: str, message: str) -> bool:
        """Send SMS notification"""
        pass
    
    @abstractmethod
    async def send_push(self, user_id: str, title: str, body: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send push notification"""
        pass


class NotificationAdapter(NotificationAdapterInterface):
    """
    Logging-based notification adapter
    
    This implementation logs all notifications instead of sending them to
    external providers. Useful for development and testing.
    """
    
    def __init__(self):
        self.email_count = 0
        self.sms_count = 0
        self.push_count = 0
        logger.info("📧 NotificationAdapter initialized in LOGGING mode")
    
    async def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """
        Log email notification (stub implementation)
        
        Args:
            to: Recipient email address
            subject: Email subject line
            body: Plain text email body
            html: Optional HTML email body
            
        Returns:
            True if logged successfully
        """
        self.email_count += 1
        
        logger.info("=" * 60)
        logger.info("📧 EMAIL NOTIFICATION (would be sent)")
        logger.info(f"   To: {to}")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Body: {body[:100]}..." if len(body) > 100 else f"   Body: {body}")
        if html:
            logger.info(f"   HTML: {html[:100]}..." if len(html) > 100 else f"   HTML: {html}")
        logger.info(f"   Timestamp: {datetime.now().isoformat()}")
        logger.info(f"   Total emails logged: {self.email_count}")
        logger.info("=" * 60)
        
        return True
    
    async def send_sms(self, to: str, message: str) -> bool:
        """
        Log SMS notification (stub implementation)
        
        Args:
            to: Recipient phone number (E.164 format)
            message: SMS message body (max 160 chars recommended)
            
        Returns:
            True if logged successfully
        """
        self.sms_count += 1
        
        logger.info("=" * 60)
        logger.info("📱 SMS NOTIFICATION (would be sent)")
        logger.info(f"   To: {to}")
        logger.info(f"   Message: {message}")
        logger.info(f"   Length: {len(message)} chars")
        logger.info(f"   Timestamp: {datetime.now().isoformat()}")
        logger.info(f"   Total SMS logged: {self.sms_count}")
        logger.info("=" * 60)
        
        return True
    
    async def send_push(self, user_id: str, title: str, body: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log push notification (stub implementation)
        
        Args:
            user_id: User identifier or device token
            title: Notification title
            body: Notification body
            data: Optional additional data payload
            
        Returns:
            True if logged successfully
        """
        self.push_count += 1
        
        logger.info("=" * 60)
        logger.info("🔔 PUSH NOTIFICATION (would be sent)")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Title: {title}")
        logger.info(f"   Body: {body}")
        if data:
            logger.info(f"   Data: {data}")
        logger.info(f"   Timestamp: {datetime.now().isoformat()}")
        logger.info(f"   Total push logged: {self.push_count}")
        logger.info("=" * 60)
        
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Get notification statistics"""
        return {
            "emails_logged": self.email_count,
            "sms_logged": self.sms_count,
            "push_logged": self.push_count,
            "total_logged": self.email_count + self.sms_count + self.push_count
        }


# Future: Production adapter with real providers
class ProductionNotificationAdapter(NotificationAdapterInterface):
    """
    Production notification adapter (stub for future implementation)
    
    Will integrate with:
    - SendGrid/AWS SES for email
    - Twilio for SMS  
    - Firebase Cloud Messaging for push
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # TODO: Initialize provider clients
        logger.info("📧 ProductionNotificationAdapter initialized (NOT IMPLEMENTED)")
    
    async def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """Send email via SendGrid/SES"""
        raise NotImplementedError("Production email sending not yet implemented")
    
    async def send_sms(self, to: str, message: str) -> bool:
        """Send SMS via Twilio"""
        raise NotImplementedError("Production SMS sending not yet implemented")
    
    async def send_push(self, user_id: str, title: str, body: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send push notification via FCM"""
        raise NotImplementedError("Production push notifications not yet implemented")
