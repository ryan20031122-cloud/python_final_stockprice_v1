import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]
DEFAULT_PERIOD = "1y"
NEWS_QUERY = "technology stocks OR artificial intelligence OR semiconductor OR cloud computing"


def get_database_url() -> str | None:
    """Read DATABASE_URL from Streamlit Secrets first, then environment variables."""
    try:
        url = st.secrets.get("DATABASE_URL", None)
        if url is not None and str(url).strip() != "":
            return str(url).strip()
    except Exception:
        pass

    url = os.getenv("DATABASE_URL", "").strip()
    return url if url else None


def get_news_api_key() -> str:
    try:
        key = st.secrets.get("NEWS_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass
    return os.getenv("NEWS_API_KEY", "").strip()
