"""Data manager for CSV file operations."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
import pytz

logger = logging.getLogger(__name__)


class DataManager:
    def __init__(self, filename: str):
        self.filename = Path(filename)
        self._ensure_directory()
    
    def _ensure_directory(self):
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.debug(f"Directory creation skipped: {e}")
    
    def get_last_timestamp(self) -> Optional[datetime]:
        jst = pytz.timezone('Asia/Tokyo')
        now_ts_jst = datetime.now(jst).replace(second=0, microsecond=0)
        now_ts = now_ts_jst.replace(tzinfo=None)
        
        try:
            if not self.filename.exists():
                return now_ts
            
            df = pd.read_csv(self.filename)
            if df.empty or 'timestamp' not in df.columns:
                return now_ts
            
            last_timestamp = pd.to_datetime(df['timestamp'].iloc[-1])
            return last_timestamp.replace(tzinfo=None)
            
        except Exception as e:
            logger.debug(f"Error reading last timestamp: {e}")
            return now_ts
    
    def load_dataframe(self) -> pd.DataFrame:
        try:
            if not self.filename.exists():
                return pd.DataFrame()
            
            if self.filename.stat().st_size == 0:
                return pd.DataFrame()

            df = pd.read_csv(self.filename)
            return df
            
        except Exception as e:
            logger.error(f"Error loading dataframe: {e}")
            return pd.DataFrame()
    
    def save_data(self, rows: List[Dict], deduplicate: bool = True) -> bool:
        if not rows:
            return False
        
        try:
            new_df = pd.DataFrame(rows)
            
            existing_df = self.load_dataframe()
            
            if not existing_df.empty:
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
            combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce').round(2)
            
            combined_df = combined_df.dropna(subset=['price'])
            
            if deduplicate:
                combined_df = combined_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'], keep='last')
            
            combined_df.to_csv(self.filename, index=False)
            return True
            
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False
    
    def file_exists(self) -> bool:
        return self.filename.exists()
    
    def get_dataframe(self) -> pd.DataFrame:
        df = self.load_dataframe()
        if df.empty:
            return df
        return df.sort_values('timestamp')

