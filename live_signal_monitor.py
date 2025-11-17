#!/usr/bin/env python3
"""Live signal monitor - checks signals in real time and logs BUY/SELL signals."""

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
from bot.telegram import (
    send_broadcast_message,
    send_broadcast_photo,
    load_chat_ids
)
from bot.poller import process_updates
from bot.graph_generator import generate_signal_plot

import matplotlib.pyplot as plt



def get_latest_signal(df):
  if df.empty or 'signal' not in df.columns:
    return None
  # Get the last non-NaN signal
  valid_signals = df[df['signal'].notna()]
  if valid_signals.empty:
    return None
  return valid_signals['signal'].iloc[-1]


def format_log_message(signal, row):
  timestamp = row['timestamp']
  price = row['price']
  
  if signal == 'HOLD': header_icon = '🔍'
  elif signal == 'BUY': header_icon = '🟢'
  elif signal == 'SELL': header_icon = '🔴'

  if pd.notna(row['short_ma']):
    short_ma_str = f"{row['short_ma']:.2f}"
  else:
    short_ma_str = 'N/A'
  
  if pd.notna(row['long_ma']):
    long_ma_str = f"{row['long_ma']:.2f}"
  else:
    long_ma_str = 'N/A'
  
  message = (
    f"{header_icon} {signal}\n"
    f"================================================\n"
    f"🕘 {timestamp}\n"
    f"💲 ${price:.2f}\n"
  )

  if signal != 'HOLD':
    message += f"🔍 {short_ma_str}\n"
    message += f"🔍 {long_ma_str}\n"

  return message



def main():
  csv_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_prices.csv')
  check_interval = 60  # Check every 60 seconds
  
  short_window = os.getenv('SHORT_WINDOW', 50)
  long_window = os.getenv('LONG_WINDOW', 200)
  strategy = MovingAverageStrategy(short_window=int(short_window), long_window=int(long_window))
  last_signal = None
  
  # Telegram bot polling
  telegram_update_offset = None
  last_signal_check_time = 0
  
  print("=" * 80)
  print("Live Signal Monitor Started")
  print(f"Monitoring: {csv_file}")
  print(f"Check interval: {check_interval} seconds")
  print("Telegram commands enabled: /test, /start, /help")
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
        
        # Check if file exists
        if not os.path.exists(csv_file):
          print(f"[{datetime.now()}] Waiting for data file: {csv_file}")
          time.sleep(2)
          continue
        
        # Read and process data
        try:
          df = pd.read_csv(csv_file)
          
          if df.empty:
            print(f"[{datetime.now()}] No data in file yet...")
            time.sleep(2)
            continue
          
          # Ensure timestamp is sorted
          df['timestamp'] = pd.to_datetime(df['timestamp'])
          df = df.sort_values('timestamp').reset_index(drop=True)
          
          # Calculate moving averages and generate signals
          df = strategy.calculate_moving_averages(df)
          df = strategy.generate_signals(df)
          
          # Get the latest signal
          current_signal = get_latest_signal(df)
          
          if current_signal is None:
            print(f"[{datetime.now()}] Waiting for enough data to calculate signals...")
            time.sleep(2)
            continue
          
          # Check if signal changed to BUY or SELL
          if current_signal in ['BUY', 'SELL', 'HOLD']:
            # Get the latest row with signal
            valid_df = df[df['signal'].notna()]
            if not valid_df.empty:
              latest_row = valid_df.iloc[-1]
              
              # Only log if this is a new BUY/SELL signal (not the same as last)
              if current_signal != last_signal:
                log_message = format_log_message(current_signal, latest_row)
                print(f"*** {log_message} ***")

                last_signal = current_signal

                send_broadcast_message(log_message)

                if current_signal == 'HOLD':
                  time.sleep(2)
                  continue

                plot_filepath = os.path.join(os.path.dirname(__file__), 'charts', 'signal_plot.png')
                if generate_signal_plot(df, plot_filepath):
                  send_broadcast_photo(plot_filepath)

          else:
            # Reset last_signal if we're back to HOLD
            if last_signal in ['BUY', 'SELL']:
              last_signal = None
          
        except Exception as e:
          print(f"[{datetime.now()}] Error processing data: {e}")
      
      # Sleep briefly to avoid busy waiting
      time.sleep(2)
      
  except KeyboardInterrupt:
    print()
    print("=" * 80)
    print("Live Signal Monitor Stopped")
    print("=" * 80)


if __name__ == '__main__':
  main()

