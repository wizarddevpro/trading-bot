# 📈 BTC Trading Bot

A Python toolkit for collecting minute-level BTC/USDT data, analysing market structure, and exercising a moving-average trading workflow end-to-end.

## ✨ Features

- **Multi-coin recorder** for BTC and TAO with automatic gap detection and optional historical backfill.
- **Configurable signal engine** powered by moving-average crossover logic.
- **Strategy backtester** with portfolio value tracking and summary metrics.
- **Triple moving-average overlays** (LOW/MID/HIGH windows) including a Telegram-ready chart command.
- **Visual reporting** that plots prices, signals, and equity curves.
- **Telegram bot integration** that delivers BUY/SELL/HOLD signals plus `/3ma` chart snapshots.

---

## 🚀 Quick Start

```bash
# 0) Clone (optional if you're already inside the repo)
git clone https://github.com/Icebitz/trading-bot.git
cd trading-bot

# 1) Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2) Collect BTC/TAO prices once per minute
python multi_coin_recorder.py            # writes data/btc_prices.csv & data/tao_prices.csv

# 3) Run a strategy backtest (writes data/<coin>_backtest.csv)
python test_backtester.py

# 4) (Optional) Generate charts / analysis artefacts
python modules/analyzer.py               # price trend chart
python test_visualizer.py                # composite equity + signal chart

# 5) Start live monitoring + Telegram bot
python live_signal_monitor.py
```

---

## 🧭 Typical Workflow

1. **Ingest prices** via `multi_coin_recorder.py` (or `modules/recorder.py` if you only care about BTC).
2. **Backfill or clean gaps** using helpers inside `modules/historical.py` when needed.
3. **Backtest** the latest CSV with `test_backtester.py` to generate `data/<coin>_backtest.csv`.
4. **Visualise** results using `modules/analyzer.py` and `modules/visualizer.plot_strategy_results`, storing PNGs in `charts/`.
5. **Go live** with `live_signal_monitor.py`, which recomputes indicators, detects crossovers, and pushes Telegram alerts.

---

## 📡 Live Signal Monitor

`live_signal_monitor.py` watches `data/<coin>_prices.csv`, recomputes moving averages every minute, and prints/pushes new BUY/SELL signals. To enable Telegram alerts, make sure your `.env` (or exported env vars) includes:

```bash
export TELEGRAM_BOT_TOKEN="xxx"
export TELEGRAM_CHAT_ID="yyy"
python live_signal_monitor.py
```

The script throttles duplicate alerts and logs each actionable crossover with the current price and MA context.

---

## 📐 Triple Moving Average Analysis

Configure three independent moving-average windows by setting the following variables in a `.env` file (coin-specific overrides like `BTC_LOW_WINDOW` are also supported):

```bash
LOW_WINDOW=10
MID_WINDOW=20
HIGH_WINDOW=50
```

Once the bot is running, send `/3ma` to the Telegram bot to receive a price chart over the last 24 hours with the LOW, MID, and HIGH moving averages applied to your currently selected coin and recorded window sizes.

---

## 🤖 Telegram Commands

| Command | Description |
| --- | --- |
| `/start` | Enables signal delivery for your chat and reports the active coin. |
| `/coin` | Shows the token selection menu. |
| `/btc`, `/tao` | Switch the active token and persist the preference. |
| `/test` | Runs a backtest for the active token and shares a performance summary + chart. |
| `/3ma` | Sends a 24h triple moving-average chart using LOW/MID/HIGH windows from `.env`. |
| `/help` | Displays the current status plus all supported commands. |

---

## 📊 Artefacts & Outputs

| File | How it is created | Contents |
| --- | --- | --- |
| `data/btc_prices.csv` | `modules/recorder.py` | Minute-level BTC/USDT price history |
| `data/btc_signals.csv` | `test_ma_strategy.py` | Prices, short/long MAs, and signals |
| `data/btc_backtest.csv` | `test_backtester.py` | Portfolio value series and performance stats |
| `charts/price_chart.png` | `modules/analyzer.py` | Last-day price plot |
| `charts/strategy_results.png` | `test_visualizer.py` | Price, MAs, signals, and equity curve |

---

## 📦 Components & Modules

- `modules/recorder.py` — resilient live price ingestion.
- `modules/historical.py` — Binance 1m kline backfill helper.
- `modules/ma_strategy.py` — moving-average crossover logic.
- `modules/backtester.py` — capital, drawdown, and win-rate calculations.
- `modules/analyzer.py` — charting utility for recent price action.
- `modules/detector.py` — pattern/volatility summaries.
- `modules/visualizer.py` — plotting helper for combined signal/equity charts.
- `live_signal_monitor.py` — real-time monitoring + optional Telegram notifications.

---

## ✅ Testing & Validation

Lightweight smoke scripts exist for each stage. Run them individually (as shown above) or via:

```bash
python -m pytest
```

Pytest will discover the `test_*.py` files; keep in mind that these scripts print artefacts rather than strict assertions, so treat them as integration smoke tests.

---

## 📂 Project Structure

```
trading-bot/
├── bot/                    # Telegram bot handlers & helpers
│   ├── commands.py
│   ├── config.py
│   ├── graph_generator.py
│   ├── poller.py
│   ├── telegram.py
│   └── user_preferences.py
├── modules/                # Core trading logic
│   ├── analyzer.py
│   ├── backtester.py
│   ├── detector.py
│   ├── historical.py
│   ├── ma_strategy.py
│   ├── recorder.py
│   └── visualizer.py
├── data/                   # Runtime CSV outputs (prices, signals, backtests)
├── charts/                 # Generated chart images
├── docs/                   # Extended documentation
├── live_signal_monitor.py  # Real-time alert runner + Telegram bridge
├── multi_coin_recorder.py  # Recorder for BTC & TAO simultaneously
├── test_backtester.py
├── test_visualizer.py
├── requirements.txt
└── README.md
```

---

## 📖 Additional Docs

- `docs/setup.md` — expanded environment and Git setup guidance.
- `docs/observations.md` — log of market learnings and experiments.

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Pandas**, **NumPy**
- **Matplotlib**
- **Requests**
- **Schedule**

---

## ⚠️ Disclaimer

This project is for educational and research purposes only and does **not** constitute financial advice. Use at your own risk.

---

**Built with ❤️ for crypto enthusiasts**

*Last Updated: November 10, 2025*

