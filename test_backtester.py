#!/usr/bin/env python3
"""Test backtester - processes MA strategy and runs backtest for BTC and TAO."""

import os
import sys
import pandas as pd

import dotenv
dotenv.load_dotenv()

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.backtester import Backtester
from modules.ma_strategy import MovingAverageStrategy

# Import bot config helper
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))
from bot.config import get_coin_config


# Coin configuration
COINS = {
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


def process_coin_backtest(coin_key, coin_config):
    """Process backtest for a single coin."""
    coin_name = coin_config['name']
    data_file = os.path.join(os.path.dirname(__file__), coin_config['file'])
    output_file = os.path.join(os.path.dirname(__file__), coin_config['output'])
    
    print("\n" + "=" * 80)
    print(f"Processing {coin_name} ({coin_key})")
    print("=" * 80)
    
    if not os.path.exists(data_file):
        print(f"⚠️  Warning: Price data file not found: {data_file}")
        print(f"   Skipping {coin_name} backtest.")
        return None
    
    print(f"Reading price data from: {data_file}")
    df = pd.read_csv(data_file)
    
    if df.empty:
        print(f"⚠️  Warning: No data in {data_file}")
        print(f"   Skipping {coin_name} backtest.")
        return None
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Get coin-specific configuration
    config = get_coin_config(coin_key)
    short_window = config['short_window']
    long_window = config['long_window']
    initial_capital = config['initial_capital']
    
    print(f'Using short window: {short_window}, long window: {long_window}')
    print(f'Initial capital: ${initial_capital:,.2f}')
    
    strategy = MovingAverageStrategy(short_window=short_window, long_window=long_window)
    df = strategy.calculate_moving_averages(df)
    df = strategy.generate_signals(df)
    
    # Filter out rows with NaN signals
    df = df.dropna(subset=['signal'])
    
    if df.empty:
        print(f"⚠️  Warning: No valid signals generated for {coin_name}")
        print(f"   Skipping {coin_name} backtest.")
        return None
    
    # Run backtest
    print("\nRunning backtest...")
    backtester = Backtester(initial_capital=initial_capital)
    performance = backtester.run_backtest(df)
    
    # Add portfolio value and daily return to dataframe
    results_df = df.copy()
    results_df['portfolio_value'] = backtester.portfolio_value
    results_df['daily_return'] = results_df['portfolio_value'].pct_change() * 100
    
    # Format and save results
    results_df['price'] = results_df['price'].apply(lambda x: f'{float(x):.2f}')
    results_df['short_ma'] = results_df['short_ma'].apply(lambda x: f'{float(x):.2f}')
    results_df['long_ma'] = results_df['long_ma'].apply(lambda x: f'{float(x):.2f}')
    results_df['portfolio_value'] = results_df['portfolio_value'].apply(lambda x: f'{float(x):.2f}')
    results_df['daily_return'] = results_df['daily_return'].apply(lambda x: f'{float(x):.2f}')
    results_df.to_csv(output_file, index=False)
    
    print(f'\n✅ Backtest completed and saved to: {output_file}')
    print(f'   Total rows processed: {len(results_df)}')
    print(f'\n📊 Performance Summary:')
    print(f'   Total return: {performance["total_return"]:.2f}%')
    print(f'   Final value: ${performance["final_value"]:,.2f}')
    print(f'   Max drawdown: {performance["max_drawdown"]:.2f}%')
    print(f'   Win rate: {performance["win_rate"]:.6f}%')
    
    return performance


def main():
    """Process backtests for all coins."""
    print("=" * 60)
    print("Multi-Coin Backtester")
    print("=" * 60)
    
    results = {}
    
    # Process each coin
    for coin_key, coin_config in COINS.items():
        performance = process_coin_backtest(coin_key, coin_config)
        if performance:
            results[coin_key] = performance
    
    # Summary
    if results:
        print("\n" + "=" * 80)
        print("SUMMARY - All Coins")
        print("=" * 80)
        for coin_key, performance in results.items():
            coin_name = COINS[coin_key]['name']
            print(f"\n{coin_name} ({coin_key}):")
            print(f"  Total return: {performance['total_return']:.2f}%")
            print(f"  Final value: ${performance['final_value']:,.2f}")
            print(f"  Max drawdown: {performance['max_drawdown']:.2f}%")
            print(f"  Win rate: {performance['win_rate']:.6f}%")
    else:
        print("\n⚠️  No backtests were completed. Please check that price data files exist.")


if __name__ == '__main__':
	main()
