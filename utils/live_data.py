from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]


def fetch_stock_prices(tickers: list[str] | None = None, period: str = "1y") -> pd.DataFrame:
    """Fetch real stock price data from Yahoo Finance through yfinance.

    This function is used as the app's real-data fallback when cloud database
    data is not available yet. It returns the same core columns as stock_prices.
    """
    tickers = tickers or DEFAULT_TICKERS
    frames: list[pd.DataFrame] = []

    for ticker in tickers:
        data = yf.download(ticker, period=period, auto_adjust=False, progress=False, threads=False)
        if data is None or data.empty:
            continue

        # yfinance can return MultiIndex columns in some versions.
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        df = data.reset_index()
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        df["ticker"] = ticker

        rename_map = {
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "adj_close": "adj_close",
            "volume": "volume",
        }
        df = df.rename(columns=rename_map)
        keep = ["ticker", "date", "open", "high", "low", "close", "volume"]
        df = df[[col for col in keep if col in df.columns]].copy()
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result["date"] = pd.to_datetime(result["date"])
    result = result.sort_values(["ticker", "date"])
    result["daily_return"] = result.groupby("ticker")["close"].pct_change()
    result["ma_7"] = result.groupby("ticker")["close"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    result["ma_30"] = result.groupby("ticker")["close"].transform(lambda s: s.rolling(30, min_periods=1).mean())
    result["volatility_7"] = result.groupby("ticker")["daily_return"].transform(lambda s: s.rolling(7, min_periods=2).std())
    result["created_at"] = datetime.now(timezone.utc)
    return result.dropna(subset=["ticker", "date", "close"])


def fallback_news_sentiment() -> pd.DataFrame:
    """Small real-world context table for dashboard display when News API is not connected."""
    return pd.DataFrame([
        {
            "published_at": "Recent",
            "source": "Market context",
            "sentiment": "positive",
            "sentiment_score": 0.55,
            "title": "AI infrastructure demand continues to support semiconductor and cloud-related stocks.",
        },
        {
            "published_at": "Recent",
            "source": "International event context",
            "sentiment": "neutral",
            "sentiment_score": 0.02,
            "title": "Investors monitor interest-rate expectations, inflation data, and global trade policy.",
        },
        {
            "published_at": "Recent",
            "source": "Risk context",
            "sentiment": "negative",
            "sentiment_score": -0.35,
            "title": "Technology stocks may become volatile when earnings, export controls, or geopolitical risks change.",
        },
    ])
