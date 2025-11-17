"""Graph generation functions for the bot."""

import os
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

# Make sure we can import from modules/
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from modules.visualizer import plot_strategy_results
from bot.config import get_coin_config


def generate_backtest_graph(coin='BTC'):
    """Generate the backtest graph (last 24 hours) for a specific coin and return the file path."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    # Map coin to file
    coin_files = {
        'BTC': 'data/btc_backtest.csv',
        'TAO': 'data/tao_backtest.csv'
    }
    
    coin_names = {
        'BTC': 'Bitcoin',
        'TAO': 'Bittensor'
    }
    
    coin = coin.upper()
    if coin not in coin_files:
        return None, f"Unsupported coin: {coin}. Supported coins: BTC, TAO"
    
    backtest_file = os.path.join(project_root, coin_files[coin])
    coin_name = coin_names.get(coin, coin)
    
    if not os.path.exists(backtest_file):
        return None, f"{coin_name} backtest file not found. Please run test_backtester.py first."
    
    try:
        df = pd.read_csv(backtest_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Check if we have price data
        if 'price' not in df.columns and 'close' not in df.columns:
            return None, "Error: No 'price' or 'close' column found in data."
        
        # Filter to last 24 hours
        if not df.empty:
            last_timestamp = df.index.max()
            cutoff_time = last_timestamp - timedelta(hours=24)
            df = df[df.index >= cutoff_time]
        
        if df.empty:
            return None, f"No {coin_name} data available for the last 24 hours."
        
        # Ensure charts directory exists
        charts_dir = os.path.join(project_root, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        # Generate visualization
        output_image = f"charts/{coin.lower()}_strategy_results.png"
        plot_strategy_results(df, output_image, show_plot=False)
        
        full_path = os.path.join(project_root, output_image)
        return full_path, None
        
    except Exception as e:
        return None, f"Error generating {coin_name} graph: {str(e)}"


def _get_price_column(df):
    if 'price' in df.columns:
        return 'price'
    if 'close' in df.columns:
        return 'close'
    return None


def generate_three_ma_chart(coin='BTC'):
    """Generate chart showing price with low/mid/high moving averages."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    
    coin_files = {
        'BTC': 'data/btc_prices.csv',
        'TAO': 'data/tao_prices.csv'
    }
    
    coin_names = {
        'BTC': 'Bitcoin',
        'TAO': 'Bittensor'
    }
    
    coin = coin.upper()
    if coin not in coin_files:
        return None, f"Unsupported coin: {coin}. Supported coins: BTC, TAO"
    
    price_file = os.path.join(project_root, coin_files[coin])
    coin_name = coin_names.get(coin, coin)
    
    if not os.path.exists(price_file):
        return None, f"{coin_name} price data file not found. Please run multi_coin_recorder.py first."
    
    try:
        df = pd.read_csv(price_file)
        if df.empty:
            return None, f"No {coin_name} price data available."
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        price_col = _get_price_column(df)
        if not price_col:
            return None, "Error: No 'price' or 'close' column found in data."
        
        config = get_coin_config(coin)
        low_window = config['low_window']
        mid_window = config['mid_window']
        high_window = config['high_window']
        
        df['low_ma'] = df[price_col].rolling(window=low_window).mean()
        df['mid_ma'] = df[price_col].rolling(window=mid_window).mean()
        df['high_ma'] = df[price_col].rolling(window=high_window).mean()
        
        last_timestamp = df['timestamp'].max()
        cutoff_time = last_timestamp - timedelta(hours=24)
        df = df[df['timestamp'] >= cutoff_time]
        
        df = df.dropna(subset=['low_ma', 'mid_ma', 'high_ma'])
        if df.empty:
            return None, f"Not enough data to compute {coin_name} 3-MA chart for the last 24 hours."
        
        charts_dir = os.path.join(project_root, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        output_path = os.path.join(charts_dir, f"{coin.lower()}_3ma_strategy.png")
        
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df[price_col], label='Price', color='#9E9E9E', linewidth=1.2)
        plt.plot(df['timestamp'], df['low_ma'], label=f'Low MA ({low_window})', color='#4CAF50', linewidth=1.5)
        plt.plot(df['timestamp'], df['mid_ma'], label=f'Mid MA ({mid_window})', color='#FFC107', linewidth=1.5)
        plt.plot(df['timestamp'], df['high_ma'], label=f'High MA ({high_window})', color='#2196F3', linewidth=1.5)
        
        plt.title(f"{coin_name} 3-MA Strategy (Last 24h)")
        plt.xlabel("Time")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return output_path, None
    except Exception as e:
        return None, f"Error generating {coin_name} 3-MA chart: {str(e)}"


def generate_signal_plot(df, filepath):
    """Generate a signal plot from dataframe."""
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    now = df["timestamp"].iloc[-1]
    start = now - pd.Timedelta(days=1)
    df = df[df["timestamp"] >= start]

    if df.empty:
        return False

    plt.figure(figsize=(8, 4))

    plt.plot(df["timestamp"], df["price"], label="Price", linewidth=1)
    
    if "short_ma" in df.columns:
        plt.plot(df["timestamp"], df["short_ma"], label="Short MA", linewidth=1)
    
    if "long_ma" in df.columns:
        plt.plot(df["timestamp"], df["long_ma"], label="Long MA", linewidth=1)

    plt.title("BTC Price + Moving Averages (Last 24 hours)")
    plt.xlabel("Time")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return True

