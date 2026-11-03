import streamlit as st

from src.kpis import queries

st.set_page_config(page_title="Campus Navigator", layout="wide")

st.title("Campus Navigator")
st.caption(
    "Wi-Fi quality on a simulated campus. All data is synthetic."
)
st.info(
    "**Signal score**: a synthetic 0-100 score. 100 = next to the access "
    "point, 0 = out of range. It is not a real unit such as dBm or Mbps. "
    "A reading below 40 is considered weak."
)


@st.cache_data
def load_data():
    return (
        queries.avg_signal_by_zone(),
        queries.weak_signal_pct_by_zone(),
        queries.avg_signal_by_hour(),
    )


by_zone, weak_by_zone, by_hour = load_data()

by_zone = by_zone.rename(columns={"avg_signal": "Signal score (0-100)"})
weak_by_zone = weak_by_zone.rename(
    columns={"weak_pct": "Weak readings (% of time)"}
)
by_hour = by_hour.rename(columns={"avg_signal": "Signal score (0-100)"})

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average signal score by zone")
    st.bar_chart(by_zone, x="zone", y="Signal score (0-100)")

with col2:
    st.subheader("Time with weak signal (< 40) by zone")
    st.bar_chart(weak_by_zone, x="zone", y="Weak readings (% of time)")

st.subheader("Average signal score by hour of day")
st.line_chart(by_hour, x="hour", y="Signal score (0-100)")