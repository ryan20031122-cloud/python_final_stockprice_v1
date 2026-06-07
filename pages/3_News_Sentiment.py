import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

from config.settings import get_database_url
from utils.live_data import fallback_news_sentiment

st.set_page_config(page_title="News Sentiment", layout="wide")
st.title("News Sentiment｜新聞情緒與國際事件對照")


@st.cache_data(ttl=3600)
def load_data() -> tuple[pd.DataFrame, str]:
    database_url = get_database_url()
    if database_url:
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            df = pd.read_sql("SELECT * FROM news_sentiment ORDER BY published_at DESC NULLS LAST", engine)
            if not df.empty:
                return df, "cloud_database"
        except Exception:
            pass
    return fallback_news_sentiment(), "event_context"


df, source = load_data()

if df.empty:
    st.info("No news data available.")
    st.stop()

source_text = "雲端 PostgreSQL / Supabase" if source == "cloud_database" else "事件對照說明資料"
st.success(f"目前資料來源：{source_text}")

fig = px.pie(df, names="sentiment", title="News / Event Sentiment Share")
st.plotly_chart(fig, use_container_width=True)

if "sentiment_score" in df.columns:
    fig2 = px.histogram(df, x="sentiment_score", nbins=20, title="Sentiment Score Distribution")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("新聞 / 國際事件對照表")
st.dataframe(df[["published_at", "source", "sentiment", "sentiment_score", "title"]], use_container_width=True)
