#!/usr/bin/env python3
"""
Test script for notification service

Demonstrates:
1. Sending manual notifications
2. Evaluating alert rules
3. Viewing notification logs
"""

import asyncio
import httpx
import sys
from datetime import datetime


BASE_URL = "http://localhost:8001"


async def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    print()


async def test_manual_notification(notification_type: str = "email"):
    """Test sending a manual notification"""
    print("=" * 60)
    print(f"Testing Manual {notification_type.upper()} Notification")
    print("=" * 60)
    
    payload = {
        "notification_type": notification_type,
        "recipient": "trader@example.com" if notification_type == "email" else "+1234567890",
        "message": f"Test {notification_type} notification from test script",
        "subject": "Test Alert" if notification_type == "email" else None
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/notifications/send", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    print()


async def test_alert_evaluation(
    symbol: str,
    confidence_overall: float,
    tp1_confidence: float
):
    """Test alert rule evaluation"""
    print("=" * 60)
    print(f"Testing Alert Evaluation for {symbol}")
    print("=" * 60)
    print(f"Overall Confidence: {confidence_overall:.1%}")
    print(f"TP1 Confidence: {tp1_confidence:.1%}")
    print()
    
    params = {
        "reco_id": f"test-{datetime.now().timestamp()}",
        "symbol": symbol,
        "confidence_overall": confidence_overall,
        "tp1_confidence": tp1_confidence,
        "entry_price": 150.00,
        "tp1_price": 165.00
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/alerts/evaluate", params=params)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Alerts Triggered: {result.get('alerts_triggered', [])}")
        if result.get('alerts_triggered'):
            for alert in result['alerts_triggered']:
                print(f"  - {alert['rule_name']} (Rule ID: {alert['rule_id']})")
        else:
            print("  No alerts triggered")
    print()


async def run_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NOTIFICATION SERVICE TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Health check
        await test_health()
        
        # Test 2: Manual email notification
        await test_manual_notification("email")
        
        # Test 3: Manual SMS notification
        await test_manual_notification("sms")
        
        # Test 4: Manual push notification
        await test_manual_notification("push")
        
        # Test 5: Alert evaluation - Low confidence (no alerts)
        await test_alert_evaluation("AAPL", 0.65, 0.62)
        
        # Test 6: Alert evaluation - Moderate confidence (one alert if enabled)
        await test_alert_evaluation("TSLA", 0.75, 0.72)
        
        # Test 7: Alert evaluation - High confidence (multiple alerts)
        await test_alert_evaluation("NVDA", 0.85, 0.88)
        
        # Test 8: Alert evaluation - Very high confidence (all alerts)
        await test_alert_evaluation("MSFT", 0.92, 0.94)
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        print()
        print("Check the notification service logs to see the notifications")
        print("that would have been sent.")
        print()
        
    except httpx.ConnectError:
        print("❌ ERROR: Could not connect to notification service")
        print(f"   Make sure the service is running at {BASE_URL}")
        print()
        print("To start the service:")
        print("  cd services/notification_service")
        print("  python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_tests())
