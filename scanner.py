import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS"
]

message = "📈 Weekly High/Low Scanner\n\n"

for stock in stocks:
    try:
        df = yf.download(stock, period="3mo", interval="1wk", progress=False)

        last_close = df["Close"].iloc[-1]
        prev_high = df["High"][:-1].max()
        prev_low = df["Low"][:-1].min()

        if last_close > prev_high:
            message += f"✅ {stock} Weekly HIGH Breakout\n"
        elif last_close < prev_low:
            message += f"🔻 {stock} Weekly LOW Breakdown\n"

    except Exception as e:
        print(e)

if message == "📈 Weekly High/Low Scanner\n\n":
    message += "No breakout found."

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": message
})
