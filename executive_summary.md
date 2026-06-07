# Executive Summary: Tech Stock & Market Sentiment Dashboard

## Project Overview

This project develops a cloud-hosted web dashboard that monitors major technology stock performance and related market sentiment. The dashboard integrates financial market data, technical indicators, and news sentiment into one interactive application. The goal is to help users quickly understand recent market movements, compare major technology companies, and observe whether public news sentiment aligns with stock performance.

## Data Pipeline and Backend Design

The backend is implemented as an automated ETL pipeline using Python. The extraction stage collects daily stock data for selected technology companies such as Apple, Microsoft, Nvidia, Google, and Tesla through Yahoo Finance. It also collects recent technology-related news headlines for sentiment analysis. The transformation stage cleans missing values, standardizes date formats, calculates daily returns, 7-day and 30-day moving averages, and 7-day volatility. News headlines are transformed into positive, neutral, or negative sentiment categories using sentiment scoring. The processed data is then loaded into a cloud PostgreSQL database.

## Front-End Dashboard

The front-end is built using Streamlit and Plotly. It includes interactive line charts, return comparison charts, volatility visualizations, sentiment distribution charts, and key performance indicator cards. Users can select companies, compare stock performance, and inspect recent news sentiment. The dashboard also displays the latest data refresh time to communicate the freshness of the data.

## Data Refresh Mechanism

The data pipeline is automatically refreshed using GitHub Actions. A scheduled workflow runs the ETL pipeline every day and updates the cloud database without requiring a local machine. This supports the project requirement that the web application must be deployed online and cannot depend on localhost during the in-class demonstration.

## Value and Insights

This application combines quantitative stock indicators and qualitative news sentiment. Instead of only showing raw prices, it converts market data into meaningful indicators such as returns, volatility, moving averages, and sentiment categories. This allows users to understand both market behavior and public information signals in a single dashboard.

## Deployment

The application is designed for deployment on Streamlit Community Cloud, with PostgreSQL hosted on a cloud database service such as Supabase, Render, or Neon. The final project can be demonstrated through a public URL and does not require a custom domain.
