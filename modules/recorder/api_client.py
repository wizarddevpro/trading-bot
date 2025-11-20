"""API client for fetching price data from Binance."""

import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

BINANCE_PRICE_URL = 'https://api.binance.com/api/v3/ticker/price'
BINANCE_KLINES_URL = 'https://api.binance.com/api/v3/klines'


class APIClient:
    def __init__(self, symbol: str, timeout: int = 10):
        self.symbol = symbol
        self.api_url = BINANCE_PRICE_URL
        self.timeout = timeout
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
    
    def fetch_price(self) -> Optional[float]:
        try:
            response = requests.get(
                f"{self.api_url}?symbol={self.symbol}",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if 'price' not in data:
                raise ValueError("Price data not found in API response")
            
            price = float(data['price'])
            self.consecutive_failures = 0
            return price
            
        except Exception as e:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.error(f"API error (attempt {self.consecutive_failures}): {e}")
            else:
                logger.debug(f"API error (attempt {self.consecutive_failures}): {e}")
            return None
    
    def reset_failures(self):
        self.consecutive_failures = 0
    
    @staticmethod
    def _to_millis(dt: datetime) -> int:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return int(dt.timestamp() * 1000)
    
    def fetch_minute_prices(
        self,
        start_time: datetime,
        end_time: datetime,
        session: Optional[requests.Session] = None
    ) -> List[Dict]:
        if start_time >= end_time:
            return []
        
        s = session or requests.Session()
        
        start_ms = self._to_millis(start_time)
        end_ms = self._to_millis(end_time)
        
        # Binance returns up to 1000 candles per request
        limit = 1000
        interval = '1m'
        
        results: List[Dict] = []
        current_start = start_ms
        
        while current_start < end_ms:
            params = {
                'symbol': self.symbol,
                'interval': interval,
                'startTime': current_start,
                'endTime': end_ms,
                'limit': limit,
            }
            
            try:
                resp = s.get(BINANCE_KLINES_URL, params=params, timeout=15)
                resp.raise_for_status()
                klines = resp.json()
                
                if not klines:
                    break
                
                for k in klines:
                    open_time_ms = k[0]
                    close_price = float(k[4])
                    open_time_dt = datetime.fromtimestamp(
                        open_time_ms / 1000.0,
                        tz=timezone.utc
                    )
                    # We align to the opening minute timestamp for consistency
                    results.append({
                        'timestamp': open_time_dt,
                        'price': round(close_price, 2)
                    })
                
                # Advance to next batch (next candle after the last returned one)
                last_open_time_ms = klines[-1][0]
                current_start = last_open_time_ms + 60_000
                
                # Safety: avoid infinite loops
                if len(klines) < limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching historical data batch: {e}")
                break
        
        return results

