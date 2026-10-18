import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="India Air Quality Analytics", layout="wide")


@st.cache_data
def load(name):
    return pd.read_csv(f"results/{name}")


# approximate city coordinates for the map (no coordinates in the dataset)
COORDS = {
    "Ahmedabad": (23.02, 72.57), "Aizawl": (23.73, 92.72), "Amaravati": (16.57, 80.36),
    "Amritsar": (31.63, 74.87), "Bengaluru": (12.97, 77.59), "Bhopal": (23.26, 77.41),
    "Brajrajnagar": (21.82, 83.92), "Chandigarh": (30.73, 76.78), "Chennai": (13.08, 80.27),
    "Coimbatore": (11.02, 76.96), "Delhi": (28.61, 77.21), "Ernakulam": (9.98, 76.30),
    "Gurugram": (28.46, 77.03), "Guwahati": (26.14, 91.74), "Hyderabad": (17.38, 78.49),
    "Jaipur": (26.91, 75.79), "Jorapokhar": (23.70, 86.42), "Kochi": (9.93, 76.27),
    "Kolkata": (22.57, 88.36), "Lucknow": (26.85, 80.95), "Mumbai": (19.08, 72.88),
    "Patna": (25.59, 85.14), "Shillong": (25.58, 91.89), "Talcher": (20.95, 85.22),
    "Thiruvananthapuram": (8.52, 76.94), "Visakhapatnam": (17.69, 83.22),
}

# stations behind each city's COVID figure (from our analysis)
COVID_STATIONS = {
    "Patna": 1, "Ahmedabad": 1, "Brajrajnagar": 1, "Amaravati": 1, "Amritsar": 1,
    "Coimbatore": 1, "Thiruvananthapuram": 1, "Talcher": 1, "Jorapokhar": 1,
    "Guwahati": 1, "Visakhapatnam": 1, "Gurugram": 2, "Lucknow": 3, "Jaipur": 3,
    "Chennai": 4, "Kolkata": 4, "Hyderabad": 6, "Bengaluru": 8, "Mumbai": 10, "Delhi": 36,
}

page = st.sidebar.radio(
    "Page",
    ["Overview", "City explorer", "COVID lockdown", "Diwali", "Forecast", "Clusters"],
)

# ---------------------------------------------------------------- Overview
if page == "Overview":
    st.title("India Air Quality Analytics")
    st.write(
        "Spatio-temporal analysis of about 2.6 million hourly CPCB readings from "
        "Indian cities (2015 to mid-2020), processed with PySpark: hotspots, "
        "seasonal and hourly patterns, Diwali and lockdown effects, station "
        "clustering and next-day AQI forecasting."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Hourly readings", "2,589,083")
    c2.metric("Stations in dataset", "230")
    c3.metric("Stations clustered", "90")

    rank = load("city_ranking.csv").sort_values("avg_AQI", ascending=False)
    fig = px.bar(rank, x="City", y="avg_AQI", color="avg_AQI",
                 title="Average AQI by city",
                 labels={"avg_AQI": "Average AQI"})
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Cities with fewer than 10,000 AQI readings are left out. Ahmedabad is "
        "excluded because its carbon monoxide sensor was faulty, which inflated "
        "its AQI."
    )

# ----------------------------------------------------------- City explorer
elif page == "City explorer":
    st.title("City explorer")

    hourly = load("hourly_pm25.csv")
    cities = sorted(hourly["City"].unique())
    default = [c for c in ["Delhi", "Mumbai", "Bengaluru", "Chennai"] if c in cities]
    chosen = st.multiselect("Cities", cities, default=default)

    fig = px.line(hourly[hourly["City"].isin(chosen)], x="hour", y="pm25", color="City",
                  title="Average PM2.5 by hour of day",
                  labels={"hour": "Hour of day", "pm25": "Average PM2.5"})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Delhi has a morning peak and a late-evening to night peak, with a low point in the afternoon.")

    season = load("city_season_aqi.csv")
    season = season[season["City"].isin(chosen)]
    long = season.melt(id_vars="City", var_name="Season", value_name="Average AQI")
    fig2 = px.bar(long, x="Season", y="Average AQI", color="City", barmode="group",
                  category_orders={"Season": ["Winter", "Summer", "Monsoon", "Post-monsoon"]},
                  title="Average AQI by season")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Delhi and Lucknow are worst in winter and post-monsoon. Chennai stays almost flat across seasons.")

# ---------------------------------------------------------- COVID lockdown
elif page == "COVID lockdown":
    st.title("COVID-19 lockdown effect on PM2.5")
    st.write("Comparison of 25 March to 30 June in 2019 and 2020, using only stations that reported in both periods.")

    st.metric("Stations with lower PM2.5 in 2020", "81 of 87", "median change -34.7%", delta_color="off")

    covid = load("covid_by_city.csv")
    covid["stations"] = covid["City"].map(COVID_STATIONS)
    covid = covid.sort_values("change_pct")
    fig = px.bar(covid, x="City", y="change_pct", color="stations",
                 title="Change in average PM2.5, 2019 to 2020 (%)",
                 labels={"change_pct": "Change (%)", "stations": "Stations"})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(covid, use_container_width=True)
    st.caption(
        "Cities with 1 station reflect a single monitor, so do not read much into them. "
        "The results are consistent with reduced traffic and industry, but weather "
        "differences between the two years are not controlled for."
    )

# ------------------------------------------------------------------ Diwali
elif page == "Diwali":
    st.title("Diwali effect on PM2.5")
    st.write("Average PM2.5 in the 5 days before Diwali compared with Diwali day and the 2 days after.")

    allst = load("diwali_all_stations.csv").sort_values("year")
    allst["change_pct"] = ((allst["after"] - allst["before"]) / allst["before"] * 100).round(1)
    st.subheader("All stations")
    st.dataframe(allst, use_container_width=True)
    long = allst.melt(id_vars="year", value_vars=["before", "after"],
                      var_name="Phase", value_name="PM2.5")
    fig = px.bar(long, x="year", y="PM2.5", color="Phase", barmode="group",
                 title="PM2.5 before vs after Diwali, all stations")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("By city")
    dc = load("diwali_by_city.csv")
    city = st.selectbox("City", sorted(dc["City"].unique()),
                        index=sorted(dc["City"].unique()).index("Delhi") if "Delhi" in set(dc["City"]) else 0)
    sub = dc[dc["City"] == city].sort_values("year")
    st.dataframe(sub, use_container_width=True)
    long2 = sub.melt(id_vars="year", value_vars=["before", "after"],
                     var_name="Phase", value_name="PM2.5")
    fig2 = px.bar(long2, x="year", y="PM2.5", color="Phase", barmode="group",
                  title=f"{city}: PM2.5 before vs after Diwali")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "PM2.5 rose after Diwali in almost every case. 2015 to 2017 had few stations, "
        "so 2018 and 2019 are more reliable. Seasonal build-up in October and November "
        "also contributes, so this does not prove fireworks were the cause."
    )

# ---------------------------------------------------------------- Forecast
elif page == "Forecast":
    st.title("Next-day AQI forecast")

    st.subheader("Model comparison (test data)")
    results = pd.DataFrame({
        "Test year": ["2019", "2019", "2019", "2020", "2020", "2020"],
        "Model": ["Persistence", "Linear Regression", "Gradient-Boosted Trees"] * 2,
        "RMSE": [50.4, 44.9, 42.4, 37.9, 33.6, 32.7],
        "MAE": [31.0, 29.2, 27.2, 24.1, 23.4, 22.1],
        "R2": [0.817, 0.854, 0.870, 0.820, 0.859, 0.867],
    })
    st.dataframe(results, use_container_width=True, hide_index=True)
    st.caption("Trained on 2015 to 2018, tested on 2019 and 2020. Persistence means tomorrow's AQI is predicted to equal today's.")

    st.subheader("Error by season (MAE, test data)")
    seas = pd.DataFrame({
        "Season": ["Winter", "Post-monsoon", "Summer", "Monsoon"],
        "GBT MAE": [31.4, 30.5, 24.0, 18.8],
        "Persistence MAE": [38.8, 36.2, 25.3, 18.8],
    })
    st.dataframe(seas, use_container_width=True, hide_index=True)

    st.subheader("Actual vs forecast")
    fc = load("forecast_predictions.csv")
    fc["date"] = pd.to_datetime(fc["date"])
    stations = sorted(fc["StationId"].unique())
    default = stations.index("DL024") if "DL024" in stations else 0
    sid = st.selectbox("Station", stations, index=default)
    sub = fc[fc["StationId"] == sid].sort_values("date")
    fig = px.line(sub, x="date", y=["next_AQI", "prediction"],
                  labels={"value": "AQI", "variable": "Series"},
                  title=f"Next-day AQI, station {sid}")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The model follows the seasonal pattern but tends to underestimate the highest spikes.")

# ---------------------------------------------------------------- Clusters
elif page == "Clusters":
    st.title("Station clusters")
    st.write("Stations grouped with KMeans (k = 3) by their average PM2.5, NO2, SO2, O3 and CO.")

    cl = load("station_clusters.csv")
    feats = ["PM25", "NO2", "SO2", "O3", "CO"]

    prof = cl.groupby("cluster")[feats].mean().round(1)
    prof["stations"] = cl.groupby("cluster").size()
    order = prof["PM25"].sort_values().index.tolist()
    names = {order[0]: "Low pollution", order[1]: "Moderate", order[-1]: "High particulate"}
    prof.insert(0, "group", prof.index.map(names))
    st.dataframe(prof, use_container_width=True)

    cl["group"] = cl["cluster"].map(names)

    city = (cl.groupby("City")
              .agg(cluster=("cluster", lambda s: s.mode().iloc[0]),
                   PM25=("PM25", "mean"), stations=("StationId", "count"))
              .reset_index())
    city["group"] = city["cluster"].map(names)
    city["lat"] = city["City"].map(lambda c: COORDS.get(c, (None, None))[0])
    city["lon"] = city["City"].map(lambda c: COORDS.get(c, (None, None))[1])
    city = city.dropna(subset=["lat", "lon"])

    fig = px.scatter_geo(city, lat="lat", lon="lon", color="group", size="stations",
                         hover_name="City", hover_data={"PM25": ":.1f", "stations": True, "lat": False, "lon": False},
                         title="Most common cluster in each city")
    fig.update_geos(fitbounds="locations", showcountries=True, showland=True)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Each city is shown with its most common cluster. Some cities have stations "
        "in more than one cluster, so clusters reflect local conditions around "
        "a station, not only the city."
    )

    st.subheader("Cities in each group")
    split = cl.groupby(["group", "City"]).size().reset_index(name="stations")
    st.dataframe(split.sort_values(["group", "stations"], ascending=[True, False]),
                 use_container_width=True, hide_index=True)
