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

def place_access_points(grid: pd.DataFrame, n_aps: int = 8,
                        min_dist: float = 5.0, seed: int = 42) -> pd.DataFrame:
    # Seed fixa: o mesmo sorteio sempre gera os mesmos roteadores
    rng = np.random.default_rng(seed)

    # Só células caminháveis podem receber um roteador
    walkable = grid.loc[grid["walkable"], ["x", "y"]].to_numpy()

    # Embaralha as células candidatas
    candidates = rng.permutation(walkable)

    chosen = []
    for cell in candidates:
        # Aceita a célula só se estiver longe o bastante dos roteadores já escolhidos
        if all(np.hypot(*(cell - c)) >= min_dist for c in chosen):
            chosen.append(cell)
        # Para quando atingir a quantidade desejada
        if len(chosen) == n_aps:
            break

    # Monta a tabela com um identificador para cada roteador
    aps = pd.DataFrame(chosen, columns=["x", "y"])
    aps.insert(0, "ap_id", range(len(aps)))

    # Alcance do sinal: 8 células
    aps["range"] = 8
    return aps

if __name__ == "__main__":
    g = build_grid()
    aps = place_access_points(g)
    print(aps)