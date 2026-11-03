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

def compute_signal(grid: pd.DataFrame, aps: pd.DataFrame,
                   days: int = 14, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Só células caminháveis têm leitura
    cells = grid.loc[grid["walkable"], ["x", "y"]].to_numpy()

    # Distância de cada célula até cada AP (matriz células x APs)
    diff = cells[:, None, :] - aps[["x", "y"]].to_numpy()[None, :, :]
    dist = np.sqrt((diff ** 2).sum(axis=2))

    # Usa o AP mais próximo de cada célula
    nearest = dist.argmin(axis=1)
    min_dist = dist.min(axis=1)
    ap_range = aps["range"].to_numpy()[nearest]

    # Qualidade base: 100 perto do AP, 0 no limite do alcance
    base = np.clip(100 * (1 - min_dist / ap_range), 0, 100)

    # Horários: de hora em hora, durante os dias pedidos
    timestamps = pd.date_range("2026-10-01", periods=days * 24, freq="h")
    hours = timestamps.hour.to_numpy()

    # Fator de congestionamento: pico de aula reduz 30%
    peak = ((hours >= 10) & (hours < 12)) | ((hours >= 19) & (hours < 21))
    factor = np.where(peak, 0.7, 1.0)

    # Combina tudo: matriz horários x células
    quality = base[None, :] * factor[:, None]
    quality += rng.normal(0, 3, size=quality.shape)
    quality = np.clip(quality, 0, 100).round(1)

    # Transforma a matriz em tabela longa
    return pd.DataFrame({
        "timestamp": np.repeat(timestamps, len(cells)),
        "x": np.tile(cells[:, 0], len(timestamps)),
        "y": np.tile(cells[:, 1], len(timestamps)),
        "signal_quality": quality.ravel(),
    })    

def main():
    g = build_grid()
    aps = place_access_points(g)
    signal = compute_signal(g, aps)

    g.to_csv("data/grid_cells.csv", index=False)
    aps.to_csv("data/access_points.csv", index=False)
    signal.to_csv("data/signal_readings.csv", index=False)
    print("Arquivos gerados em data/")


if __name__ == "__main__":
    main()