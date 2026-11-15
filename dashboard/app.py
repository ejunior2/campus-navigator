import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from dashboard.maps import heatmap_figure
from src.data_gen.generate import main as generate_data
from src.kpis import queries
from src.kpis.db import DB_PATH, load_csvs_to_db

# Rótulos exibidos na tela (os nomes nos dados continuam iguais)
ZONE_LABELS = {"Patio": "Pátio"}


def zone_label(zone):
    return ZONE_LABELS.get(zone, zone)


def ensure_database():
    if not DB_PATH.exists():
        Path("data").mkdir(exist_ok=True)
        generate_data()
        load_csvs_to_db()


ensure_database()

st.set_page_config(page_title="Campus Navigator", layout="wide")

st.title("Campus Navigator")
st.caption(
    "Qualidade do Wi-Fi em um campus simulado. Todos os dados são sintéticos."
)
st.info(
    "**Índice de sinal**: pontuação sintética de 0 a 100. 100 = ao lado do "
    "ponto de acesso, 0 = fora de alcance. Não é uma unidade real, como "
    "dBm ou Mbps."
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


st.sidebar.header("Filtros")
threshold = st.sidebar.slider(
    "Limite de sinal fraco", min_value=10, max_value=80, value=40, step=5
)

by_zone, weak_by_zone = load_zone_data(threshold)
by_hour = load_hour_data()

all_zones = by_zone["zone"].tolist()
selected = st.sidebar.multiselect(
    "Zonas", all_zones, default=all_zones, format_func=zone_label
)

by_zone = by_zone[by_zone["zone"].isin(selected)].copy()
weak_by_zone = weak_by_zone[weak_by_zone["zone"].isin(selected)].copy()

by_zone["zone"] = by_zone["zone"].map(zone_label)
weak_by_zone["zone"] = weak_by_zone["zone"].map(zone_label)

by_zone = by_zone.rename(columns={"avg_signal": "Índice de sinal (0-100)"})
weak_by_zone = weak_by_zone.rename(
    columns={"weak_pct": "Leituras fracas (% do tempo)"}
)
by_hour = by_hour.rename(columns={"avg_signal": "Índice de sinal (0-100)"})

tab_overview, tab_map = st.tabs(["Visão geral", "Mapa de conectividade"])

with tab_overview:
    if not selected:
        st.warning("Selecione pelo menos uma zona na barra lateral.")
    else:
        col1, col2 = st.columns(2)  
        with col1:
            st.subheader("Índice médio de sinal por zona")
            st.bar_chart(by_zone, x="zone", y="Índice de sinal (0-100)")
        with col2:
            st.subheader(f"Tempo com sinal fraco (< {threshold}) por zona")
            st.bar_chart(weak_by_zone, x="zone", y="Leituras fracas (% do tempo)")
        st.subheader("Índice médio de sinal por hora do dia")
        st.line_chart(by_hour, x="hour", y="Índice de sinal (0-100)")

with tab_map:
    st.subheader("Mapa do sinal Wi-Fi (grid 20x20)")
    hour = st.slider("Hora do dia", 0, 23, 10)
    st.plotly_chart(heatmap_figure(hour), width="stretch")
    st.caption(
        "Células vazias são paredes. Losangos são pontos de acesso. "
        "Dados sintéticos e modelo de sinal simplificado."
    )