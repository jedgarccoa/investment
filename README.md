# Investment Trading Bot

This repository contains a simple intraday trading helper written in Python. The
script reads tickers from `all_tickers.json`, evaluates them with a logistic
regression model and emails the best opportunities.

## Configuration

Create a `config.json` file (already included as example) with:

```json
{
  "analysis_time": "09:00",
  "profit_threshold": 0.05,
  "tickers": ["AAPL", "MSFT", "NVDA"],
  "email": "jedgar.coa.@gmail.com"
}
```

Set the environment variables `EMAIL_USER` and `EMAIL_PASS` with your Gmail
credentials for sending notifications.

## Running

Install the dependencies:

```bash
pip install -r requirements.txt  # or manually install yfinance, ta, scikit-learn
```

Execute the bot manually:

```bash
python trading_bot.py
```

The script schedules an analysis at the configured time each day. Use cron to
run the script at startup for full automation.
