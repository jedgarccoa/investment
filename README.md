# Investment Trading Bot

This repository contains a simple intraday trading helper written in Python.
The script loads the list of tickers to analyze and then evaluates them with a
logistic regression model, emailing the best opportunities. If no tickers are
provided in `config.json` the bot will automatically download the entire S&P 500
list from
<https://gist.github.com/princefishthrower/30ab8a532b4b281ce5bfe386e1df7a29>.

## Configuration

Create a `config.json` file (already included as example) with:

```json
{
  "analysis_time": "09:00",
  "profit_threshold": 0.05,
  "tickers": ["AAPL", "MSFT", "NVDA"],  # optional
  "email": "jedgar.coa.@gmail.com"
}
```

If `tickers` is omitted or left empty, the script will download the full list
of S&P 500 symbols from the aforementioned gist before running the analysis.

Copy `.env.example` to `.env` and fill in `EMAIL_USER` and `EMAIL_PASS` with the
account credentials used to send notifications:

```
EMAIL_USER=you@gmail.com
EMAIL_PASS=yourpassword
```

These variables will be loaded automatically when running the bot.

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
