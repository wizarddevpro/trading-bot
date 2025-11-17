import pandas as pd
import matplotlib.pyplot as plt
import os

class Analyzer:
    def __init__(self, csv_file='data/btc_prices.csv', output_image='charts/price_chart.png'):
        self.dir_name = os.path.dirname(__file__)
        self.csv_file = os.path.join(os.path.dirname(self.dir_name), csv_file)
        self.output_image = os.path.join(os.path.dirname(self.dir_name), output_image)

    def load_and_plot(self, title='Price History'):
        df = pd.read_csv(self.csv_file)
        
        # Convert timestamp column
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        elif 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')

        # Get last 24 hours of data
        df = df.tail(30 * 60)

        # Create chart
        plt.figure(figsize=(12, 5))
        plt.plot(df.index, df['price'], label='Price', linewidth=1)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        os.makedirs(os.path.dirname(self.output_image), exist_ok=True)
        plt.savefig(self.output_image, dpi=300, bbox_inches='tight')
        print(f"Chart saved: {self.output_image}")
        
        # Show chart
        plt.show()
        
        return df

