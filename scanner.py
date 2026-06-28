import os
import io
import requests
import pandas as pd
from dhanhq import dhanhq
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice

# ---------------------------
# Secrets
# ---------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)

# ---------------------------
# Telegram
# ---------------------------
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=20
    )

# ---------------------------
# Instrument CSV
# ---------------------------
CSV_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"

instrument_df = pd.read_csv(
    io.StringIO(
        requests.get(CSV_URL, timeout=30).text
    )
)

print("Instrument Loaded :", len(instrument_df))
# ---------------------------
# Scanner Settings
# ---------------------------

STOCKS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN"
]

INTERVAL = 5

FROM_DATE = "2026-06-20"
TO_DATE = "2026-06-28"


def get_security_id(symbol):
    data = instrument_df[
        (instrument_df["SEM_TRADING_SYMBOL"] == symbol) &
        (instrument_df["SEM_EXM_EXCH_ID"] == "NSE")
    ]

    if data.empty:
        return None

    return str(data.iloc[0]["SEM_SMST_SECURITY_ID"])


for symbol in STOCKS:

    security_id = get_security_id(symbol)

    if security_id is None:
        print(symbol, "Security ID Not Found")
        continue

    print(symbol, security_id)
