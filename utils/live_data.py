import pandas as pd
import requests
from io import StringIO


TICKER_MAP = {
    "AAPL": "aapl.us",
    "MSFT": "msft.us",
    "NVDA": "nvda.us",
    "GOOGL": "googl.us",
    "TSLA": "tsla.us",
}


def fetch_stooq_stock(symbol: str) -> pd.DataFrame:
    """
    從 Stooq CSV 取得真實歷史股價資料。
    """
    stooq_symbol = TICKER_MAP.get(symbol, symbol.lower())

    url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    text = response.text.strip()

    if not text or "Date,Open,High,Low,Close,Volume" not in text:
        return pd.DataFrame()

    df = pd.read_csv(StringIO(text))

    if df.empty:
        return pd.DataFrame()

    df.columns = [col.lower() for col in df.columns]

    df["date"] = pd.to_datetime(df["date"])
    df["ticker"] = symbol

    df = df.sort_values("date")

    df["daily_return"] = df["close"].pct_change()
    df["ma_7"] = df["close"].rolling(window=7).mean()
    df["ma_30"] = df["close"].rolling(window=30).mean()
    df["volatility_7"] = df["daily_return"].rolling(window=7).std()

    return df[
        [
            "date",
            "ticker",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "daily_return",
            "ma_7",
            "ma_30",
            "volatility_7",
        ]
    ]


def fetch_live_stock_data(
    tickers=None,
    period_days: int = 365
) -> pd.DataFrame:
    """
    抓取多檔股票真實歷史資料。
    預設抓最近約一年資料。
    """
    if tickers is None:
        tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]

    frames = []

    for ticker in tickers:
        try:
            df = fetch_stooq_stock(ticker)

            if not df.empty:
                latest_date = df["date"].max()
                start_date = latest_date - pd.Timedelta(days=period_days)
                df = df[df["date"] >= start_date]
                frames.append(df)

        except Exception:
            continue

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result = result.sort_values(["ticker", "date"])

    return result
