import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

from config.settings import get_database_url, TICKERS, DEFAULT_PERIOD
from utils.live_data import fetch_stock_prices

st.set_page_config(page_title="Stock Overview", layout="wide")
st.title("Stock Overview｜實際股價資料")
st.write("此頁優先讀取雲端 PostgreSQL / Supabase；若資料庫尚未建立或沒有資料，會自動抓取 Yahoo Finance 真實股價。")


@st.cache_data(ttl=3600)
def load_data() -> tuple[pd.DataFrame, str]:
    database_url = get_database_url()

    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            query = """
                SELECT ticker, date, open, high, low, close, volume,
                       daily_return, ma_7, ma_30, volatility_7, created_at
                FROM stock_prices
                ORDER BY date ASC;
            """
            db_df = pd.read_sql(query, engine)
            if not db_df.empty:
                db_df["date"] = pd.to_datetime(db_df["date"])
                return db_df, "cloud_database"
        except Exception as exc:
            st.warning(f"雲端資料庫讀取失敗，改用 Yahoo Finance 真實股價。錯誤類型：{type(exc).__name__}")

    live_df = fetch_stock_prices(TICKERS, DEFAULT_PERIOD)
    return live_df, "yahoo_finance_live"


df, source = load_data()

if df.empty:
    st.error("目前無法取得實際股價資料。請確認 requirements.txt 有 yfinance，並重新部署 Streamlit Cloud。")
    st.stop()

source_text = "雲端 PostgreSQL / Supabase" if source == "cloud_database" else "Yahoo Finance 即時抓取"
st.success(f"目前資料來源：{source_text}")

col1, col2, col3 = st.columns(3)
col1.metric("股票數量", df["ticker"].nunique())
col2.metric("資料筆數", len(df))
col3.metric("最新交易日", str(pd.to_datetime(df["date"]).max().date()))

tickers = sorted(df["ticker"].unique())
selected_tickers = st.multiselect("選擇股票代碼", tickers, default=tickers)
filtered_df = df[df["ticker"].isin(selected_tickers)]

st.subheader("收盤價走勢")
fig = px.line(filtered_df, x="date", y="close", color="ticker", title="Major Technology Stock Price Trend")
st.plotly_chart(fig, use_container_width=True)

st.subheader("移動平均與波動率")
selected_single_ticker = st.selectbox("選擇一檔股票查看技術指標", tickers)
indicator_df = df[df["ticker"] == selected_single_ticker].copy()

ma_cols = [col for col in ["close", "ma_7", "ma_30"] if col in indicator_df.columns]
ma_df = indicator_df[["date"] + ma_cols].melt(id_vars="date", var_name="indicator", value_name="value")
fig_ma = px.line(ma_df, x="date", y="value", color="indicator", title=f"{selected_single_ticker} 收盤價與移動平均")
st.plotly_chart(fig_ma, use_container_width=True)

if "volatility_7" in indicator_df.columns:
    fig_vol = px.line(indicator_df, x="date", y="volatility_7", title=f"{selected_single_ticker} 7 日波動率")
    st.plotly_chart(fig_vol, use_container_width=True)

st.subheader("資料表")
st.dataframe(filtered_df, use_container_width=True)
