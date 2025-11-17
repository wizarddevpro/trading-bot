"""Command handlers for Telegram bot."""

import os
from bot.telegram import send_message_to_chat, send_photo_to_chat
from bot.graph_generator import generate_backtest_graph


def handle_command(command: str, chat_id: str):
    """Handle Telegram bot commands."""
    if command == '/test':
        send_message_to_chat(chat_id, "Generating backtest graph...")
        graph_path, error = generate_backtest_graph()
        
        if error:
            send_message_to_chat(chat_id, error)
            return
        
        if graph_path and os.path.exists(graph_path):
            if send_photo_to_chat(chat_id, graph_path):
                send_message_to_chat(chat_id, "Backtest graph (last 24 hours) sent successfully!")
            else:
                send_message_to_chat(chat_id, "Failed to send graph. Please try again.")
        else:
            send_message_to_chat(chat_id, "Failed to generate graph. Please try again.")
    
    elif command == '/start':
        send_message_to_chat(chat_id, "Welcome! Use /test to get the backtest graph.")
    
    elif command == '/help':
        help_text = (
            "Available commands:\n"
            "/test - Get backtest graph (last 24 hours)\n"
            "/start - Welcome message\n"
            "/help - Show this help message"
        )
        send_message_to_chat(chat_id, help_text)
    
    else:
        send_message_to_chat(chat_id, f"Unknown command: {command}. Use /help for available commands.")

