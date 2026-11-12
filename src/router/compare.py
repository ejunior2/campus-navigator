import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.router.env import GridEnv
from src.router.qlearning import QLearningAgent
from src.router.search import astar, bfs

WEAK = 40
PAIRS = [((1, 1), (18, 18)), ((1, 18), (18, 1)), ((2, 9), (17, 10))]
SEEDS = [0, 1, 2, 3, 4]


def metrics(env, path):
    if path is None:
        return None
    sig = [env.cell_signal(x, y) for x, y in path]
    return {"length": len(path), "mean_signal": float(np.mean(sig)),
            "min_signal": float(np.min(sig)),
            "weak_cells": int(sum(s < WEAK for s in sig))}


def timed(fn):
    t = time.perf_counter()
    path = fn()
    return path, (time.perf_counter() - t) * 1000


def main():
    g = pd.read_csv("data/grid_cells.csv")
    s = pd.read_csv("data/signal_readings.csv")
    env = GridEnv(g, s)
    rows, curves = [], []
    for start, goal in PAIRS:
        if not (env.is_walkable(*start) and env.is_walkable(*goal)):
            print("par ignorado (parede):", start, goal)
            continue
        pair = f"{start}->{goal}"
        for name, fn in [
            ("BFS", lambda: bfs(env, start, goal)),
            ("A* distance", lambda: astar(env, start, goal)),
            ("A* signal", lambda: astar(env, start, goal, use_signal=True)),
        ]:
            path, ms = timed(fn)
            m = metrics(env, path)
            if m:
                rows.append({"pair": pair, "algorithm": name, "time_ms": ms,
                             "success": 1, **m})
        for seed in SEEDS:
            agent = QLearningAgent(env, goal, seed=seed)
            t = time.perf_counter()
            hist = agent.train(start)
            train_ms = (time.perf_counter() - t) * 1000
            path = agent.route(start)
            m = metrics(env, path)
            row = {"pair": pair, "algorithm": "Q-Learning", "seed": seed,
                   "time_ms": train_ms, "success": int(path is not None)}
            if m:
                row.update(m)
            rows.append(row)
            if seed == 0 and not curves:
                curves = [{"episode": h["episode"], "reward": h["reward"],
                           "success": int(h["success"]), "steps": h["steps"]}
                          for h in hist]
    df = pd.DataFrame(rows)
    Path("results").mkdir(exist_ok=True)
    df.to_csv("results/route_comparison.csv", index=False)
    Path("results/learning_curve.json").write_text(json.dumps(curves))
    summary = df.groupby(["pair", "algorithm"]).agg(
        success=("success", "mean"), length=("length", "mean"),
        mean_signal=("mean_signal", "mean"), min_signal=("min_signal", "mean"),
        weak_cells=("weak_cells", "mean"), time_ms=("time_ms", "mean")).round(2)
    print(summary.to_string())


if __name__ == "__main__":
    main()