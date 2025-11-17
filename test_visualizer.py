#!/usr/bin/env python3
"""Test script for visualizer.py - generates strategy visualization charts for BTC and TAO."""

import os
import sys
import pandas as pd
from datetime import timedelta

import dotenv
dotenv.load_dotenv()

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.visualizer import plot_strategy_results


# Coin configuration
COINS = {
    'BTC': {
        'file': 'data/btc_backtest.csv',
        'output': 'charts/btc_strategy_results.png',
        'name': 'Bitcoin'
    },
    'TAO': {
        'file': 'data/tao_backtest.csv',
        'output': 'charts/tao_strategy_results.png',
        'name': 'Bittensor'
    }
}


def process_coin_visualization(coin_key, coin_config):
    """Generate visualization for a single coin."""
    coin_name = coin_config['name']
    backtest_file = os.path.join(os.path.dirname(__file__), coin_config['file'])
    output_image = coin_config['output']
    
    print("\n" + "=" * 80)
    print(f"Generating visualization for {coin_name} ({coin_key})")
    print("=" * 80)
    
    if not os.path.exists(backtest_file):
        print(f"⚠️  Warning: Backtest file not found: {backtest_file}")
        print(f"   Skipping {coin_name} visualization.")
        print(f"   Please run test_backtester.py first to generate backtest data.")
        return False
    
    print(f"Reading backtest results from: {backtest_file}")
    df = pd.read_csv(backtest_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Check if we have price data
    if 'price' not in df.columns and 'close' not in df.columns:
        print(f"⚠️  Error: No 'price' or 'close' column found in data.")
        return False
    
    if df.empty:
        print(f"⚠️  Warning: No data in {backtest_file}")
        return False
    
    # Filter to last 24 hours
    last_timestamp = df.index.max()
    cutoff_time = last_timestamp - timedelta(hours=24)
    df = df[df.index >= cutoff_time]
    
    if df.empty:
        print(f"⚠️  Warning: No data available for the last 24 hours.")
        return False
    
    print(f"Data points (last 24 hours): {len(df)}")
    
    # Ensure charts directory exists
    os.makedirs('charts', exist_ok=True)
    
    # Generate visualization
    output_path = os.path.join(os.path.dirname(__file__), output_image)
    plot_strategy_results(df, output_image)
    
    print(f"✅ Chart saved to: {output_path}")
    return True


def main():
    """Generate visualizations for all coins."""
    print("=" * 80)
    print("Multi-Coin Visualizer")
    print("=" * 80)
    
    success_count = 0
    
    # Process each coin
    for coin_key, coin_config in COINS.items():
        if process_coin_visualization(coin_key, coin_config):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if success_count > 0:
        print(f"✅ Successfully generated {success_count} visualization(s)")
        for coin_key, coin_config in COINS.items():
            output_path = os.path.join(os.path.dirname(__file__), coin_config['output'])
            if os.path.exists(output_path):
                print(f"   - {coin_config['name']}: {output_path}")
    else:
        print("⚠️  No visualizations were generated.")
        print("   Please run test_backtester.py first to generate backtest data.")


if __name__ == '__main__':
  main()

