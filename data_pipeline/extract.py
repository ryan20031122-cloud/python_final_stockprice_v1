from datetime import datetime, timedelta, timezone
import os
import requests
import yfinance as yf
import pandas as pd
from config.settings import TICKERS, DEFAULT_PERIOD, NEWS_QUERY


def extract_stock_prices(tickers: list[str] | None = None, period: str = DEFAULT_PERIOD) -> pd.DataFrame:
    tickers = tickers or TICKERS
    frames = []

    for ticker in tickers:
        data = yf.download(ticker, period=period, auto_adjust=False, progress=False)
        if data.empty:
            continue
        data = data.reset_index()
        data["ticker"] = ticker
        data.columns = [str(col).lower().replace(" ", "_") for col in data.columns]
        frames.append(data)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def extract_news() -> pd.DataFrame:
    """Extract recent news from NewsAPI if NEWS_API_KEY is available.

    If no key is provided, returns a small demo dataset so the app still works.
    """
    api_key = os.getenv("NEWS_API_KEY", "")
    if not api_key:
        return pd.DataFrame([
            {
                "title": "AI chip stocks rise as demand for data centers continues",
                "source": "Demo News",
                "published_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "title": "Technology shares mixed before inflation report",
                "source": "Demo News",
                "published_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "title": "Cloud software companies face pressure from slower enterprise spending",
                "source": "Demo News",
                "published_at": datetime.now(timezone.utc).isoformat(),
            },
        ])

    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": NEWS_QUERY,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 50,
        "apiKey": api_key,
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    articles = response.json().get("articles", [])

    rows = []
    for article in articles:
        rows.append({
            "title": article.get("title"),
            "source": (article.get("source") or {}).get("name"),
            "published_at": article.get("publishedAt"),
        })
    return pd.DataFrame(rows)
