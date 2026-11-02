import numpy as np
import pandas as pd

GRID_SIZE = 20


def build_grid(seed: int = 42) -> pd.DataFrame:
    """Cria o mapa do campus: uma grade GRID_SIZE x GRID_SIZE."""
    rng = np.random.default_rng(seed)

    # Todas as combinações (x, y) da grade
    xs, ys = np.meshgrid(np.arange(GRID_SIZE), np.arange(GRID_SIZE))
    grid = pd.DataFrame({"x": xs.ravel(), "y": ys.ravel()})

    # Começa tudo caminhável
    grid["walkable"] = True

    # Zonas: dividimos o mapa em 4 quadrantes nomeados
    half = GRID_SIZE // 2
    grid["zone"] = np.select(
        [
            (grid["x"] < half) & (grid["y"] < half),
            (grid["x"] >= half) & (grid["y"] < half),
            (grid["x"] < half) & (grid["y"] >= half),
        ],
        ["Bloco A", "Bloco B", "Biblioteca"],
        default="Patio",
    )

    # Prédios: sorteia ~15% das células como bloqueadas
    blocked = rng.random(len(grid)) < 0.15
    grid.loc[blocked, "walkable"] = False

    return grid


if __name__ == "__main__":
    g = build_grid()
    print(g.head())
    print(g["walkable"].value_counts())