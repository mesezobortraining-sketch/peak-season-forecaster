"""Train the peak-season demand forecast and save the results to SQLite.

The model is trained on data up to TRAIN_END and tested on the 2025 peak
season, then compared with two simple baselines.
"""
import logging
import sqlite3

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

from src import config

log = logging.getLogger(__name__)

TRAIN_END = "2025-10-31"
TEST_START = "2025-11-01"
TEST_END = "2025-12-31"

FEATURES = [
    "day_of_week", "is_bank_holiday", "is_peak_event", "is_peak_season",
    "day_of_year", "rain_mm", "temp_c", "wind_kmh", "lag_7", "lag_14",
]


def load_model_data(conn) -> pd.DataFrame:
    """Join parcels, weather and calendar, then add baselines and lag features."""
    ops = (pd.read_sql("select date, parcels from ops_synthetic", conn, parse_dates=["date"])
             .sort_values("date").set_index("date"))
    weather = pd.read_sql("select * from weather", conn, parse_dates=["date"]).set_index("date")
    cal = pd.read_sql(
        "select date, is_bank_holiday, is_peak_event, is_peak_season, day_of_week from calendar",
        conn, parse_dates=["date"],
    ).set_index("date")

    data = ops.join(weather).join(cal)

    # Baselines
    data["ma7"] = data["parcels"].shift(1).rolling(7).mean()   # average of previous 7 days
    data["seasonal_naive"] = data["parcels"].shift(7)          # same weekday last week

    # Model features: what happened on the same weekday 1 and 2 weeks ago
    data["lag_7"] = data["parcels"].shift(7)
    data["lag_14"] = data["parcels"].shift(14)
    data["day_of_year"] = data.index.dayofyear
    return data.dropna()


def score(actual: pd.Series, predicted: pd.Series) -> dict:
    """Average miss in parcels (MAE) and as a percentage (MAPE). Lower is better."""
    error = (actual - predicted).abs()
    return {"MAE": round(error.mean()), "MAPE": round((error / actual).mean() * 100, 1)}


def run_forecast() -> pd.DataFrame:
    """Fit the model, save forecast and metrics tables, return the metrics."""
    with sqlite3.connect(config.DB_PATH) as conn:
        data = load_model_data(conn)
        train = data.loc[:TRAIN_END]
        test = data.loc[TEST_START:TEST_END].copy()
        log.info("Training on %d days, testing on %d days", len(train), len(test))

        model = GradientBoostingRegressor(random_state=config.RANDOM_SEED)
        model.fit(train[FEATURES], train["parcels"])
        test["gbm"] = model.predict(test[FEATURES])

        metrics = pd.DataFrame(
            {name: score(test["parcels"], test[name]) for name in ["ma7", "seasonal_naive", "gbm"]}
        ).T
        metrics.index.name = "model"

        forecast = (test[["parcels", "gbm"]]
                    .rename(columns={"parcels": "actual_parcels", "gbm": "forecast_parcels"})
                    .reset_index())
        forecast.to_sql("forecast_peak_2025", conn, if_exists="replace", index=False)
        metrics.reset_index().to_sql("forecast_metrics", conn, if_exists="replace", index=False)
    return metrics
