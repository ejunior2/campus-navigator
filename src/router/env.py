import numpy as np
import pandas as pd

from src.data_gen.generate import GRID_SIZE

ACTIONS = {0: (0, -1), 1: (0, 1), 2: (-1, 0), 3: (1, 0)}  # cima, baixo, esq, dir
ACTION_NAMES = {0: "up", 1: "down", 2: "left", 3: "right"}


class GridEnv:
    def __init__(self, grid: pd.DataFrame, signal: pd.DataFrame):
        self.size = GRID_SIZE
        self.walkable = np.zeros((self.size, self.size), dtype=bool)
        self.walkable[grid["y"].to_numpy(), grid["x"].to_numpy()] = grid["walkable"].to_numpy()

        # sinal médio por célula (média de todos os horários)
        mean = signal.groupby(["x", "y"])["signal_quality"].mean()
        self.signal = np.zeros((self.size, self.size))
        for (x, y), value in mean.items():
            self.signal[y, x] = value

    def is_walkable(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size and bool(self.walkable[y, x])

    def step(self, x: int, y: int, action: int) -> tuple[int, int]:
        dx, dy = ACTIONS[action]
        nx, ny = x + dx, y + dy
        if self.is_walkable(nx, ny):
            return nx, ny
        return x, y  # bateu na parede ou na borda: fica parado

    def neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        result = []
        for a in ACTIONS:
            nx, ny = self.step(x, y, a)
            if (nx, ny) != (x, y):
                result.append((nx, ny))
        return result

    def cell_signal(self, x: int, y: int) -> float:
        return float(self.signal[y, x])