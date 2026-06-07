import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

from config.settings import get_database_url, TICKERS, DEFAULT_PERIOD
from utils.live_data import fetch_stock_prices, fallback_news_sentiment

st.set_page_config(
    page_title="Tech Stock & Market Sentiment Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 科技股與新聞情緒分析 Dashboard")
st.caption("A cloud-hosted dashboard integrating stock prices, volatility indicators, and news sentiment.")


@st.cache_data(ttl=3600)
def load_stock_data() -> tuple[pd.DataFrame, str]:
    """Load cloud database data first; if unavailable, fetch real stock prices online."""
    database_url = get_database_url()

    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            query = """
                SELECT ticker, date, close, daily_return, ma_7, ma_30, volatility_7, volume, created_at
                FROM stock_prices
                ORDER BY date ASC;
            """
            db_df = pd.read_sql(query, engine)
            if not db_df.empty:
                db_df["date"] = pd.to_datetime(db_df["date"])
                return db_df, "cloud_database"
        except Exception:
            pass

    live_df = fetch_stock_prices(TICKERS, DEFAULT_PERIOD)
    if not live_df.empty:
        return live_df, "yahoo_finance_live"

    return pd.DataFrame(), "no_data"


@st.cache_data(ttl=3600)
def load_news_data() -> pd.DataFrame:
    database_url = get_database_url()
    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            query = """
                SELECT title, source, published_at, sentiment, sentiment_score, created_at
                FROM news_sentiment
                ORDER BY published_at DESC NULLS LAST
                LIMIT 100;
            """
            news_df = pd.read_sql(query, engine)
            if not news_df.empty:
                return news_df
        except Exception:
            pass
    return fallback_news_sentiment()


stocks, data_source = load_stock_data()
news = load_news_data()

if stocks.empty:
    st.error("目前無法取得股價資料。請確認網路、yfinance 套件或 DATABASE_URL 設定。")
    st.stop()

stocks["date"] = pd.to_datetime(stocks["date"])
latest_date = stocks["date"].max().date()
latest = stocks.sort_values("date").groupby("ticker").tail(1)

source_label = {
    "cloud_database": "Cloud PostgreSQL / Supabase",
    "yahoo_finance_live": "Yahoo Finance 即時抓取",
    "no_data": "No data",
}.get(data_source, data_source)

col1, col2, col3, col4 = st.columns(4)
col1.metric("資料來源", source_label)
col2.metric("追蹤股票數", latest["ticker"].nunique())
col3.metric("最新交易日", str(latest_date))
col4.metric("平均日報酬率", f"{latest['daily_return'].mean() * 100:.2f}%")

if data_source == "cloud_database":
    st.success("目前使用雲端資料庫中的真實股價資料。")
else:
    st.info("目前未讀到雲端資料庫資料，系統已自動改用 Yahoo Finance 真實股價資料，不再使用假資料。")

st.subheader("科技股收盤價走勢")
selected = st.multiselect(
    "選擇股票",
    options=sorted(stocks["ticker"].unique()),
    default=sorted(stocks["ticker"].unique())[:3],
)
filtered = stocks[stocks["ticker"].isin(selected)]
fig = px.line(filtered, x="date", y="close", color="ticker", title="Closing Price Over Time")
st.plotly_chart(fig, use_container_width=True)

st.subheader("最新績效快照")
snapshot_cols = ["ticker", "close", "daily_return", "ma_7", "ma_30", "volatility_7", "volume"]
snapshot = latest[[col for col in snapshot_cols if col in latest.columns]].copy()
if "daily_return" in snapshot:
    snapshot["daily_return"] = snapshot["daily_return"].map(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "N/A")
if "volatility_7" in snapshot:
    snapshot["volatility_7"] = snapshot["volatility_7"].map(lambda x: f"{x * 100:.2f}%" if pd.notnull(x) else "N/A")
st.dataframe(snapshot, use_container_width=True)

st.subheader("新聞情緒與國際事件對照")
if not news.empty:
    sentiment_counts = news["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    fig2 = px.bar(sentiment_counts, x="sentiment", y="count", title="News / Event Sentiment Distribution")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(news[["published_at", "source", "sentiment", "sentiment_score", "title"]].head(10), use_container_width=True)
else:
    st.info("目前沒有新聞情緒資料。")
