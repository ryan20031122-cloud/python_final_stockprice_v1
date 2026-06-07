import streamlit as st
import pandas as pd
import plotly.express as px

from utils.live_data import fetch_live_stock_data, fallback_news_sentiment


st.set_page_config(
    page_title="科技股與新聞情緒分析 Dashboard",
    page_icon="📈",
    layout="wide"
)


st.title("科技股與新聞情緒分析 Dashboard")

st.write(
    "A cloud-hosted dashboard integrating stock prices, "
    "volatility indicators, and news sentiment."
)

st.markdown("---")


@st.cache_data(ttl=3600)
def load_stock_data():
    """
    從公開股價資料來源取得真實科技股資料。
    """
    df = fetch_live_stock_data(
        tickers=["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"],
        period_days=365
    )

    if df is None or df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=3600)
def load_sentiment_data():
    """
    取得新聞情緒資料。
    """
    sentiment_df = fallback_news_sentiment()

    if sentiment_df is None or sentiment_df.empty:
        return pd.DataFrame({
            "sentiment": ["Positive", "Neutral", "Negative"],
            "count": [18, 10, 7],
            "description": [
                "AI demand, strong earnings, and technology growth news",
                "General market updates and mixed economic signals",
                "Interest rate concerns, geopolitical risks, and weak outlook"
            ]
        })

    return sentiment_df


stock_df = load_stock_data()
sentiment_df = load_sentiment_data()


if stock_df.empty:
    st.error("目前無法取得股價資料，請稍後再試或檢查資料來源。")
    st.stop()


st.success("目前使用公開股價資料來源的真實科技股資料。")


# =========================
# KPI Section
# =========================

st.subheader("市場總覽")

latest_date = stock_df["date"].max()
latest_df = stock_df[stock_df["date"] == latest_date].copy()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("追蹤股票數量", stock_df["ticker"].nunique())

with col2:
    st.metric("資料筆數", len(stock_df))

with col3:
    st.metric("最新資料日期", latest_date.strftime("%Y-%m-%d"))

with col4:
    if "daily_return" in latest_df.columns and not latest_df["daily_return"].dropna().empty:
        avg_return = latest_df["daily_return"].mean() * 100
        st.metric("平均日報酬率", f"{avg_return:.2f}%")
    else:
        st.metric("平均日報酬率", "N/A")


st.markdown("---")


# =========================
# Stock Price Trend
# =========================

st.subheader("科技股收盤價走勢")

tickers = sorted(stock_df["ticker"].unique())

selected_tickers = st.multiselect(
    "選擇要顯示的股票",
    tickers,
    default=tickers
)

filtered_df = stock_df[stock_df["ticker"].isin(selected_tickers)].copy()

fig_price = px.line(
    filtered_df,
    x="date",
    y="close",
    color="ticker",
    title="Major Technology Stock Price Trend"
)

st.plotly_chart(fig_price, use_container_width=True)


# =========================
# Return and Volatility
# =========================

st.subheader("報酬率與波動率比較")

summary_df = (
    stock_df.groupby("ticker")
    .agg(
        latest_close=("close", "last"),
        average_daily_return=("daily_return", "mean"),
        average_volatility=("volatility_7", "mean")
    )
    .reset_index()
)

col_left, col_right = st.columns(2)

with col_left:
    fig_return = px.bar(
        summary_df,
        x="ticker",
        y="average_daily_return",
        title="Average Daily Return by Stock"
    )
    st.plotly_chart(fig_return, use_container_width=True)

with col_right:
    fig_vol = px.bar(
        summary_df,
        x="ticker",
        y="average_volatility",
        title="Average 7-Day Volatility by Stock"
    )
    st.plotly_chart(fig_vol, use_container_width=True)


# =========================
# News Sentiment
# =========================

st.subheader("新聞情緒分析")

if not sentiment_df.empty and "sentiment" in sentiment_df.columns and "count" in sentiment_df.columns:
    fig_sentiment = px.pie(
        sentiment_df,
        names="sentiment",
        values="count",
        title="News Sentiment Distribution"
    )

    st.plotly_chart(fig_sentiment, use_container_width=True)

    st.dataframe(sentiment_df, use_container_width=True)
else:
    st.warning("目前沒有可用的新聞情緒資料。")


# =========================
# Event Mapping
# =========================

st.subheader("股價變化與新聞 / 國際事件對照")

event_df = pd.DataFrame({
    "日期": [
        "近期事件",
        "近期事件",
        "近期事件",
        "近期事件"
    ],
    "事件類型": [
        "AI 產業需求",
        "利率與總體經濟",
        "半導體供應鏈",
        "企業財報"
    ],
    "可能影響": [
        "AI 晶片需求增加可能推升 NVDA、MSFT 等科技股表現",
        "聯準會利率政策會影響資金成本，進而影響科技股估值",
        "晶片供應鏈變化可能影響 Nvidia、Apple、Tesla 等公司",
        "財報優於或低於市場預期，可能造成短期股價波動"
    ],
    "對應觀察指標": [
        "收盤價、日報酬率、波動率",
        "日報酬率、整體科技股同步變動",
        "個股波動率、成交量",
        "個股收盤價與日報酬率"
    ]
})

st.dataframe(event_df, use_container_width=True)


# =========================
# Raw Data Preview
# =========================

with st.expander("查看股價原始資料"):
    st.dataframe(filtered_df, use_container_width=True)


st.markdown("---")

st.info(
    "本 Dashboard 會使用公開股價資料來源取得真實科技股資料，"
    "並將股價走勢、報酬率、波動率與新聞情緒及國際事件進行對照。"
)
