"""Create images/08_headcount_plan.png from the saved forecast.

Run from the project folder:  python make_headcount_chart.py
Needs run_forecast.py to have been run first.
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw to a file, no window needed
import matplotlib.pyplot as plt
import pandas as pd

from src import config
from src.capacity import headcount_needed

BUFFER = 0.15
HOURS_PER_ASSOCIATE = 8
ABSENCE_RATE = 0.10

images = config.ROOT / "images"
images.mkdir(exist_ok=True)

with sqlite3.connect(config.DB_PATH) as conn:
    fc = pd.read_sql("select * from forecast_peak_2025", conn, parse_dates=["date"]).set_index("date")
    target_uph = round(pd.read_sql("select uph from ops_synthetic", conn)["uph"].median(), 1)

fc["planned"] = headcount_needed(fc["forecast_parcels"] * (1 + BUFFER), target_uph, HOURS_PER_ASSOCIATE, ABSENCE_RATE)
fc["needed"] = headcount_needed(fc["actual_parcels"], target_uph, HOURS_PER_ASSOCIATE, ABSENCE_RATE)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(fc.index, fc["needed"], label="Actually needed", linewidth=2)
ax.plot(fc.index, fc["planned"], label="Planned from forecast (15% buffer)", linewidth=2)
ax.set_title("Associates planned vs needed, peak season 2025")
ax.set_ylabel("Associates")
ax.legend()

out = images / "08_headcount_plan.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print("Saved:", out)
