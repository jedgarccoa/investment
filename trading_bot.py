import json
import os
import time
from datetime import datetime
import urllib.request

import schedule
import pandas as pd
import numpy as np
import yfinance as yf
from ta.momentum import RSIIndicator
from sklearn.linear_model import LogisticRegression
import smtplib
from email.mime.text import MIMEText


CONFIG_FILE = "config.json"
TICKERS_FILE = "all_tickers.json"
SP500_URL = "https://gist.githubusercontent.com/princefishthrower/30ab8a532b4b281ce5bfe386e1df7a29/raw"


def load_config(path: str = CONFIG_FILE) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def load_tickers(config: dict, path: str = TICKERS_FILE, url: str = SP500_URL):
    if config.get("tickers"):
        return config["tickers"]
    try:
        with urllib.request.urlopen(url) as f:
            data = json.load(f)
        return [c["symbol"] for c in data.get("companies", [])]
    except Exception as e:
        print(f"Failed to fetch S&P 500 list: {e}")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            return [item[2] for item in data.get("data", [])]
    return []


def fetch_features(ticker: str):
    df = yf.Ticker(ticker).history(period="60d", interval="1d")
    if df.empty or len(df) < 15:
        return None
    df["return"] = df["Close"].pct_change()
    df["rsi"] = RSIIndicator(df["Close"]).rsi()
    df["ma5"] = df["Close"].rolling(window=5).mean()
    df["ma10"] = df["Close"].rolling(window=10).mean()
    df.dropna(inplace=True)
    if len(df) < 2:
        return None
    features = df[["return", "rsi", "ma5", "ma10"]].values[:-1]
    target = (df["Close"].shift(-1) > df["Close"]).astype(int).values[:-1]
    model = LogisticRegression(max_iter=100)
    model.fit(features, target)
    latest = df.iloc[-1][["return", "rsi", "ma5", "ma10"]].values
    prob_up = model.predict_proba([latest])[0, 1]
    return {"ticker": ticker, "prob_up": prob_up, "last_close": df["Close"].iloc[-1]}


def send_email(to_addr: str, subject: str, body: str):
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    if not user or not password:
        print("Email credentials not set")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.send_message(msg)


def analyze():
    config = load_config()
    tickers = load_tickers(config)
    results = []
    for tkr in tickers:
        try:
            res = fetch_features(tkr)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Error processing {tkr}: {e}")
    if not results:
        return
    results.sort(key=lambda x: x["prob_up"], reverse=True)
    best = results[:5]
    lines = [f"{r['ticker']}: {r['prob_up']:.2%} (close {r['last_close']:.2f})" for r in best]
    body = "\n".join(lines)
    send_email(config["email"], "Daily Opportunities", body)


def monitor_prices():
    config = load_config()
    tickers = load_tickers(config)
    threshold = config.get("profit_threshold", 0.05)
    purchase = {t: None for t in tickers}
    while True:
        for tkr in tickers:
            data = yf.download(tkr, period="1d", interval="1m", progress=False)
            if data.empty:
                continue
            current = data["Close"].iloc[-1]
            if purchase[tkr] is None:
                purchase[tkr] = current
            change = (current - purchase[tkr]) / purchase[tkr]
            if change >= threshold:
                send_email(
                    config["email"],
                    f"Sell signal {tkr}",
                    f"{tkr} has gained {change:.2%} since purchase",
                )
                purchase[tkr] = current
        time.sleep(300)


def main():
    config = load_config()
    schedule.every().day.at(config.get("analysis_time", "09:00")).do(analyze)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
