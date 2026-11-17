import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.maps import heatmap_figure
from src.router.env import GridEnv
from src.router.qlearning import QLearningAgent
from src.router.search import astar, bfs

PRESETS = {
    "(1, 1) → (18, 18)": ((1, 1), (18, 18)),
    "(2, 16) → (18, 1)": ((2, 16), (18, 1)),
    "(0, 15) → (19, 0)": ((0, 15), (19, 0)),
    "Personalizado": None,
}

# nome -> (cor, espessura, traço)
STYLES = {
    "BFS": ("#2962ff", 9, "solid"),
    "A* (distância)": ("#000000", 5, "dash"),
    "A* (sinal)": ("#aa00ff", 4, "solid"),
    "Q-Learning": ("#00e5ff", 3, "dot"),
    }


@st.cache_resource
def load_env():
    grid = pd.read_csv("data/grid_cells.csv")
    signal = pd.read_csv("data/signal_readings.csv")
    return GridEnv(grid, signal)


@st.cache_data(show_spinner=False)
def train_qlearning(_env, start, goal):
    t = time.perf_counter()
    agent = QLearningAgent(_env, goal, seed=0)
    agent.train(start)
    ms = (time.perf_counter() - t) * 1000
    return agent.route(start), ms


def compute_routes(env, start, goal):
    """Retorna {algoritmo: (caminho ou None, tempo em ms)}."""
    results = {}
    for name, fn in [
        ("BFS", lambda: bfs(env, start, goal)),
        ("A* (distância)", lambda: astar(env, start, goal)),
        ("A* (sinal)", lambda: astar(env, start, goal, use_signal=True)),
    ]:
        t = time.perf_counter()
        path = fn()
        results[name] = (path, (time.perf_counter() - t) * 1000)
    with st.spinner("Treinando o Q-Learning (alguns segundos)..."):
        results["Q-Learning"] = train_qlearning(env, start, goal)
    return results


def route_table(env, results, weak):
    rows = []
    for name, (path, ms) in results.items():
        if path is None:
            rows.append({"Algoritmo": name, "Passos": "sem rota"})
            continue
        sig = [env.cell_signal(x, y) for x, y in path]
        rows.append({
            "Algoritmo": name,
            "Passos": len(path),
            "Sinal médio": round(float(np.mean(sig)), 1),
            "Sinal mínimo": round(float(np.min(sig)), 1),
            "Células fracas": int(sum(s < weak for s in sig)),
            "Tempo (ms)": round(ms, 2),
        })
    return pd.DataFrame(rows)


def build_figure(hour, results, start, goal):
    paths = {
        name: (path, STYLES[name][0])
        for name, (path, _) in results.items() if path
    }
    fig = heatmap_figure(hour, route_paths=paths)
    for name, (color, width, dash) in STYLES.items():
        fig.update_traces(
            mode="lines+markers",
            marker=dict(size=6, color="#00e5ff"),
            selector=dict(name="Q-Learning"),
        )
    fig.add_trace(go.Scatter(
        x=[start[0]], y=[start[1]], mode="markers+text", text=["Início"],
        textposition="bottom center", name="Início",
        marker=dict(symbol="circle", size=15, color="white",
                    line=dict(color="black", width=2))))
    fig.add_trace(go.Scatter(
        x=[goal[0]], y=[goal[1]], mode="markers+text", text=["Destino"],
        textposition="bottom center", name="Destino",
        marker=dict(symbol="star", size=18, color="white",
                    line=dict(color="black", width=2))))

    fig.update_xaxes(side="top", range=[-0.5, 19.5], constrain="domain")
    fig.update_yaxes(autorange=False, range=[19.5, -0.5])
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.05,
                    xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=50, b=60),
    )
    return fig


def render_routes_tab(threshold):
    env = load_env()

    col1, col2 = st.columns([2, 1])
    with col1:
        choice = st.selectbox("Origem e destino", list(PRESETS))
    with col2:
        hour = st.slider("Hora do mapa", 0, 23, 10, key="route_hour")

    if PRESETS[choice]:
        start, goal = PRESETS[choice]
    else:
        c1, c2, c3, c4 = st.columns(4)
        start = (c1.number_input("Origem x", 0, 19, 1),
                 c2.number_input("Origem y", 0, 19, 1))
        goal = (c3.number_input("Destino x", 0, 19, 18),
                c4.number_input("Destino y", 0, 19, 18))

    if not (env.is_walkable(*start) and env.is_walkable(*goal)):
        st.error("Origem ou destino cai em uma parede. Escolha outra célula.")
        return

    results = compute_routes(env, start, goal)
    st.plotly_chart(build_figure(hour, results, start, goal), width="stretch")

    st.subheader("Comparação das rotas")
    st.dataframe(route_table(env, results, threshold),
                 hide_index=True, width="stretch")
    st.caption(
        "Sinal médio e mínimo usam a média de todos os horários. "
        f"Célula fraca = sinal abaixo de {threshold} (filtro da barra lateral). "
        "BFS e A* (distância) minimizam passos; A* (sinal) também penaliza "
        "sinal ruim, então as funções de custo são diferentes e o custo total "
        "não é comparável. No Q-Learning, o tempo é o de treinamento (seed 0)."
    )