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
        dict with keys: short_window, long_window, initial_capital,
        low_window, mid_window, high_window
    """
    coin = coin.upper()

    def _get_value(key: str, default: str):
        return os.getenv(f'{coin}_{key}', os.getenv(key, default))
    
    short_window = _get_value('SHORT_WINDOW', '50')
    long_window = _get_value('LONG_WINDOW', '200')
    low_window = _get_value('LOW_WINDOW', '10')
    mid_window = _get_value('MID_WINDOW', '20')
    high_window = _get_value('HIGH_WINDOW', '50')
    initial_capital = os.getenv(
        f'{coin}_INITIAL_CAPITAL',
        os.getenv('INITIAL_CAPITAL', '1000000')
    )
    
    return {
        'short_window': int(short_window),
        'long_window': int(long_window),
        'initial_capital': float(initial_capital),
        'low_window': int(low_window),
        'mid_window': int(mid_window),
        'high_window': int(high_window),
    }

