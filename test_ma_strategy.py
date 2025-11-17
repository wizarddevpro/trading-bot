import os
import sys
import pandas as pd

import dotenv
dotenv.load_dotenv()

# Make sure we can import from modules/
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from modules.ma_strategy import MovingAverageStrategy


def main():
  # Read input CSV file
  csv_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_prices.csv')
  if not os.path.exists(csv_file):
    print(f"Error: Missing data file: {csv_file}")
    return
  
  df = pd.read_csv(csv_file)
  
  # Ensure timestamp is sorted
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  df = df.sort_values('timestamp').reset_index(drop=True)
  
  # Calculate moving averages and generate signals
  short_window = os.getenv('SHORT_WINDOW', 50)
  long_window = os.getenv('LONG_WINDOW', 200)
  print(f'Using short window: {short_window}, long window: {long_window}')

  strategy = MovingAverageStrategy(short_window=int(short_window), long_window=int(long_window))
  df = strategy.calculate_moving_averages(df)
  df = strategy.generate_signals(df)
  
  # Save results to CSV file
  output_file = os.path.join(os.path.dirname(__file__), 'data', 'btc_signals.csv')
  results_df = df.copy()
  results_df['price'] = results_df['price'].apply(lambda x: f'{float(x):.2f}')
  results_df['short_ma'] = results_df['short_ma'].apply(lambda x: f'{float(x):.2f}')
  results_df['long_ma'] = results_df['long_ma'].apply(lambda x: f'{float(x):.2f}')
  results_df.to_csv(output_file, index=False)
  print(f'Moving averages and signals calculated and saved to: \n\t{output_file}')
  print(f'Total rows: {len(df)}')


if __name__ == '__main__':
  main()
