"""Generate SYNTHETIC delivery-station data.

This is invented data with realistic patterns (weekly rhythm, peak-season ramp,
weather effects). It contains no real company data. Say so in the README.
"""
import numpy as np
import pandas as pd

from src import config


def generate_ops(weather: pd.DataFrame, calendar: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(config.RANDOM_SEED)
    df = calendar.merge(weather, on="date", how="inner").sort_values("date").reset_index(drop=True)

    base = 20_000  # parcels on an ordinary day

    # Weekly pattern: busiest early in the week, quiet on Sunday
    weekly = np.array([1.15, 1.10, 1.00, 0.98, 1.05, 0.85, 0.55])
    volume = base * weekly[df["day_of_week"].to_numpy()]

    # Peak season ramps up through Nov and Dec, easing off over Christmas
    day_of_year = df["date"].dt.dayofyear.to_numpy()
    ramp = np.where(df["is_peak_season"] == 1, 1 + 0.5 * (day_of_year - 305) / 60, 1.0)
    volume = volume * np.clip(ramp, 1.0, 1.5)
    volume = volume * np.where(df["is_peak_event"] == 1, 1.6, 1.0)
    volume = volume * np.where(df["is_bank_holiday"] == 1, 0.4, 1.0)

    # Longer-term growth plus random noise
    years_elapsed = (df["date"] - df["date"].min()).dt.days.to_numpy() / 365
    volume = volume * (1 + 0.08 * years_elapsed) * rng.normal(1.0, 0.05, len(df))
    df["parcels"] = volume.round().astype(int)

    # Units per hour: rain and heavy peak volume slow the building down
    uph = rng.normal(95, 4, len(df)) - 0.6 * df["rain_mm"].clip(upper=20) - 4 * df["is_peak_event"]
    df["uph"] = uph.round(1)
    df["labour_hours"] = (df["parcels"] / df["uph"]).round(1)

    # Defects per million opportunities, a little worse in busy weeks
    dpmo = rng.normal(900, 120, len(df)) + 0.01 * (df["parcels"] - base)
    df["dpmo"] = dpmo.clip(lower=100).round(0)

    return df[["date", "parcels", "labour_hours", "uph", "dpmo"]]
