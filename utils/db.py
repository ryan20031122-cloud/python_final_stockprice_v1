import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set. Add it to .env, Streamlit secrets, or GitHub Secrets.")
    return create_engine(database_url, pool_pre_ping=True)


def run_schema(schema_path: str = "database/schema.sql") -> None:
    engine = get_engine()
    with open(schema_path, "r", encoding="utf-8") as file:
        schema_sql = file.read()
    with engine.begin() as conn:
        conn.execute(text(schema_sql))


def read_sql(query: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(query, engine)
