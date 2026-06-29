import os
import io
import requests
import pandas as pd

from dhanhq import dhanhq
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice

# ===========================
# Secrets
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

dhan = dhanhq(CLIENT_ID)
# ===========================
# Telegram
# ===========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

# ===========================
# Load Instrument Master
# ===========================

CSV_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"

instrument_df = pd.read_csv(
    io.StringIO(
        requests.get(CSV_URL, timeout=30).text
    )
)

print("Instrument Loaded :", len(instrument_df))
# ===========================
# Scanner Settings
# ===========================

STOCKS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN"
]

INTERVAL = 5

FROM_DATE = "2026-06-20"
TO_DATE = "2026-06-29"

def get_security_id(symbol):
    data = instrument_df[
        (instrument_df["SEM_TRADING_SYMBOL"] == symbol) &
        (instrument_df["SEM_EXM_EXCH_ID"] == "NSE")
    ]

    if data.empty:
        return None

    return str(data.iloc[0]["SEM_SMST_SECURITY_ID"])


def get_historical_data(security_id):
    data = dhan.historical_minute_charts(
        security_id=security_id,
        exchange_segment="NSE_EQ",
        instrument_type="EQUITY",
        expiry_code=0,
        from_date=FROM_DATE,
        to_date=TO_DATE,
        interval=INTERVAL
    )

    if "data" not in data:
        return None

    df = pd.DataFrame(data["data"])

    if df.empty:
        return None

    return df
  # ===========================
# Indicator Calculation
# ===========================

def calculate_indicators(df):

    df["EMA20"] = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    df["EMA200"] = EMAIndicator(
        close=df["close"],
        window=200
    ).ema_indicator()

    df["RSI"] = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    adx = ADXIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=14
    )

    df["ADX"] = adx.adx()

    vwap = VolumeWeightedAveragePrice(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        volume=df["volume"]
    )

    df["VWAP"] = vwap.volume_weighted_average_price()

    return df


# ===========================
# Buy Signal
# ===========================

def is_buy_signal(last):

    return (
        last["EMA20"] > last["EMA200"]
        and last["close"] > last["VWAP"]
        and last["RSI"] > 60
        and last["ADX"] > 20
    )
  # ===========================
# Main Scanner
# ===========================

for symbol in STOCKS:

    try:

        security_id = get_security_id(symbol)

        if security_id is None:
            print(symbol, "Security ID Not Found")
            continue

        print("Scanning :", symbol)

        df = get_historical_data(security_id)

        if df is None:
            print(symbol, "No Data")
            continue

        df = calculate_indicators(df)

        last = df.iloc[-1]

        if is_buy_signal(last):

            msg = f"""
🚀 BUY SIGNAL

Stock : {symbol}

Price : {last['close']:.2f}

EMA20 : {last['EMA20']:.2f}
EMA200 : {last['EMA200']:.2f}

VWAP : {last['VWAP']:.2f}

RSI : {last['RSI']:.2f}

ADX : {last['ADX']:.2f}
"""

            print(msg)

            send_telegram(msg)

        else:
            print(symbol, "No Signal")

    except Exception as e:

        print(symbol, e)
