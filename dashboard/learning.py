import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from dashboard.routes import PRESETS, load_env, train_with_history

PAIRS = {k: v for k, v in PRESETS.items() if v}


def _blocks(df, window):
    """Agrega o treino em blocos de `window` episódios."""
    block = df["episode"] // window
    g = df.groupby(block)
    out = pd.DataFrame({
        "x": (g["episode"].min() + g["episode"].max()) / 2,
        "success_rate": g["success"].mean() * 100,
        "steps": g["steps"].mean(),
    })
    ok = df[df["success"]]
    out["signal"] = ok.groupby(ok["episode"] // window)["mean_signal"].mean()
    return out


def learning_figure(hist, window):
    blocks = _blocks(hist, window)
    ma = hist["reward"].rolling(window, min_periods=1).mean()

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=(
            "Recompensa por episódio",
            "Taxa de sucesso por janela (%)",
            "Passos médios por episódio",
            "Sinal médio nos episódios que chegaram ao destino",
        ),
    )
    fig.add_trace(go.Scatter(
        x=hist["episode"], y=hist["reward"], mode="lines", name="Recompensa",
        line=dict(width=1, color="rgba(150,150,150,0.45)")), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=hist["episode"], y=ma, mode="lines", name=f"Média móvel ({window})",
        line=dict(width=3, color="#ff6d00")), row=1, col=1)
    for row, col_name, label, color in [
        (2, "success_rate", "Taxa de sucesso", "#2e7d32"),
        (3, "steps", "Passos médios", "#2962ff"),
        (4, "signal", "Sinal médio", "#aa00ff"),
    ]:
        fig.add_trace(go.Scatter(
            x=blocks["x"], y=blocks[col_name], mode="lines+markers",
            name=label, line=dict(width=3, color=color)), row=row, col=1)

    # fim da queda do epsilon (80% dos episódios): a exploração se encerra
    fig.add_vline(x=int(len(hist) * 0.8), line_dash="dot",
                  line_color="gray", row="all", col=1)
    fig.update_xaxes(title_text="Episódio", row=4, col=1)
    fig.update_layout(height=900, showlegend=True,
                      legend=dict(orientation="h", y=-0.08, x=0.5,
                                  xanchor="center"),
                      margin=dict(l=10, r=10, t=40, b=60))
    return fig, blocks


def render_learning_tab():
    env = load_env()

    col1, col2 = st.columns([2, 1])
    with col1:
        choice = st.selectbox("Origem e destino", list(PAIRS),
                              key="learn_pair")
    with col2:
        window = st.slider("Tamanho da janela (episódios)", 50, 500, 200, 50)
    start, goal = PAIRS[choice]

    with st.spinner("Treinando o Q-Learning (alguns segundos)..."):
        _, _, hist = train_with_history(env, start, goal)

    fig, blocks = learning_figure(hist, window)

    m1, m2, m3 = st.columns(3)
    m1.metric("Sucesso na 1ª janela", f"{blocks['success_rate'].iloc[0]:.0f}%")
    m2.metric("Sucesso na última janela",
              f"{blocks['success_rate'].iloc[-1]:.0f}%")
    m3.metric("Passos médios na última janela",
              f"{blocks['steps'].iloc[-1]:.0f}")

    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Treino com seed 0 e 6000 episódios. A linha pontilhada marca onde o "
        "epsilon chega ao mínimo e o agente para de explorar. Episódios que "
        "não chegam ao destino contam como 300 passos (limite). O sinal médio "
        "considera todas as células visitadas no episódio, inclusive as da "
        "exploração, e só entram episódios bem-sucedidos."
    )