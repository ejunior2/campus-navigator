import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from src.kpis import queries
from src.kpis.db import get_connection
from src.router.env import GridEnv
from src.router.search import astar

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def get_worst_zone() -> dict:
    df = queries.avg_signal_by_zone()
    worst = df.iloc[-1]
    return {"zone": worst["zone"], "avg_signal": float(worst["avg_signal"])}


def get_best_zone() -> dict:
    df = queries.avg_signal_by_zone()
    best = df.iloc[0]
    return {"zone": best["zone"], "avg_signal": float(best["avg_signal"])}


def get_weak_signal_pct(threshold: int = 40) -> list[dict]:
    df = queries.weak_signal_pct_by_zone(threshold)
    return df.to_dict(orient="records")


def get_signal_by_hour(hour: int) -> dict:
    df = queries.avg_signal_by_hour()
    row = df[df["hour"] == hour]
    if row.empty:
        return {"error": f"hour {hour} not found (use 0-23)"}
    return {"hour": hour, "avg_signal": float(row.iloc[0]["avg_signal"])}


def get_weakest_hours(top_n: int = 3) -> list[dict]:
    """Retorna as horas do dia com o menor sinal médio."""
    df = queries.avg_signal_by_hour().sort_values("avg_signal").head(top_n)
    return df.to_dict(orient="records")


# ---------- Roteamento ----------


def _normalize(text: str) -> str:
    # remove acentos e ignora maiúsculas (Pátio == patio)
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


@lru_cache(maxsize=1)
def _get_env() -> GridEnv:
    grid = pd.read_csv(DATA_DIR / "grid_cells.csv")
    signal = pd.read_csv(DATA_DIR / "signal_readings.csv")
    return GridEnv(grid, signal)


@lru_cache(maxsize=1)
def _zone_cells() -> dict:
    """Células caminháveis de cada zona, lidas do banco."""
    env = _get_env()
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT x, y, zone FROM grid_cells WHERE zone IS NOT NULL", conn
        )
    finally:
        conn.close()
    cells = {}
    for zone, group in df.groupby("zone"):
        walkable = [(int(x), int(y)) for x, y in zip(group["x"], group["y"])
                    if env.is_walkable(int(x), int(y))]
        if walkable:
            cells[zone] = walkable
    return cells


def _find_zone(name: str):
    wanted = _normalize(name)
    for zone in _zone_cells():
        if _normalize(zone) == wanted:
            return zone
    return None


def _center_cell(zone: str) -> tuple[int, int]:
    """Célula caminhável da zona mais próxima do centro dela."""
    cells = _zone_cells()[zone]
    cx = float(np.mean([c[0] for c in cells]))
    cy = float(np.mean([c[1] for c in cells]))
    return min(cells, key=lambda c: (c[0] - cx) ** 2 + (c[1] - cy) ** 2)


def _route_metrics(path, threshold: int) -> dict:
    env = _get_env()
    sig = [env.cell_signal(x, y) for x, y in path]
    return {
        "steps": len(path),
        "mean_signal": round(float(np.mean(sig)), 1),
        "min_signal": round(float(np.min(sig)), 1),
        "weak_cells": int(sum(s < threshold for s in sig)),
        "path": [[x, y] for x, y in path],
    }


def get_route(origin_zone: str, destination_zone: str,
              optimize: str = "shortest",
              threshold: int = queries.WEAK_THRESHOLD) -> dict:
    """Calcula a rota entre duas zonas do campus com um algoritmo de busca.

    origin_zone e destination_zone: nomes das zonas (Biblioteca, Bloco A,
    Bloco B, Pátio). optimize: "shortest" para a rota com menos passos ou
    "best_signal" para a rota que também evita sinal fraco. O sinal usado é
    a média de todos os horários. Origem e destino são a célula caminhável
    mais central de cada zona. Retorna passos, sinal médio, sinal mínimo,
    quantidade de células com sinal abaixo de threshold e o caminho.
    """
    if optimize not in ("shortest", "best_signal"):
        return {"error": "optimize deve ser 'shortest' ou 'best_signal'"}
    origin = _find_zone(origin_zone)
    destination = _find_zone(destination_zone)
    if origin is None or destination is None:
        return {"error": "zona não encontrada",
                "valid_zones": sorted(_zone_cells())}
    if origin == destination:
        return {"error": "origem e destino são a mesma zona"}

    env = _get_env()
    start, goal = _center_cell(origin), _center_cell(destination)
    use_signal = optimize == "best_signal"
    path = astar(env, start, goal, use_signal=use_signal)
    if path is None:
        return {"error": "nenhuma rota encontrada entre as zonas"}
    return {
        "origin_zone": origin,
        "destination_zone": destination,
        "origin_cell": list(start),
        "destination_cell": list(goal),
        "optimize": optimize,
        "algorithm": "A* (sinal)" if use_signal else "A* (distância)",
        **_route_metrics(path, threshold),
    }


def compare_routes(origin_zone: str, destination_zone: str,
                   threshold: int = queries.WEAK_THRESHOLD) -> dict:
    """Compara a rota mais curta com a rota de melhor sinal entre duas zonas.

    Retorna as métricas das duas rotas e a diferença entre elas (passos a
    mais, ganho de sinal médio e de sinal mínimo, células fracas evitadas).
    """
    shortest = get_route(origin_zone, destination_zone, "shortest", threshold)
    if "error" in shortest:
        return shortest
    best = get_route(origin_zone, destination_zone, "best_signal", threshold)
    if "error" in best:
        return best
    return {
        "shortest": {k: v for k, v in shortest.items() if k != "path"},
        "best_signal": {k: v for k, v in best.items() if k != "path"},
        "difference": {
            "extra_steps": best["steps"] - shortest["steps"],
            "mean_signal_gain": round(best["mean_signal"] - shortest["mean_signal"], 1),
            "min_signal_gain": round(best["min_signal"] - shortest["min_signal"], 1),
            "weak_cells_avoided": shortest["weak_cells"] - best["weak_cells"],
        },
    }


if __name__ == "__main__":
    print(get_worst_zone())
    print(get_best_zone())
    print(get_weak_signal_pct())
    print(get_signal_by_hour(10))
    print(compare_routes("Biblioteca", "Bloco B"))
    print(get_route("Pátio", "Bloco A")["steps"])
    print(get_route("Cantina", "Bloco A"))