# top10_rebalancing/config.py
from datetime import datetime

# Backtest Configuration
START_YEAR_OFFSET = 10  # 10 years ago
TOP_N = 10
INITIAL_CAPITAL = 1000000  # Initial investment (Year 1 Jan) - KRW
MONTHLY_CONTRIBUTION = 1000000  # Monthly addition - KRW

# Fees & Taxes
TRANSACTION_FEE = 0.002  # 0.2% (Approx. including tax)

# Rebalancing Schedule (Yearly)
# Target: 2nd Monday of January
REBALANCING_MONTH = 1
REBALANCING_WEEK = 2
REBALANCING_WEEKDAY = 0  # 0=Monday, 6=Sunday

# Monthly Investment Schedule
# Target: 2nd Monday of every month
INVESTMENT_WEEK = 2
INVESTMENT_WEEKDAY = 0  # Monday
