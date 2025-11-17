"""Configuration helper for coin-specific settings."""

import os
import dotenv

dotenv.load_dotenv()


def get_coin_config(coin: str):
    """Get coin-specific configuration from environment variables.
    
    Looks for coin-specific values first (e.g., BTC_SHORT_WINDOW), 
    then falls back to generic values (e.g., SHORT_WINDOW).
    
    Args:
        coin: Coin symbol (BTC, TAO, etc.)
        
    Returns:
        dict with keys: short_window, long_window, initial_capital
    """
    coin = coin.upper()
    
    # Get coin-specific values, fallback to generic values
    short_window = os.getenv(
        f'{coin}_SHORT_WINDOW',
        os.getenv('SHORT_WINDOW', '50')
    )
    
    long_window = os.getenv(
        f'{coin}_LONG_WINDOW',
        os.getenv('LONG_WINDOW', '200')
    )
    
    initial_capital = os.getenv(
        f'{coin}_INITIAL_CAPITAL',
        os.getenv('INITIAL_CAPITAL', '1000000')
    )
    
    return {
        'short_window': int(short_window),
        'long_window': int(long_window),
        'initial_capital': float(initial_capital)
    }

