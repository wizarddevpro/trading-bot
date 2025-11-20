"""User preferences storage for Telegram bot."""

import os
import json
from pathlib import Path
import dotenv

dotenv.load_dotenv()

PREFERENCES_FILE = Path(__file__).parent.parent / 'data' / 'user_preferences.json'


def load_preferences():
    """Load user preferences from file."""
    if not PREFERENCES_FILE.exists():
        return {}
    
    try:
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_preferences(preferences):
    """Save user preferences to file."""
    PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f, indent=2)


def get_user_coin(chat_id: str):
    """Get the coin preference for a user. Defaults to 'BTC'."""
    preferences = load_preferences()
    return preferences.get(str(chat_id), {}).get('coin', 'BTC')


def set_user_coin(chat_id: str, coin: str):
    """Set the coin preference for a user."""
    preferences = load_preferences()
    if str(chat_id) not in preferences:
        preferences[str(chat_id)] = {}
    preferences[str(chat_id)]['coin'] = coin.upper()
    save_preferences(preferences)


def get_all_users_for_coin(coin: str):
    """Get all chat IDs that are subscribed to a specific coin."""
    preferences = load_preferences()
    coin = coin.upper()
    return [
        chat_id for chat_id, prefs in preferences.items()
        if prefs.get('coin', 'BTC').upper() == coin
    ]


def set_user_active(chat_id: str, active: bool = True):
    """Set user as active (started signal detection)."""
    preferences = load_preferences()
    if str(chat_id) not in preferences:
        preferences[str(chat_id)] = {}
    preferences[str(chat_id)]['active'] = active
    save_preferences(preferences)


def is_user_active(chat_id: str):
    """Check if user is active (has started signal detection)."""
    preferences = load_preferences()
    return preferences.get(str(chat_id), {}).get('active', False)


def get_all_active_users():
    """Get all chat IDs of active users."""
    preferences = load_preferences()
    users = [
        chat_id for chat_id, prefs in preferences.items()
        if prefs.get('active', False)
    ]

    valid_ids = load_valid_chat_ids()

    users = [user for user in users if user in valid_ids]

    return users


def load_valid_chat_ids():
    """Load Telegram chat IDs from environment variable."""
    ids = os.getenv("TELEGRAM_CHAT_ID", "")
    if not ids:
        return []
    
    # Split by comma, trim whitespace
    return [chat_id.strip() for chat_id in ids.split(",") if chat_id.strip()]
