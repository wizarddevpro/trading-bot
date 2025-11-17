"""Telegram bot polling logic."""

from bot.telegram import get_updates
from bot.commands import handle_command


def process_updates(offset=None):
    """Process Telegram updates and return new offset."""
    updates = get_updates(offset=offset)
    new_offset = offset
    
    if updates and updates.get('ok'):
        for update in updates.get('result', []):
            new_offset = update['update_id'] + 1
            
            if 'message' not in update:
                continue
            
            message = update['message']
            chat_id = str(message['chat']['id'])
            text = message.get('text', '').strip()
            
            # Handle commands
            if text.startswith('/test'):
                handle_command('/test', chat_id)
            elif text.startswith('/start'):
                handle_command('/start', chat_id)
            elif text.startswith('/help'):
                handle_command('/help', chat_id)
            elif text.startswith('/'):
                # Unknown command
                handle_command(text.split()[0], chat_id)
    
    return new_offset

