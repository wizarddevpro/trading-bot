# Trading Bot Dashboard

A simple web dashboard for visualizing price history and trading signals.

## Features

- **Price History Chart**: Interactive line chart showing price data for the last 24 hours
- **Signals Table**: Complete table of all trading signals with profit/loss tracking
- **Real-time Stats**: Latest price, total profit, and latest signal displayed at the top
- **Multi-Coin Support**: Switch between BTC and TAO coins
- **Auto-refresh**: Dashboard updates every 30 seconds

## Installation

Make sure Flask is installed:

```bash
pip install flask
```

Or install all requirements:

```bash
pip install -r ../requirements.txt
```

## Running the Dashboard

From the project root directory:

```bash
python dashboard/run_dashboard.py
```

Or from the dashboard directory:

```bash
cd dashboard
python run_dashboard.py
```

The dashboard will be available at: `http://localhost:5000`

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/coins` - List all available coins with stats
- `GET /api/price/<coin>` - Get price data for a coin (BTC or TAO)
- `GET /api/signals/<coin>` - Get signal data for a coin (BTC or TAO)

## Data Sources

The dashboard reads from:
- Price data: `data/btc_prices.csv` and `data/tao_prices.csv`
- Signal data: `data/btc_signals.csv` and `data/tao_signals.csv`

