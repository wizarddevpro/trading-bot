#!/usr/bin/env python3
"""Flask dashboard for price history and signals analysis."""

import os
import sys
import pandas as pd
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Coin configuration
COINS = {
    'BTC': {
        'symbol': 'BTCUSDT',
        'price_file': 'data/btc_prices.csv',
        'signal_file': 'data/btc_signals.csv',
        'name': 'Bitcoin'
    },
    'TAO': {
        'symbol': 'TAOUSDT',
        'price_file': 'data/tao_prices.csv',
        'signal_file': 'data/tao_signals.csv',
        'name': 'Bittensor'
    }
}


def get_project_root():
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_price_data(coin_key):
    """Load price data for a coin."""
    coin_config = COINS.get(coin_key.upper())
    if not coin_config:
        return pd.DataFrame()
    
    file_path = os.path.join(get_project_root(), coin_config['price_file'])
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Filter to last 24 hours by default
        if not df.empty:
            last_timestamp = df['timestamp'].max()
            cutoff_time = last_timestamp - timedelta(hours=24)
            df = df[df['timestamp'] >= cutoff_time]
        
        return df
    except Exception as e:
        print(f"Error loading price data for {coin_key}: {e}")
        return pd.DataFrame()


def load_signal_data(coin_key):
    """Load signal data for a coin."""
    coin_config = COINS.get(coin_key.upper())
    if not coin_config:
        return pd.DataFrame()
    
    file_path = os.path.join(get_project_root(), coin_config['signal_file'])
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return df
        
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time', ascending=False)
        
        return df
    except Exception as e:
        print(f"Error loading signal data for {coin_key}: {e}")
        return pd.DataFrame()


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html', coins=list(COINS.keys()))


@app.route('/api/price/<coin>')
def get_price_data(coin):
    """API endpoint to get price data for a coin."""
    df = load_price_data(coin)
    
    if df.empty:
        return jsonify({
            'success': False,
            'message': f'No price data available for {coin}'
        }), 404
    
    # Convert to JSON format
    data = {
        'success': True,
        'coin': coin.upper(),
        'coin_name': COINS.get(coin.upper(), {}).get('name', coin),
        'timestamps': df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'prices': df['price'].tolist()
    }
    
    return jsonify(data)


@app.route('/api/signals/<coin>')
def get_signal_data(coin):
    """API endpoint to get signal data for a coin."""
    df = load_signal_data(coin)
    
    if df.empty:
        return jsonify({
            'success': False,
            'message': f'No signal data available for {coin}'
        }), 404
    
    # Convert DataFrame to list of dictionaries
    signals = df.to_dict('records')
    
    # Convert datetime objects to strings
    for signal in signals:
        if isinstance(signal.get('time'), pd.Timestamp):
            signal['time'] = signal['time'].strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        'success': True,
        'coin': coin.upper(),
        'coin_name': COINS.get(coin.upper(), {}).get('name', coin),
        'signals': signals
    }
    
    return jsonify(data)


@app.route('/api/coins')
def get_coins():
    """API endpoint to get list of available coins."""
    coins_info = []
    for key, config in COINS.items():
        price_df = load_price_data(key)
        signal_df = load_signal_data(key)
        
        coins_info.append({
            'key': key,
            'name': config['name'],
            'has_price_data': not price_df.empty,
            'has_signal_data': not signal_df.empty,
            'latest_price': float(price_df['price'].iloc[-1]) if not price_df.empty else None,
            'latest_signal': signal_df['signal'].iloc[0] if not signal_df.empty else None,
            'total_profit': float(signal_df['total'].iloc[0]) if not signal_df.empty and 'total' in signal_df.columns else None
        })
    
    return jsonify({'success': True, 'coins': coins_info})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

