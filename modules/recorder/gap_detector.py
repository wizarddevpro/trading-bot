"""Gap detector for identifying missing time periods in price data."""

import logging
from datetime import timedelta
from typing import List, Dict

import pandas as pd

logger = logging.getLogger(__name__)


class GapDetector:
    def __init__(self, interval: int):
        self.interval = interval
        self.expected_interval = timedelta(seconds=interval)
    
    def detect_missing_periods(self, df: pd.DataFrame) -> List[Dict]:
        if df.empty or 'timestamp' not in df.columns:
            return []
        
        try:
            df_sorted = df.sort_values('timestamp').copy()
            missing_periods = []
            
            for i in range(len(df_sorted) - 1):
                current_time = df_sorted.iloc[i]['timestamp']
                next_time = df_sorted.iloc[i + 1]['timestamp']
                actual_interval = next_time - current_time
                
                if actual_interval > self.expected_interval * 1.5:
                    missing_periods.append({
                        'start': current_time,
                        'end': next_time
                    })
            
            return missing_periods
            
        except Exception as e:
            logger.debug(f"Error detecting missing periods: {e}")
            return []
    
    def find_gap_before(self, last_timestamp: pd.Timestamp, current_timestamp: pd.Timestamp) -> bool:
        if last_timestamp is None:
            return False
        
        expected_next = (last_timestamp + timedelta(seconds=self.interval)).replace(second=0, microsecond=0)
        return expected_next < current_timestamp

