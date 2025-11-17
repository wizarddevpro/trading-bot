"""Graph generation functions for the bot."""

import os
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

# Make sure we can import from modules/
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from modules.visualizer import plot_strategy_results


def generate_backtest_graph():
    """Generate the backtest graph (last 24 hours) and return the file path."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    backtest_file = os.path.join(project_root, 'data', 'btc_backtest.csv')
    
    if not os.path.exists(backtest_file):
        return None, "Backtest file not found. Please run test_backtester.py first."
    
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
            return None, "No data available for the last 24 hours."
        
        # Ensure charts directory exists
        charts_dir = os.path.join(project_root, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        # Generate visualization
        output_image = "charts/strategy_results.png"
        plot_strategy_results(df, output_image, show_plot=False)
        
        full_path = os.path.join(project_root, output_image)
        return full_path, None
        
    except Exception as e:
        return None, f"Error generating graph: {str(e)}"


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

