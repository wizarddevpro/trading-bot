"""Main recorder class for price data collection."""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import pytz
import schedule

from .api_client import APIClient
from .data_manager import DataManager
from .gap_detector import GapDetector

logger = logging.getLogger(__name__)


class Recorder:
    def __init__(
        self,
        symbol: str = 'TAOUSDT',
        interval: int = 60,
        filename: str = '../data/tao_prices.csv',
        verbose: bool = True
    ):
        self.symbol = symbol
        self.interval = interval
        self.verbose = verbose
        
        # Initialize components
        self.api_client = APIClient(symbol)
        self.data_manager = DataManager(filename)
        self.gap_detector = GapDetector(interval)
        
        # Logging state
        self.last_log_time = 0
        self.log_interval = 1800  # 30 minutes
    
    def _get_current_timestamp(self) -> datetime:
        jst = pytz.timezone('Asia/Tokyo')
        now_ts_jst = datetime.now(jst).replace(second=0, microsecond=0)
        return now_ts_jst.replace(tzinfo=None)
    
    def _fetch_historical_data(self, start_time: datetime, end_time: datetime) -> list:
        if start_time is None or end_time is None or start_time >= end_time:
            return []
        
        try:
            jst = pytz.timezone('Asia/Tokyo')
            start_aware = jst.localize(start_time).astimezone(pytz.utc)
            end_aware = jst.localize(end_time).astimezone(pytz.utc)
            
            return self.api_client.fetch_minute_prices(start_aware, end_aware)
        except Exception as e:
            logger.error(f"Historical fetch error: {e}")
            return []
    
    def _prepare_rows(self, price: float, current_timestamp: datetime) -> list:
        rows = []
        last_timestamp = self.data_manager.get_last_timestamp()
        
        if last_timestamp is None:
            rows.append({
                'timestamp': current_timestamp,
                'price': round(price, 2)
            })
        else:
            expected_next = (last_timestamp + timedelta(seconds=self.interval)).replace(second=0, microsecond=0)
            
            if expected_next > current_timestamp:
                rows.append({
                    'timestamp': current_timestamp,
                    'price': round(price, 2)
                })
            else:
                if expected_next < current_timestamp:
                    gap_duration = current_timestamp - expected_next
                    logger.info(
                        f"Gap detected: {gap_duration.total_seconds() / 60:.1f} minutes. "
                        f"Backfilling from {expected_next} to {current_timestamp}"
                    )
                    try:
                        historical_rows = self._fetch_historical_data(expected_next, current_timestamp)
                        
                        if historical_rows:
                            logger.info(f"Fetched {len(historical_rows)} historical records")
                            jst = pytz.timezone('Asia/Tokyo')
                            for r in historical_rows:
                                try:
                                    ts_jst = r['timestamp'].astimezone(jst).replace(second=0, microsecond=0)
                                    ts_local = ts_jst.replace(tzinfo=None)
                                    if ts_local < current_timestamp:
                                        rows.append({
                                            'timestamp': ts_local,
                                            'price': round(float(r['price']), 2)
                                        })
                                except Exception as e:
                                    logger.debug(f"Error processing historical row: {e}")
                                    continue
                            if rows:
                                logger.info(f"Prepared {len(rows)} records for backfill (including current)")
                        else:
                            logger.warning("No historical data retrieved for gap")
                    except Exception as e:
                        logger.error(f"Historical fetch failed: {e}", exc_info=True)
                
                # Always add current minute
                rows.append({
                    'timestamp': current_timestamp,
                    'price': round(price, 2)
                })
        
        return rows
    
    def save_price(self):
        # Fetch price from API
        price = self.api_client.fetch_price()
        if price is None:
            if self.api_client.consecutive_failures >= self.api_client.max_consecutive_failures:
                logger.warning("Failed to fetch price data")
            return
        
        # Get current timestamp
        current_timestamp = self._get_current_timestamp()
        
        # Prepare rows (including gap backfill)
        rows = self._prepare_rows(price, current_timestamp)
        
        # Save to file
        if not self.data_manager.save_data(rows):
            logger.error("Failed to save price data")
            return
        
        # Occasional logging
        current_time = time.time()
        if (current_time - self.last_log_time) >= self.log_interval:
            logger.info(f"{self.symbol}: ${price:,.2f}")
            self.last_log_time = current_time
    
    def backfill_on_startup(self) -> int:
        if not self.data_manager.file_exists():
            logger.info("No existing data file, skipping backfill")
            return 0
        
        try:
            df = self.data_manager.get_dataframe()
            if df.empty:
                return 0
            
            # Detect missing periods
            missing_periods = self.gap_detector.detect_missing_periods(df)
            
            if not missing_periods:
                logger.info("No gaps detected in existing data")
                return 0
            
            total_backfilled = 0
            for period in missing_periods:
                start_time = period['start']
                end_time = period['end']
                
                # Limit backfill to reasonable time ranges (e.g., last 7 days)
                max_backfill = timedelta(days=7)
                if (end_time - start_time) > max_backfill:
                    logger.warning(
                        f"Gap too large to backfill automatically: "
                        f"{start_time} to {end_time} ({(end_time - start_time).days} days). "
                        f"Limiting to last 7 days."
                    )
                    start_time = end_time - max_backfill
                
                logger.info(f"Backfilling gap: {start_time} to {end_time}")
                historical_rows = self._fetch_historical_data(start_time, end_time)
                
                if historical_rows:
                    jst = pytz.timezone('Asia/Tokyo')
                    rows_to_save = []
                    for r in historical_rows:
                        try:
                            ts_jst = r['timestamp'].astimezone(jst).replace(second=0, microsecond=0)
                            ts_local = ts_jst.replace(tzinfo=None)
                            rows_to_save.append({
                                'timestamp': ts_local,
                                'price': round(float(r['price']), 2)
                            })
                        except Exception as e:
                            logger.debug(f"Error processing historical row: {e}")
                            continue
                    
                    if rows_to_save:
                        if self.data_manager.save_data(rows_to_save):
                            total_backfilled += len(rows_to_save)
                            logger.info(f"Backfilled {len(rows_to_save)} records")
            
            if total_backfilled > 0:
                logger.info(f"Total backfilled: {total_backfilled} records")
            
            return total_backfilled
            
        except Exception as e:
            logger.error(f"Error during startup backfill: {e}")
            return 0
    
    def start(self, backfill_on_start: bool = True):
        # Backfill gaps on startup if requested
        if backfill_on_start:
            self.backfill_on_startup()
        
        # Initial save (this will also backfill any gap from last run to now)
        self.save_price()
        
        # Schedule periodic saves
        schedule.every(self.interval).seconds.do(self.save_price)
        
        logger.info(
            f"Started {self.symbol} recorder "
            f"(interval: {self.interval}s, file: {self.data_manager.filename})"
        )
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopped by user")
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(5)

