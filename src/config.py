"""Central settings. Change these rather than hunting through the code."""
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "processed" / "forecaster.db"

# Location used for weather. Defaults to central London; swap in your
# delivery station's nearest town (look up its latitude/longitude).
LATITUDE = 51.5072
LONGITUDE = -0.1276
TIMEZONE = "Europe/London"

START_DATE = date(2023, 1, 1)
# The Open-Meteo archive lags by a few days, so stop slightly short of today.
END_DATE = date.today() - timedelta(days=5)

OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
BANK_HOLIDAYS_URL = "https://www.gov.uk/bank-holidays.json"
REQUEST_TIMEOUT = 30  # seconds

RANDOM_SEED = 42
