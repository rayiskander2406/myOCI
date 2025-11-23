#!/usr/bin/env python3
"""
ntfy to Telegram Forwarder
Subscribes to ntfy topics and forwards notifications to Telegram
"""

import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ntfy-telegram-forwarder')

# Configuration from environment variables
NTFY_URL = os.getenv('NTFY_URL', 'http://oci-ntfy')
NTFY_TOPICS = os.getenv('NTFY_TOPICS', 'monitoring-alerts').split(',')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Priority emoji mapping
PRIORITY_EMOJI = {
    'urgent': '🚨',
    'high': '⚠️',
    'default': '📢',
    'low': 'ℹ️',
    'min': '💬'
}

# Tag emoji mapping for common alert types
TAG_EMOJI = {
    'critical': '🔴',
    'warning': '🟡',
    'success': '✅',
    'info': '🔵',
    'error': '❌',
    'netdata': '📊',
    'docker': '🐳',
    'server': '🖥️',
    'network': '🌐',
    'disk': '💾',
    'cpu': '⚙️',
    'memory': '🧠'
}


def validate_config():
    """Validate required configuration"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        sys.exit(1)

    if not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_CHAT_ID environment variable is required")
        sys.exit(1)

    logger.info(f"Configuration validated")
    logger.info(f"NTFY URL: {NTFY_URL}")
    logger.info(f"Subscribing to topics: {', '.join(NTFY_TOPICS)}")
    logger.info(f"Telegram Chat ID: {TELEGRAM_CHAT_ID}")


def format_message(notification: Dict[str, Any]) -> str:
    """Format ntfy notification for Telegram"""
    message_parts = []

    # Add priority emoji
    # ntfy sends priority as integer: 1=min, 2=low, 3=default, 4=high, 5=urgent
    priority_int = notification.get('priority', 3)
    priority_map = {1: 'min', 2: 'low', 3: 'default', 4: 'high', 5: 'urgent'}
    priority_name = priority_map.get(priority_int, 'default') if isinstance(priority_int, int) else priority_int
    emoji = PRIORITY_EMOJI.get(priority_name, PRIORITY_EMOJI['default'])
    message_parts.append(f"{emoji} <b>Priority: {priority_name.upper()}</b>")

    # Add tags with emojis if present
    tags = notification.get('tags', [])
    if tags:
        tag_line = ' '.join([TAG_EMOJI.get(tag, f"#{tag}") for tag in tags])
        message_parts.append(tag_line)

    # Add title if present
    if 'title' in notification and notification['title']:
        message_parts.append(f"\n<b>{notification['title']}</b>")

    # Add main message
    message_parts.append(f"\n{notification.get('message', 'No message')}")

    # Add topic info
    topic = notification.get('topic', 'unknown')
    message_parts.append(f"\n\n<i>Topic: {topic}</i>")

    # Add timestamp
    if 'time' in notification:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S EET',
                                 time.localtime(notification['time']))
        message_parts.append(f"<i>Time: {timestamp}</i>")

    return '\n'.join(message_parts)


def send_to_telegram(message: str) -> bool:
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to Telegram successfully")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to Telegram: {e}")
        return False


def subscribe_to_ntfy(topic: str):
    """Subscribe to ntfy topic and forward messages"""
    url = f"{NTFY_URL}/{topic}/json"

    logger.info(f"Subscribing to {url}")

    while True:
        try:
            response = requests.get(url, stream=True, timeout=None)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        notification = json.loads(line.decode('utf-8'))

                        # Skip keepalive messages
                        if notification.get('event') == 'keepalive':
                            logger.debug("Received keepalive")
                            continue

                        # Process message events
                        if notification.get('event') == 'message':
                            logger.info(f"Received notification from topic '{topic}': {notification.get('message', '')[:50]}")

                            # Format and send to Telegram
                            telegram_message = format_message(notification)
                            send_to_telegram(telegram_message)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse notification: {e}")
                        continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {e}")
            logger.info("Reconnecting in 5 seconds...")
            time.sleep(5)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            sys.exit(0)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            logger.info("Reconnecting in 5 seconds...")
            time.sleep(5)


def test_telegram_connection():
    """Send a test message to verify Telegram connection"""
    logger.info("Testing Telegram connection...")

    test_message = (
        "🤖 <b>ntfy-Telegram Forwarder Started</b>\n\n"
        f"Monitoring topics: {', '.join(NTFY_TOPICS)}\n"
        f"Server: OCI Cairo\n"
        f"Time: {time.strftime('%Y-%m-%d %H:%M:%S EET')}\n\n"
        "<i>Ready to receive alerts!</i>"
    )

    if send_to_telegram(test_message):
        logger.info("Telegram connection test successful")
    else:
        logger.error("Telegram connection test failed")
        sys.exit(1)


def main():
    """Main entry point"""
    logger.info("Starting ntfy-Telegram forwarder")

    # Validate configuration
    validate_config()

    # Test Telegram connection
    test_telegram_connection()

    # For now, subscribe to the first topic
    # In the future, we can handle multiple topics with threads
    if NTFY_TOPICS:
        topic = NTFY_TOPICS[0].strip()
        logger.info(f"Starting subscription to topic: {topic}")
        subscribe_to_ntfy(topic)
    else:
        logger.error("No topics configured")
        sys.exit(1)


if __name__ == '__main__':
    main()
