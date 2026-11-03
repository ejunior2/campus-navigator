import streamlit as st

from src.kpis import queries

from pathlib import Path

from src.data_gen.generate import main as generate_data
from src.kpis.db import DB_PATH, load_csvs_to_db


def ensure_database():
    if not DB_PATH.exists():
        Path("data").mkdir(exist_ok=True)
        generate_data()
        load_csvs_to_db()


ensure_database()

st.set_page_config(page_title="Campus Navigator", layout="wide")

st.title("Campus Navigator")
st.caption(
    "Wi-Fi quality on a simulated campus. All data is synthetic."
)
st.info(
    "**Signal score**: a synthetic 0-100 score. 100 = next to the access "
    "point, 0 = out of range. It is not a real unit such as dBm or Mbps."
)


@st.cache_data
def load_zone_data(threshold):
    return (
        queries.avg_signal_by_zone(),
        queries.weak_signal_pct_by_zone(threshold),
    )


@st.cache_data
def load_hour_data():
    return queries.avg_signal_by_hour()


st.sidebar.header("Filters")
threshold = st.sidebar.slider(
    "Weak signal threshold", min_value=10, max_value=80, value=40, step=5
)

by_zone, weak_by_zone = load_zone_data(threshold)
by_hour = load_hour_data()

all_zones = by_zone["zone"].tolist()
selected = st.sidebar.multiselect("Zones", all_zones, default=all_zones)

by_zone = by_zone[by_zone["zone"].isin(selected)]
weak_by_zone = weak_by_zone[weak_by_zone["zone"].isin(selected)]

by_zone = by_zone.rename(columns={"avg_signal": "Signal score (0-100)"})
weak_by_zone = weak_by_zone.rename(
    columns={"weak_pct": "Weak readings (% of time)"}
)
by_hour = by_hour.rename(columns={"avg_signal": "Signal score (0-100)"})

if not selected:
    st.warning("Select at least one zone in the sidebar.")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Average signal score by zone")
        st.bar_chart(by_zone, x="zone", y="Signal score (0-100)")

    with col2:
        st.subheader(f"Time with weak signal (< {threshold}) by zone")
        st.bar_chart(weak_by_zone, x="zone", y="Weak readings (% of time)")

    st.subheader("Average signal score by hour of day")
    st.line_chart(by_hour, x="hour", y="Signal score (0-100)")