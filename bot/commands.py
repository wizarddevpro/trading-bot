"""Command handlers for Telegram bot."""

import os
import sys
import pandas as pd
import dotenv

dotenv.load_dotenv()

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from modules.backtester import Backtester
from modules.ma_strategy import MovingAverageStrategy

from bot.telegram import send_message_to_chat, send_photo_to_chat
from bot.graph_generator import generate_backtest_graph
from bot.user_preferences import (
    get_user_coin, 
    set_user_coin, 
    set_user_active,
    is_user_active
)
from bot.config import get_coin_config


def run_backtest_for_coin(coin: str):
    """Run backtest for a specific coin and save to file."""
    coin = coin.upper()
    coin_config = {
        'BTC': {
            'file': 'data/btc_prices.csv',
            'output': 'data/btc_backtest.csv',
            'name': 'Bitcoin'
        },
        'TAO': {
            'file': 'data/tao_prices.csv',
            'output': 'data/tao_backtest.csv',
            'name': 'Bittensor'
        }
    }
    
    if coin not in coin_config:
        return None, f"Unsupported coin: {coin}"
    
    coin_info = coin_config[coin]
    project_root = os.path.dirname(os.path.dirname(__file__))
    data_file = os.path.join(project_root, coin_info['file'])
    output_file = os.path.join(project_root, coin_info['output'])
    
    if not os.path.exists(data_file):
        return None, f"{coin_info['name']} price data file not found. Please run multi_coin_recorder.py first."
    
    try:
        df = pd.read_csv(data_file)
        if df.empty:
            return None, f"No data available for {coin_info['name']}"
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Get coin-specific configuration
        config = get_coin_config(coin)
        short_window = config['short_window']
        long_window = config['long_window']
        initial_capital = config['initial_capital']
        
        strategy = MovingAverageStrategy(short_window=short_window, long_window=long_window)
        df = strategy.calculate_moving_averages(df)
        df = strategy.generate_signals(df)
        df = df.dropna(subset=['signal'])
        
        if df.empty:
            return None, f"No valid signals generated for {coin_info['name']}"
        
        # Run backtest
        backtester = Backtester(initial_capital=initial_capital)
        performance = backtester.run_backtest(df)
        
        # Add portfolio value and daily return
        results_df = df.copy()
        results_df['portfolio_value'] = backtester.portfolio_value
        results_df['daily_return'] = results_df['portfolio_value'].pct_change() * 100
        
        # Format and save
        results_df['price'] = results_df['price'].apply(lambda x: f'{float(x):.2f}')
        results_df['short_ma'] = results_df['short_ma'].apply(lambda x: f'{float(x):.2f}')
        results_df['long_ma'] = results_df['long_ma'].apply(lambda x: f'{float(x):.2f}')
        results_df['portfolio_value'] = results_df['portfolio_value'].apply(lambda x: f'{float(x):.2f}')
        results_df['daily_return'] = results_df['daily_return'].apply(lambda x: f'{float(x):.2f}')
        results_df.to_csv(output_file, index=False)
        
        return performance, None
        
    except Exception as e:
        return None, f"Error running backtest: {str(e)}"


def handle_command(command: str, chat_id: str):
    """Handle Telegram bot commands."""
    if command == '/start':
        # Start signal detection for user
        set_user_active(chat_id, True)
        current_coin = get_user_coin(chat_id)
        coin_names = {'BTC': 'Bitcoin', 'TAO': 'Bittensor'}
        coin_name = coin_names.get(current_coin, current_coin)
        
        message = (
            "✅ Signal detection started! 🚀\n\n"
            f"Current trading token: {current_coin} ({coin_name})\n\n"
            "You will now receive real-time trading signals:\n"
            "• BUY/SELL signals with charts\n"
            "• HOLD signals (message only)\n\n"
            "Use /coin to change your trading token.\n"
            "Use /test to run backtest for your current token.\n"
            "Use /help for all commands."
        )
        send_message_to_chat(chat_id, message)
    
    elif command == '/test':
        # Get user's coin preference
        user_coin = get_user_coin(chat_id)
        coin_names = {'BTC': 'Bitcoin', 'TAO': 'Bittensor'}
        coin_name = coin_names.get(user_coin, user_coin)
        
        send_message_to_chat(chat_id, f"🔄 Running {coin_name} backtest...\nThis may take a moment...")
        
        # Run backtest
        performance, error = run_backtest_for_coin(user_coin)
        
        if error:
            send_message_to_chat(chat_id, f"❌ {error}")
            return
        
        # Generate and send graph
        send_message_to_chat(chat_id, "📊 Generating backtest graph...")
        graph_path, graph_error = generate_backtest_graph(user_coin)
        
        if graph_error:
            send_message_to_chat(chat_id, f"⚠️ Graph generation failed: {graph_error}")
        elif graph_path and os.path.exists(graph_path):
            if send_photo_to_chat(chat_id, graph_path):
                # Send performance summary
                summary = (
                    f"✅ {coin_name} backtest completed!\n\n"
                    f"📈 Performance Summary:\n"
                    f"• Total return: {performance['total_return']:.2f}%\n"
                    f"• Final value: ${performance['final_value']:,.2f}\n"
                    f"• Max drawdown: {performance['max_drawdown']:.2f}%\n"
                    f"• Win rate: {performance['win_rate']:.6f}%\n\n"
                    f"Results saved to: data/{user_coin.lower()}_backtest.csv"
                )
                send_message_to_chat(chat_id, summary)
            else:
                send_message_to_chat(chat_id, "⚠️ Failed to send graph. Results saved to file.")
        else:
            send_message_to_chat(chat_id, "⚠️ Failed to generate graph. Results saved to file.")
    
    elif command == '/coin':
        current_coin = get_user_coin(chat_id)
        message = (
            f"Current trading token: {current_coin}\n\n"
            "Select a trading token:\n"
            "/btc - Set to BTC\n"
            "/tao - Set to TAO"
        )
        send_message_to_chat(chat_id, message)
    
    elif command == '/btc':
        set_user_coin(chat_id, 'BTC')
        send_message_to_chat(chat_id, "✅ Trading token set to BTC")
    
    elif command == '/tao':
        set_user_coin(chat_id, 'TAO')
        send_message_to_chat(chat_id, "✅ Trading token set to TAO")
    
    elif command == '/help':
        current_coin = get_user_coin(chat_id)
        active_status = "✅ Active" if is_user_active(chat_id) else "❌ Inactive"
        coin_names = {'BTC': 'Bitcoin', 'TAO': 'Bittensor'}
        coin_name = coin_names.get(current_coin, current_coin)
        
        help_text = (
            f"📊 Trading Bot Commands\n\n"
            f"Status: {active_status}\n"
            f"Current token: {current_coin} ({coin_name})\n\n"
            "Available commands:\n"
            "/start - Start signal detection\n"
            "/coin - Show token selection menu\n"
            "/btc - Set token to BTC\n"
            "/tao - Set token to TAO\n"
            "/test - Run backtest for current token\n"
            "/help - Show this help message"
        )
        send_message_to_chat(chat_id, help_text)
    
    else:
        send_message_to_chat(chat_id, f"Unknown command: {command}. Use /help for available commands.")

