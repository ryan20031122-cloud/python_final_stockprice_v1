import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

from config.settings import get_database_url, TICKERS, DEFAULT_PERIOD
from utils.live_data import fetch_stock_prices

st.set_page_config(page_title="Stock Comparison", layout="wide")
st.title("Stock Comparison｜科技股報酬率與波動率比較")


@st.cache_data(ttl=3600)
def load_data() -> tuple[pd.DataFrame, str]:
    database_url = get_database_url()
    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            df = pd.read_sql("SELECT * FROM stock_prices ORDER BY date ASC", engine)
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                return df, "cloud_database"
        except Exception:
            pass
    return fetch_stock_prices(TICKERS, DEFAULT_PERIOD), "yahoo_finance_live"


df, source = load_data()
if df.empty:
    st.error("目前無法取得股價資料。")
    st.stop()

source_text = "雲端 PostgreSQL / Supabase" if source == "cloud_database" else "Yahoo Finance 即時抓取"
st.success(f"目前資料來源：{source_text}")

df["date"] = pd.to_datetime(df["date"])
selected = st.multiselect("Select tickers", sorted(df["ticker"].unique()), default=sorted(df["ticker"].unique()))
filtered = df[df["ticker"].isin(selected)].copy()
filtered["cumulative_return"] = filtered.groupby("ticker")["daily_return"].transform(lambda s: (1 + s.fillna(0)).cumprod() - 1)

fig = px.line(filtered, x="date", y="cumulative_return", color="ticker", title="Cumulative Return Comparison")
st.plotly_chart(fig, use_container_width=True)

latest = filtered.sort_values("date").groupby("ticker").tail(1)
fig2 = px.bar(latest, x="ticker", y="volatility_7", title="Latest 7-Day Volatility")
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(latest[["ticker", "date", "close", "daily_return", "volatility_7", "volume"]], use_container_width=True)
