"""Train the forecast and save it for the dashboard: python run_forecast.py

Run run_ingestion.py first so the database exists.
"""
import logging

from src.forecast import run_forecast

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    metrics = run_forecast()
    print("\nPeak-season 2025 test results (lower is better):")
    print(metrics.to_string())


if __name__ == "__main__":
    main()
