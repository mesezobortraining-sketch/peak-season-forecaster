"""Pull UK bank holidays and add retail peak-season dates."""
import logging

import pandas as pd
import requests

from src import config

log = logging.getLogger(__name__)


def _black_friday(year: int) -> pd.Timestamp:
    """Black Friday is the Friday after US Thanksgiving (4th Thursday of Nov)."""
    thursdays = pd.date_range(f"{year}-11-01", f"{year}-11-30", freq="W-THU")
    return thursdays[3] + pd.Timedelta(days=1)


def fetch_bank_holidays() -> pd.DataFrame:
    """Return date, name for England and Wales bank holidays."""
    resp = requests.get(config.BANK_HOLIDAYS_URL, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    events = resp.json()["england-and-wales"]["events"]
    df = pd.DataFrame(events)[["date", "title"]]
    df["date"] = pd.to_datetime(df["date"])
    return df.rename(columns={"title": "name"})


def build_calendar(start=config.START_DATE, end=config.END_DATE) -> pd.DataFrame:
    """One row per day with flags for bank holidays and retail peak events."""
    days = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    holidays = fetch_bank_holidays()

    peak_dates = {}
    for year in range(start.year, end.year + 1):
        bf = _black_friday(year)
        peak_dates[bf] = "Black Friday"
        peak_dates[bf + pd.Timedelta(days=3)] = "Cyber Monday"
    peak = pd.DataFrame({"date": list(peak_dates), "peak_event": list(peak_dates.values())})

    cal = days.merge(holidays, on="date", how="left").merge(peak, on="date", how="left")
    cal["is_bank_holiday"] = cal["name"].notna().astype(int)
    cal["is_peak_event"] = cal["peak_event"].notna().astype(int)
    cal["day_of_week"] = cal["date"].dt.dayofweek  # Monday = 0
    cal["is_peak_season"] = cal["date"].dt.month.isin([11, 12]).astype(int)
    return cal.rename(columns={"name": "holiday_name"})
