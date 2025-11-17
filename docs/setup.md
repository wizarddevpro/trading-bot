# Trading Bot - Setup Guide

Step-by-step instructions for installing, configuring, and operating the BTC & TAO trading bot toolkit (multi-coin with Telegram integration).

---

## Prerequisites

- **Python 3.8+** (tested on Python 3.13)
- **pip** for dependency management
- Stable internet connection (Binance API access)
- macOS, Linux, or Windows

---

## Environment Setup

```bash
git clone https://github.com/Icebitz/trading-bot.git
cd trading-bot

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

> Keep the virtual environment active whenever you run project scripts.

---

## Project Layout

```
trading-bot/
├── bot/                    # Telegram handlers & graph helpers
│   ├── commands.py
│   ├── config.py
│   ├── graph_generator.py
│   ├── poller.py
│   ├── telegram.py
│   └── user_preferences.py
├── modules/                # Core trading logic
│   ├── analyzer.py         # Price chart generation
│   ├── backtester.py       # Portfolio simulation logic
│   ├── detector.py         # Volatility & pattern summaries
│   ├── historical.py       # Binance 1m backfill helper
│   ├── ma_strategy.py      # Moving-average strategy
│   ├── recorder.py         # Base recorder (BTC-only)
│   └── visualizer.py       # Signal + equity plotting
├── data/                   # CSV outputs (created at runtime)
├── charts/                 # Generated chart images
├── docs/                   # Documentation (this folder)
├── live_signal_monitor.py  # Real-time BUY/SELL alert loop
├── multi_coin_recorder.py  # BTC & TAO recorder
├── test_backtester.py      # Smoke script for backtesting stage
├── test_visualizer.py      # Charting smoke test
├── requirements.txt        # Python dependencies
└── README.md               # Project overview
```

---

## Dependency Snapshot

`requirements.txt` currently pins the core stack:

```
pandas>=1.3.0
requests>=2.25.0
schedule>=1.1.0
pytz>=2021.1
matplotlib>=3.3.0
```

Install optional tooling (e.g., `pytest`) as needed via `pip install pytest`.

---

## Core Workflows

### 1. Record Minute-Level Prices (BTC & TAO)

```bash
source venv/bin/activate
python multi_coin_recorder.py
```

- Writes data to `data/btc_prices.csv` and `data/tao_prices.csv`
- Handles API hiccups with retries and minimal logging noise
- Press `Ctrl+C` to stop recording

**Customise programmatically:**

```python
from modules.recorder import Recorder

btc_recorder = Recorder(symbol='BTCUSDT', filename='data/btc_prices.csv')
tao_recorder = Recorder(symbol='TAOUSDT', filename='data/tao_prices.csv')
btc_recorder.start()
tao_recorder.start()
```

### 2. Backtest the Strategy

```bash
python test_backtester.py
```

- Consumes the latest `data/<coin>_prices.csv`
- Produces `data/<coin>_backtest.csv` with price, MAs, portfolio metrics
- Uses environment-configured MA windows per coin (`SHORT_WINDOW`, `LONG_WINDOW`, `LOW/MID/HIGH_WINDOW`)

### 3. Visualise Results

```bash
python modules/analyzer.py        # 24h price chart → charts/price_chart.png
python test_visualizer.py         # Equity + signal chart → charts/strategy_results.png
```

### 4. Monitor Live Signals + Telegram (Optional)

```bash
export TELEGRAM_BOT_TOKEN="xxx"
export TELEGRAM_CHAT_ID="yyy"
python live_signal_monitor.py
```

- Recomputes moving averages every minute from both `data/btc_prices.csv` and `data/tao_prices.csv`
- Sends BUY/SELL/HOLD messages plus `/3ma` chart responses to active Telegram chats

### 5. Request 3-MA Chart On Demand

Inside Telegram:
```
/3ma
```

- Pulls LOW/MID/HIGH window sizes from `.env`
- Generates `charts/<coin>_3ma_strategy.png` and sends it to the requesting chat

---

## Advanced Configuration

**Adjust recording cadence**
```python
Recorder(interval=300)    # record every 5 minutes
```

**Backfill missing minutes**
```python
from modules.historical import fetch_minute_prices
rows = fetch_minute_prices('BTCUSDT', start_dt, end_dt)
```

**Tune strategy windows via .env**
```
SHORT_WINDOW=50
LONG_WINDOW=200
LOW_WINDOW=10
MID_WINDOW=30
HIGH_WINDOW=90
TAO_LOW_WINDOW=20
```

---

## Troubleshooting

| Issue | Fix |
| --- | --- |
| `ModuleNotFoundError` | Activate venv and rerun `pip install -r requirements.txt` |
| Binance API errors | Check network, retry later, or swap endpoint in `modules/recorder.py` |
| Charts not displaying | Headless environments still save PNGs; comment out `plt.show()` if needed |
| CSV permission errors | `chmod 644 data/*.csv` |
| Missing backtest files | Ensure recorder produced data and rerun `test_backtester.py` |

---

## Best Practices

- Keep the recorder running in a dedicated terminal for continuous data.
- Version-control your notebooks/scripts but ignore `data/`, `charts/`, `venv/`, and `__pycache__/`.
- Snapshot CSV outputs before major experiments.
- Log key findings in `docs/observations.md` after each analysis pass (include both coins).
- Run `python -m pytest` occasionally to smoke-test the workflow.

---

## Contribution Guide

1. Create a feature branch.
2. Add or update smoke scripts in `test_*.py`.
3. Run through the core workflow with fresh data.
4. Update documentation (README + docs/).
5. Open a pull request describing behaviour changes and test evidence.

---

## Reference Links

- [Binance Spot API](https://binance-docs.github.io/apidocs/spot/en/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/)

---

*Last Updated: November 10, 2025*

