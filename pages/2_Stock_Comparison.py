import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

from config.settings import get_database_url
from utils.live_data import fetch_live_stock_data


st.set_page_config(page_title="Stock Comparison", layout="wide")

st.title("Stock Comparison")
st.write("比較主要科技股的報酬率與波動率")


@st.cache_data(ttl=3600)
def load_data():
    database_url = get_database_url()

    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)

            query = """
            SELECT
                date,
                ticker,
                close,
                daily_return,
                volatility_7
            FROM stock_prices
            ORDER BY date ASC
            """

            df = pd.read_sql(query, engine)

            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                return df, "cloud_database"

        except Exception:
            pass

    df = fetch_live_stock_data()

    if not df.empty:
        return df, "stooq_live_data"

    return pd.DataFrame(), "no_data"


df, mode = load_data()

if mode == "cloud_database":
    st.success("目前使用雲端資料庫中的真實股價資料。")
elif mode == "stooq_live_data":
    st.success("目前使用 Stooq 公開 CSV 來源的真實股價資料。")
else:
    st.error("目前無法取得股價資料。")
    st.stop()

summary = (
    df.groupby("ticker")
    .agg(
        latest_close=("close", "last"),
        average_daily_return=("daily_return", "mean"),
        average_volatility=("volatility_7", "mean")
    )
    .reset_index()
)

st.subheader("各科技股平均每日報酬率")

fig_return = px.bar(
    summary,
    x="ticker",
    y="average_daily_return",
    title="Average Daily Return by Stock"
)

st.plotly_chart(fig_return, use_container_width=True)

st.subheader("各科技股平均 7 日波動率")

fig_vol = px.bar(
    summary,
    x="ticker",
    y="average_volatility",
    title="Average 7-Day Volatility by Stock"
)

st.plotly_chart(fig_vol, use_container_width=True)

st.subheader("比較資料表")

st.dataframe(summary, use_container_width=True)
