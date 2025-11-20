#!/usr/bin/env python3
"""Multi-coin recorder - records both BTC and TAO price history in real time."""

import logging
import threading
import time
from pathlib import Path

from modules.recorder import Recorder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def start_recorder(symbol: str, filename: str, interval: int = 60):
    try:
        logger.info(f"Starting {symbol} recorder...")
        recorder = Recorder(
            symbol=symbol,
            interval=interval,
            filename=filename,
            verbose=True
        )
        recorder.start()
    except Exception as e:
        logger.error(f"Error in {symbol} recorder: {e}", exc_info=True)
        raise


def main():
    """Start recorders for both BTC and TAO."""
    project_root = Path(__file__).parent
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # BTC recorder configuration
    btc_file = data_dir / 'btc_prices.csv'
    btc_thread = threading.Thread(
        target=start_recorder,
        args=('BTCUSDT', str(btc_file), 60),
        daemon=True,
        name='BTC-Recorder'
    )
    
    # TAO recorder configuration
    tao_file = data_dir / 'tao_prices.csv'
    tao_thread = threading.Thread(
        target=start_recorder,
        args=('TAOUSDT', str(tao_file), 60),
        daemon=True,
        name='TAO-Recorder'
    )
    
    print("=" * 80)
    print("Multi-Coin Recorder")
    print("=" * 80)
    print(f"Recording BTC/USDT → {btc_file}")
    print(f"Recording TAO/USDT → {tao_file}")
    print(f"Interval: 60 seconds (1 minute)")
    print("=" * 80)
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # Start both recorders
    try:
        btc_thread.start()
        logger.info("BTC recorder thread started")
        
        tao_thread.start()
        logger.info("TAO recorder thread started")
        
        # Monitor threads
        while True:
            time.sleep(1)
            
            # Check thread status
            if not btc_thread.is_alive():
                logger.error("BTC recorder thread stopped unexpectedly")
                if not tao_thread.is_alive():
                    logger.error("Both recorder threads stopped")
                    break
            
            if not tao_thread.is_alive():
                logger.error("TAO recorder thread stopped unexpectedly")
                if not btc_thread.is_alive():
                    logger.error("Both recorder threads stopped")
                    break
                    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        print()
        print("=" * 80)
        print("Multi-Coin Recorder Stopped")
        print("=" * 80)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

