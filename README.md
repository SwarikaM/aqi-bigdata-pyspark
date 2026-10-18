# Spatio-Temporal Analytics of Indian Air Quality using PySpark

Big Data Analytics mini project. An end-to-end PySpark pipeline on about **2.59 million hourly air quality readings** from **230 CPCB monitoring stations** across Indian cities (January 2015 to July 2020). It covers cleaning, hotspot and seasonal analysis, Diwali and COVID-19 lockdown effects, station clustering, next-day AQI forecasting and an interactive Streamlit dashboard.

**Category:** Spatio-Temporal Data Analytics


---

## Key findings

| Question | Result |
|---|---|
| Most polluted cities (average AQI) | Delhi (236.6), Lucknow (217.0), Patna (212.9), Gurugram (210.8) |
| When does pollution peak? | Post-monsoon and winter; mornings and late evenings in Delhi |
| COVID-19 lockdown (25 Mar to 30 Jun, 2020 vs 2019) | PM2.5 lower at **81 of 87** comparable stations, median change **-34.7%** |
| Diwali effect | PM2.5 rose after Diwali in every year studied (2018: +44%, 2019: +92%, all stations) |
| Station clustering (KMeans, k = 3) | High-particulate, moderate (higher ozone) and low-pollution groups |
| Next-day AQI forecast | Gradient-Boosted Trees: R2 0.870 (2019) and 0.867 (2020), better than the persistence baseline |

Two faulty sensors were found and excluded: Ahmedabad (station GJ001, carbon monoxide) and Delhi (station DL028, ozone). The results show associations, not proven causes, because weather data was not available.


## Pipeline

```
CSV  ->  PySpark (explicit schema)  ->  Parquet  ->  Cleaning and features
     ->  Spark SQL analytics  ->  Spark MLlib (KMeans, regression)
     ->  Result CSVs  ->  Streamlit dashboard
```

## Tech stack

Python, Apache PySpark (Spark SQL and MLlib), pandas, matplotlib, Plotly, Streamlit, Jupyter Notebook, Parquet. Developed on Windows with WSL2 (Ubuntu), Spark in local mode.

## Repository structure

```
.
├── aqi_bda.ipynb        # Full PySpark analysis (cleaning, analytics, clustering, forecasting)
├── app.py               # Streamlit dashboard
├── results/             # Result tables exported from Spark (used by the dashboard)
├── requirements.txt
└── README.md
```

## Dataset

The raw data is **not included** because the main file is too large for GitHub.

Download **"Air Quality Data in India (2015 - 2020)"** from Kaggle: https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india

Files used: `station_hour.csv` and `stations.csv`.

## How to run

### 1. Set up the environment

Requires Python 3 and Java 17 (for Spark).

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the dashboard only (no Spark needed)

The `results/` folder already contains the tables exported from Spark.

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser. Pages: Overview, City explorer, COVID lockdown, Diwali, Forecast, Clusters.

### 3. Re-run the full analysis (optional)

1. Download `station_hour.csv` and `stations.csv` from Kaggle and place them next to `aqi_bda.ipynb`.
2. Start Jupyter and run the notebook cells in order:

```bash
jupyter notebook
```

The notebook writes intermediate Parquet folders and regenerates the files in `results/`. Spark runs in local mode with 4 GB driver memory.

## Methodology in brief

1. **Ingestion:** CSV read with an explicit schema and written to Parquet.
2. **Cleaning:** null analysis (Xylene dropped at 80% missing), station join, time features (hour, month, season).
3. **Data quality:** faulty CO (Ahmedabad GJ001) and O3 (Delhi DL028) readings detected and nulled out.
4. **Analysis:** city ranking, hourly and seasonal patterns, Diwali and lockdown comparisons using only stations present in both periods.
5. **Clustering:** KMeans on station-level average PM2.5, NO2, SO2, O3 and CO; k chosen using silhouette scores and cluster sizes.
6. **Forecasting:** next-day AQI per station, trained on 2015 to 2018 and tested on 2019 and 2020 (time-based split), compared against a persistence baseline.

## Limitations

- Station coverage grew from 25 (2015) to 110 (2020), so comparisons use only stations present in both periods.
- Many cities have a single station, so their results describe one monitor.
- Event analyses cannot separate causes such as fireworks or lockdown from weather and seasonal effects.
- The forecast underestimates extreme spikes and adds little over persistence in the monsoon.
- Spark was run in local mode on one machine.

## Future work

Add weather variables, multi-day forecasts, a streaming layer for live readings and a multi-node Spark deployment.

## Acknowledgements

Data: Central Pollution Control Board (CPCB), India, via the Kaggle dataset linked above.
