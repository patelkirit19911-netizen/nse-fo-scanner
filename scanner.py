import yfinance as yf

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS"
]

print("Weekly High/Low Scanner")
print("-" * 30)

for stock in stocks:
    try:
        df = yf.download(stock, period="3mo", interval="1wk", progress=False)

        last_close = df["Close"].iloc[-1]
        prev_high = df["High"][:-1].max()
        prev_low = df["Low"][:-1].min()

        if last_close > prev_high:
            print(f"🚀 {stock} Weekly HIGH Breakout")

        elif last_close < prev_low:
            print(f"🔻 {stock} Weekly LOW Breakdown")

        else:
            print(f"➖ {stock} No Breakout")

    except Exception as e:
        print(stock, e)
