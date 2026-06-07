import pandas as pd
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from utils.db import get_engine, run_schema


def upsert_dataframe(df: pd.DataFrame, table_name: str, conflict_cols: list[str]) -> None:
    if df.empty:
        print(f"No rows to load into {table_name}.")
        return

    engine = get_engine()
    rows = df.to_dict(orient="records")
    metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload_with=engine)

    with engine.begin() as conn:
        stmt = insert(table).values(rows)
        update_cols = {
            col.name: getattr(stmt.excluded, col.name)
            for col in table.columns
            if col.name not in ["id", "created_at"] + conflict_cols
        }
        stmt = stmt.on_conflict_do_update(index_elements=conflict_cols, set_=update_cols)
        conn.execute(stmt)


def load_stock_prices(df: pd.DataFrame) -> None:
    run_schema()
    upsert_dataframe(df, "stock_prices", ["ticker", "date"])


def load_news_sentiment(df: pd.DataFrame) -> None:
    run_schema()
    upsert_dataframe(df, "news_sentiment", ["title", "published_at"])
