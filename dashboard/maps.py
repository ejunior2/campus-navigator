import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.kpis.db import get_connection

SIZE = 20


def _query(sql: str, params: dict | None = None) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()


def load_aps() -> pd.DataFrame:
    return _query("SELECT ap_id, x, y FROM access_points")


def load_signal_by_hour(hour: int) -> pd.DataFrame:
    sql = """
        SELECT x, y, AVG(signal_quality) AS signal
        FROM signal_readings
        WHERE CAST(strftime('%H', timestamp) AS INTEGER) = :h
        GROUP BY x, y
    """
    return _query(sql, {"h": hour})


def signal_matrix(signal: pd.DataFrame) -> np.ndarray:
    z = np.full((SIZE, SIZE), np.nan)  # NaN = parede (sem leitura)
    z[signal["y"].to_numpy(), signal["x"].to_numpy()] = signal["signal"].to_numpy()
    return z


def heatmap_figure(hour: int, route_paths: dict | None = None) -> go.Figure:
    z = signal_matrix(load_signal_by_hour(hour))
    aps = load_aps()

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=z, x=list(range(SIZE)), y=list(range(SIZE)),
        colorscale=[[0, "#d73027"], [0.4, "#fee08b"], [1, "#1a9850"]],
        zmin=0, zmax=100, xgap=1, ygap=1,
        colorbar=dict(title="Signal (0-100)"),
        hovertemplate="x=%{x}, y=%{y}<br>signal=%{z:.1f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=aps["x"], y=aps["y"], mode="markers+text",
        text=[f"AP{i}" for i in aps["ap_id"]], textposition="top center",
        marker=dict(symbol="diamond", size=12, color="white",
                    line=dict(color="black", width=1.5)),
        name="Access point",
    ))
    for name, (path, color) in (route_paths or {}).items():
        fig.add_trace(go.Scatter(
            x=[p[0] for p in path], y=[p[1] for p in path], mode="lines",
            line=dict(width=4, color=color), name=name,
        ))
    fig.update_yaxes(autorange="reversed", scaleanchor="x", title="y")
    fig.update_xaxes(title="x")
    fig.update_layout(height=620, margin=dict(l=10, r=10, t=30, b=10))
    return fig