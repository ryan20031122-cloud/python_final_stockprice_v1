import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

from config.settings import get_database_url
from utils.live_data import fetch_live_stock_data


st.set_page_config(page_title="Stock Overview", layout="wide")

st.title("Stock Overview")
st.write("科技股價格走勢與波動分析")


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
                open,
                high,
                low,
                close,
                volume,
                daily_return,
                ma_7,
                ma_30,
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
    st.error("目前無法取得股價資料，請稍後再試或檢查網路來源。")
    st.stop()

st.subheader("資料概況")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("資料來源", "Cloud DB" if mode == "cloud_database" else "Stooq CSV")

with col2:
    st.metric("股票數量", df["ticker"].nunique())

with col3:
    st.metric("資料筆數", len(df))

tickers = sorted(df["ticker"].unique())

selected_tickers = st.multiselect(
    "選擇股票代碼",
    tickers,
    default=tickers
)

filtered_df = df[df["ticker"].isin(selected_tickers)]

st.subheader("科技股收盤價走勢")

fig = px.line(
    filtered_df,
    x="date",
    y="close",
    color="ticker",
    title="Major Technology Stock Price Trend"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("收盤價與移動平均")

selected_single_ticker = st.selectbox(
    "選擇一檔股票查看技術指標",
    tickers
)

indicator_df = df[df["ticker"] == selected_single_ticker].copy()

ma_df = indicator_df[["date", "close", "ma_7", "ma_30"]].melt(
    id_vars="date",
    var_name="indicator",
    value_name="value"
)

fig_ma = px.line(
    ma_df,
    x="date",
    y="value",
    color="indicator",
    title=f"{selected_single_ticker} 收盤價與移動平均"
)

st.plotly_chart(fig_ma, use_container_width=True)

st.subheader("7 日波動率")

fig_vol = px.line(
    indicator_df,
    x="date",
    y="volatility_7",
    title=f"{selected_single_ticker} 7 日波動率"
)

st.plotly_chart(fig_vol, use_container_width=True)

st.subheader("原始資料表")

st.dataframe(filtered_df, use_container_width=True)
