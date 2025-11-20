"""Telegram bot package for trading bot."""

from bot.telegram import (
    send_message_to_chat,
    send_photo_to_chat,
    send_broadcast_message,
    send_broadcast_photo,
    get_updates
)
from bot.commands import handle_command
from bot.graph_generator import generate_backtest_graph, generate_signal_plot
from bot.user_preferences import (
    get_user_coin,
    set_user_coin,
    get_all_users_for_coin,
    get_all_active_users
)

__all__ = [
    'send_message_to_chat',
    'send_photo_to_chat',
    'send_broadcast_message',
    'send_broadcast_photo',
    'get_updates',
    'handle_command',
    'generate_backtest_graph',
    'generate_signal_plot',
    'get_user_coin',
    'set_user_coin',
    'get_all_users_for_coin',
    'get_all_active_users'
]

