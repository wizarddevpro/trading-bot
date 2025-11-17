import matplotlib.pyplot as plt
import os

import dotenv
dotenv.load_dotenv()

def plot_strategy_results(df, output_image, show_plot=True):
  # Use 'price' if available, otherwise 'close'
  price_col = 'price' if 'price' in df.columns else 'close'

  short_window = int(os.getenv('SHORT_WINDOW', 50))  
  long_window = int(os.getenv('LONG_WINDOW', 200))
  
  plt.figure(figsize=(12, 8))

  plt.subplot(2, 1, 1)
  plt.plot(df[price_col], label="Price", alpha=0.5)
  plt.plot(df['short_ma'], label=f'MA{short_window}', alpha=0.8)
  plt.plot(df['long_ma'], label=f'MA{long_window}', alpha=0.8)

  buy_signals = df[df['signal'] == 'BUY']
  sell_signals = df[df['signal'] == 'SELL']
  plt.scatter(buy_signals.index, buy_signals[price_col], 
              color='red', marker='^', label='BUY', s=100)
  plt.scatter(sell_signals.index, sell_signals[price_col], 
              color='blue', marker='v', label='SELL', s=100)
  
  plt.xlabel('Time')
  plt.ylabel('Price')
  plt.title('Price Chart with Moving Averages and Signals')
  plt.legend()
  plt.grid(True, alpha=0.3)
  
  plt.subplot(2, 1, 2)
  plt.plot(df['portfolio_value'], label='Portfolio Value', color='green')
  plt.xlabel('Time')
  plt.ylabel('Portfolio Value ($)')
  plt.title('Portfolio Value Over Time')
  plt.legend()
  plt.grid(True, alpha=0.3)

  dirname = os.path.dirname(__file__)
  filename = os.path.join(os.path.dirname(dirname), output_image)

  plt.tight_layout()
  plt.savefig(filename)
  if show_plot:
    plt.show()
  else:
    plt.close()