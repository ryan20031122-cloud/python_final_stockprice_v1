# Tech Stock & Market Sentiment Dashboard

A cloud-hosted dashboard that tracks major technology stock performance and recent technology news sentiment.

## Project Features

- Interactive Streamlit dashboard
- Stock price trend visualization
- Moving average and volatility indicators
- Cumulative return comparison
- News headline sentiment analysis
- PostgreSQL database storage
- Automated ETL refresh using GitHub Actions

## Tech Stack

- Front-end: Streamlit, Plotly
- Back-end: Python ETL Pipeline
- Database: PostgreSQL / Supabase PostgreSQL
- Automation: GitHub Actions
- Data Sources: Yahoo Finance through `yfinance`, NewsAPI or demo news fallback

## Repository Structure

```text
tech-stock-sentiment-dashboard/
├── app.py
├── requirements.txt
├── executive_summary.md
├── config/
├── data_pipeline/
├── database/
├── pages/
├── utils/
└── .github/workflows/
```

## Setup

### 1. Create a PostgreSQL database

You can use Supabase, Render PostgreSQL, Neon, or any hosted PostgreSQL database.

### 2. Add environment variables

Create a `.env` file locally:

```env
DATABASE_URL=postgresql://username:password@host:5432/database
NEWS_API_KEY=your_newsapi_key_optional
```

For GitHub Actions, add these as repository secrets:

- `DATABASE_URL`
- `NEWS_API_KEY` optional

For Streamlit Community Cloud, add `DATABASE_URL` to app secrets.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run ETL pipeline

```bash
python data_pipeline/run_pipeline.py
```

### 5. Run dashboard locally for testing

```bash
streamlit run app.py
```

## Deployment

Recommended deployment:

1. Push this repository to GitHub.
2. Create a PostgreSQL database on Supabase or another cloud provider.
3. Add `DATABASE_URL` to GitHub Secrets.
4. Manually run the GitHub Actions workflow once.
5. Deploy `app.py` on Streamlit Community Cloud.
6. Add the same `DATABASE_URL` to Streamlit Secrets.
7. Submit your public Streamlit URL for demo.

## Data Refresh Mechanism

The file `.github/workflows/daily_etl.yml` schedules the ETL pipeline to run daily at 01:00 UTC. It can also be triggered manually through GitHub Actions.
