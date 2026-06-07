from pathlib import Path
import sys

# Allow this script to be run from the repository root with:
# python data_pipeline/run_pipeline.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_pipeline.extract import extract_stock_prices, extract_news
from data_pipeline.transform import transform_stock_prices, transform_news
from data_pipeline.load import load_stock_prices, load_news_sentiment


def main() -> None:
    print("Starting ETL pipeline...")

    raw_stocks = extract_stock_prices()
    clean_stocks = transform_stock_prices(raw_stocks)
    load_stock_prices(clean_stocks)
    print(f"Loaded {len(clean_stocks)} stock rows.")

    raw_news = extract_news()
    clean_news = transform_news(raw_news)
    load_news_sentiment(clean_news)
    print(f"Loaded {len(clean_news)} news rows.")

    print("ETL pipeline completed.")


if __name__ == "__main__":
    main()
