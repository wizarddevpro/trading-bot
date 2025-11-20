"""Telegram API functions for sending messages and photos."""

import os
import requests
import dotenv
from bot.user_preferences import get_all_active_users

dotenv.load_dotenv()


def get_bot_token():
    """Get Telegram bot token from environment."""
    return os.getenv('TELEGRAM_BOT_TOKEN')


def get_api_url():
    """Get Telegram API base URL."""
    token = get_bot_token()
    if not token:
        return None
    return f"https://api.telegram.org/bot{token}"


def send_message_to_chat(chat_id: str, message: str):
    """Send a message to a specific chat ID."""
    api_url = get_api_url()
    if not api_url:
        return False
    
    url = f"{api_url}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending message to {chat_id}: {e}")
        return False


def send_photo_to_chat(chat_id: str, photo_path: str):
    """Send a photo to a specific chat ID."""
    api_url = get_api_url()
    if not api_url:
        return False
    
    url = f"{api_url}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            payload = {'chat_id': chat_id}
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error sending photo to {chat_id}: {e}")
        return False


def send_broadcast_message(message: str):
    """Send a message to all configured chat IDs."""
    chat_ids = get_all_active_users()
    for chat_id in chat_ids:
        send_message_to_chat(chat_id, message)


def send_broadcast_photo(photo_path: str):
    """Send a photo to all configured chat IDs."""
    chat_ids = get_all_active_users()
    for chat_id in chat_ids:
        send_photo_to_chat(chat_id, photo_path)


def get_updates(offset=None):
    """Get updates from Telegram bot API."""
    api_url = get_api_url()
    if not api_url:
        return None
    
    url = f"{api_url}/getUpdates"
    params = {'timeout': 5}
    if offset:
        params['offset'] = offset
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

