#!/usr/bin/env python3
"""Multi-coin recorder - records both BTC and TAO price history in real time."""

import os
import sys
import threading
from pathlib import Path

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.recorder import Recorder


def start_recorder(symbol, filename):
    """Start a recorder for a specific coin."""
    recorder = Recorder(
        symbol=symbol,
        interval=60,
        filename=filename,
        verbose=True
    )
    recorder.start()


def main():
    """Start recorders for both BTC and TAO."""
    project_root = Path(__file__).parent
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # BTC recorder
    btc_file = data_dir / 'btc_prices.csv'
    btc_thread = threading.Thread(
        target=start_recorder,
        args=('BTCUSDT', str(btc_file)),
        daemon=True,
        name='BTC-Recorder'
    )
    
    # TAO recorder
    tao_file = data_dir / 'tao_prices.csv'
    tao_thread = threading.Thread(
        target=start_recorder,
        args=('TAOUSDT', str(tao_file)),
        daemon=True,
        name='TAO-Recorder'
    )
    
    print("=" * 80)
    print("Multi-Coin Recorder Started")
    print(f"Recording BTC to: {btc_file}")
    print(f"Recording TAO to: {tao_file}")
    print("=" * 80)
    print()
    
    # Start both recorders
    btc_thread.start()
    tao_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            btc_thread.join(timeout=1)
            tao_thread.join(timeout=1)
            
            # Check if threads are still alive
            if not btc_thread.is_alive() and not tao_thread.is_alive():
                print("Both recorders stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print("Multi-Coin Recorder Stopped")
        print("=" * 80)


if __name__ == '__main__':
    main()

