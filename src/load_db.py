"""Write DataFrames to a local SQLite database."""
import logging
import sqlite3

import pandas as pd

from src import config

log = logging.getLogger(__name__)


def save_table(df: pd.DataFrame, table: str) -> None:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(config.DB_PATH) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)
    log.info("Saved %d rows to table '%s'", len(df), table)
