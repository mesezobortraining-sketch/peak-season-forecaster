# Peak Season Delivery Demand & Capacity Forecaster

Forecasts daily parcel volumes and the labour hours needed to hit throughput
targets during peak season, using weather and UK calendar data.

> **Data note:** operations data is **synthetic**, generated in
> `src/generate_synthetic_ops.py`. Weather (Open-Meteo) and bank holidays
> (gov.uk) are real public data. No employer data is used.

## Pipeline (in progress)
1. Ingest and clean (done in this step)
2. Exploratory analysis
3. Forecast models vs a moving-average baseline
4. Capacity calculator (parcels -> labour hours -> headcount)
5. Dashboard
6. Optional AWS layer (S3, Lambda, Athena)

## Run it
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_ingestion.py
```
Output lands in `data/processed/forecaster.db` (tables: `weather`, `calendar`, `ops_synthetic`).

## Structure
```
run_ingestion.py
src/        config, ingest_weather, ingest_holidays, generate_synthetic_ops, load_db
data/       raw/ (API snapshots), processed/ (SQLite)
notebooks/  exploratory analysis
```
