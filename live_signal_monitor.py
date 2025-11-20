#!/usr/bin/env python3
"""Live signal monitor - checks signals in real time and logs BUY/SELL signals for multiple coins."""

import os
import sys
import time
import pandas as pd
from datetime import datetime

import dotenv
dotenv.load_dotenv()

# Set matplotlib to use non-interactive backend
import matplotlib
matplotlib.use('Agg')

# Make sure we can import from modules/
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.ma_strategy import MovingAverageStrategy

# Import bot modules
from bot.telegram import send_message_to_chat, send_photo_to_chat
from bot.poller import process_updates
from bot.graph_generator import generate_signal_plot
from bot.user_preferences import get_all_active_users
from bot.config import get_coin_config

import matplotlib.pyplot as plt


# Coin configuration
COINS = {
    'BTC': {
        'symbol': 'BTCUSDT',
        'file': 'data/btc_prices.csv',
        'name': 'Bitcoin'
    },
    'TAO': {
        'symbol': 'TAOUSDT',
        'file': 'data/tao_prices.csv',
        'name': 'Bittensor'
    }
}


def get_latest_signal(df):
  if df.empty or 'signal' not in df.columns:
    return None
  # Get the last non-NaN signal
  valid_signals = df[df['signal'].notna()]
  if valid_signals.empty:
    return None
  return valid_signals['signal'].iloc[-1]


def format_log_message(coin_name, signal, row):
  timestamp = row['timestamp']
  price = row['price']
  
  if signal == 'HOLD': header_icon = '💎'
  elif signal == 'BUY': header_icon = '🟢'
  elif signal == 'SELL': header_icon = '🔴'

  message = (
    f"{header_icon} {coin_name} {signal}\n"
    f"🕘 {timestamp} → 💲 {price:.2f}\n"
  )

  return message


def get_last_total_and_buy_price(signal_file):
  """Get the last total value and last BUY price from the signal CSV file."""
  last_total = 0.0
  last_buy_price = None
  
  if not os.path.exists(signal_file):
    return last_total, last_buy_price
  
  try:
    df = pd.read_csv(signal_file)
    if df.empty:
      return last_total, last_buy_price
    
    # Get last total
    if 'total' in df.columns:
      last_total = float(df['total'].iloc[-1])
    
    # Get last BUY price (find the most recent BUY signal)
    if 'signal' in df.columns and 'price' in df.columns:
      buy_signals = df[df['signal'] == 'BUY']
      if not buy_signals.empty:
        last_buy_price = float(buy_signals['price'].iloc[-1])
    
    return last_total, last_buy_price
  except Exception as e:
    print(f"Error reading signal file {signal_file}: {e}")
    return last_total, last_buy_price


def save_signal_with_profit(coin_key, signal, price, timestamp):
  """Save signal to CSV with profit and total columns.
  Profit calculation starts from BUY: profit is only calculated on SELL (sell_price - buy_price).
  """
  project_root = os.path.dirname(__file__)
  signal_file = os.path.join(project_root, 'data', f'{coin_key.lower()}_signals.csv')
  
  # Get last total and last BUY price
  last_total, last_buy_price = get_last_total_and_buy_price(signal_file)
  
  # Calculate profit based on signal type
  # Profit calculation starts from BUY: only SELL calculates actual profit
  if signal == 'BUY':
    # BUY: profit is 0 (we're just recording the buy price)
    profit = 0.0
    total = last_total  # Total doesn't change on BUY, profit is calculated on SELL
  elif signal == 'SELL':
    # SELL: calculate profit as (sell_price - buy_price) if we have a previous BUY
    if last_buy_price is not None:
      profit = float(price) - last_buy_price  # Actual profit from the trade
    else:
      # No previous BUY, profit is just the sell price
      profit = float(price)
    total = last_total + profit  # Add profit to total
  else:  # HOLD
    profit = 0.0
    total = last_total  # Total doesn't change for HOLD
  
  # Prepare data
  signal_data = {
    'time': timestamp,
    'price': float(price),
    'signal': signal,
    'profit': profit,
    'total': total
  }
  
  # Append to CSV file
  try:
    signal_df = pd.DataFrame([signal_data])
    if os.path.exists(signal_file):
      signal_df.to_csv(signal_file, mode='a', header=False, index=False)
    else:
      signal_df.to_csv(signal_file, mode='w', header=True, index=False)
  except Exception as e:
    print(f"Error saving signal to file: {e}")


def process_coin_signals(coin_key, coin_config, last_signals):
  """Process signals for a specific coin."""
  csv_file = os.path.join(os.path.dirname(__file__), coin_config['file'])
  coin_name = coin_config['name']
  
  if not os.path.exists(csv_file):
    return
  
  try:
    df = pd.read_csv(csv_file)
    
    if df.empty:
      return
    
    # Ensure timestamp is sorted
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Get coin-specific configuration and create strategy
    config = get_coin_config(coin_key)
    strategy = MovingAverageStrategy(
      short_window=config['short_window'],
      long_window=config['long_window']
    )
    
    # Calculate moving averages and generate signals
    df = strategy.calculate_moving_averages(df)
    df = strategy.generate_signals(df)
    
    # Get the latest signal
    current_signal = get_latest_signal(df)
    
    if current_signal is None:
      return
    
    # Check if signal changed to BUY or SELL
    if current_signal in ['BUY', 'SELL', 'HOLD']:
      # Get the latest row with signal
      valid_df = df[df['signal'].notna()]
      if not valid_df.empty:
        latest_row = valid_df.iloc[-1]
        
        # Only process if this is a new signal (not the same as last)
        last_signal = last_signals.get(coin_key)
        if current_signal != last_signal:
          log_message = format_log_message(coin_name, current_signal, latest_row)
          print(f"*** {log_message} ***")
          
          # Save signal to CSV with profit and total (skip HOLD signals)
          if current_signal != 'HOLD':
            save_signal_with_profit(
              coin_key=coin_key,
              signal=current_signal,
              price=latest_row['price'],
              timestamp=latest_row['timestamp']
            )
          
          # Get all active users (send to everyone who started signal detection)
          active_users = get_all_active_users()
          
          if active_users:
            # Send message to all active users
            for chat_id in active_users:
              send_message_to_chat(chat_id, log_message)
            
            # Send plot for BUY/SELL signals only (not HOLD)
            if current_signal != 'HOLD':
              plot_filepath = os.path.join(
                os.path.dirname(__file__), 
                'charts', 
                f'{coin_key.lower()}_signal_plot.png'
              )
              if generate_signal_plot(df, coin_key, plot_filepath):
                for chat_id in active_users:
                  send_photo_to_chat(chat_id, plot_filepath)
          
          last_signals[coin_key] = current_signal
    else:
      # Reset last_signal if we're back to HOLD
      if last_signals.get(coin_key) in ['BUY', 'SELL']:
        last_signals[coin_key] = None
        
  except Exception as e:
    print(f"[{datetime.now()}] Error processing {coin_name} data: {e}")



def main():
  check_interval = 60  # Check every 60 seconds
  
  # Track last signals for each coin
  last_signals = {coin: None for coin in COINS.keys()}
  
  # Telegram bot polling
  telegram_update_offset = None
  last_signal_check_time = 0
  
  print("=" * 80)
  print("Multi-Coin Signal Monitor Started")
  print(f"Monitoring coins: {', '.join([c['name'] for c in COINS.values()])}")
  print(f"Check interval: {check_interval} seconds")
  print("Telegram commands enabled: /coin, /btc, /tao, /test, /start, /help")
  print("=" * 80)
  print()
  
  try:
    while True:
      current_time = time.time()
      
      # Check for Telegram commands frequently (every 2 seconds)
      telegram_update_offset = process_updates(offset=telegram_update_offset)
      
      # Check signals at the specified interval
      if current_time - last_signal_check_time >= check_interval:
        last_signal_check_time = current_time
        
        # Process signals for each coin
        for coin_key, coin_config in COINS.items():
          process_coin_signals(coin_key, coin_config, last_signals)
      
      # Sleep briefly to avoid busy waiting
      time.sleep(2)
      
  except KeyboardInterrupt:
    print()
    print("=" * 80)
    print("Multi-Coin Signal Monitor Stopped")
    print("=" * 80)


if __name__ == '__main__':
  main()

