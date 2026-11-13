"""Run the full ingestion step: python run_ingestion.py"""
import logging

from src import config
from src.generate_synthetic_ops import generate_ops
from src.ingest_holidays import build_calendar
from src.ingest_weather import fetch_weather
from src.load_db import save_table

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    weather = fetch_weather()
    calendar = build_calendar()
    ops = generate_ops(weather, calendar)

    # Keep a raw copy of the real API data, then load everything to SQLite
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    weather.to_csv(config.RAW_DIR / "weather.csv", index=False)
    calendar.to_csv(config.RAW_DIR / "calendar.csv", index=False)

    save_table(weather, "weather")
    save_table(calendar, "calendar")
    save_table(ops, "ops_synthetic")


if __name__ == "__main__":
    main()
