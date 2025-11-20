#!/usr/bin/env python3
"""Start the trading bot dashboard."""

import sys
import os

# Add dashboard directory to path
dashboard_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dashboard_dir)

from app import app

if __name__ == '__main__':
    print("=" * 80)
    print("Trading Bot Dashboard")
    print("=" * 80)
    print("Starting dashboard server...")
    print("Access the dashboard at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 80)
    app.run(host='0.0.0.0', port=5000, debug=True)

