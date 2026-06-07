import pandas as pd
from utils.sentiment import score_sentiment


def transform_stock_prices(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw

    df = raw.copy()
    rename_map = {
        "adj_close": "adj_close",
        "close": "close",
        "date": "date",
        "open": "open",
        "high": "high",
        "low": "low",
        "volume": "volume",
        "ticker": "ticker",
    }
    df = df.rename(columns=rename_map)

    keep_cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
    df = df[[col for col in keep_cols if col in df.columns]]
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.sort_values(["ticker", "date"])

    df["daily_return"] = df.groupby("ticker")["close"].pct_change()
    df["ma_7"] = df.groupby("ticker")["close"].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df["ma_30"] = df.groupby("ticker")["close"].transform(lambda s: s.rolling(30, min_periods=1).mean())
    df["volatility_7"] = df.groupby("ticker")["daily_return"].transform(lambda s: s.rolling(7, min_periods=2).std())

    return df.dropna(subset=["ticker", "date", "close"])


def transform_news(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw

    df = raw.copy()
    df = df.dropna(subset=["title"])
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    scored = df["title"].apply(score_sentiment)
    df["sentiment"] = scored.apply(lambda x: x[0])
    df["sentiment_score"] = scored.apply(lambda x: x[1])

    return df[["title", "source", "published_at", "sentiment", "sentiment_score"]]
