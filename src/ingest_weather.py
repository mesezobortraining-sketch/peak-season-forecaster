"""Pull daily historical weather from the free Open-Meteo archive API."""
import logging

import pandas as pd
import requests

from src import config

log = logging.getLogger(__name__)

DAILY_FIELDS = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]


def fetch_weather(start=config.START_DATE, end=config.END_DATE) -> pd.DataFrame:
    """Return one row per day: date, temp_c, rain_mm, wind_kmh."""
    params = {
        "latitude": config.LATITUDE,
        "longitude": config.LONGITUDE,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": ",".join(DAILY_FIELDS),
        "timezone": config.TIMEZONE,
    }
    log.info("Requesting weather %s to %s", start, end)
    resp = requests.get(config.OPEN_METEO_URL, params=params, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()  # fail loudly on HTTP errors
    daily = resp.json()["daily"]

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]),
            "temp_c": daily["temperature_2m_mean"],
            "rain_mm": daily["precipitation_sum"],
            "wind_kmh": daily["wind_speed_10m_max"],
        }
    )
    # Fill small gaps rather than dropping days, then report what happened.
    missing = df[["temp_c", "rain_mm", "wind_kmh"]].isna().sum().sum()
    if missing:
        log.warning("Filling %d missing weather values", missing)
        df = df.sort_values("date").ffill()
    return df
