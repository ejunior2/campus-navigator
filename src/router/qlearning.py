import numpy as np

from src.router.env import ACTIONS, GridEnv

GOAL_REWARD = 100.0
STEP_COST = -1.0
WALL_COST = -5.0
SIGNAL_WEIGHT_RL = 0.05
SHAPING = 1.5


class QLearningAgent:
    def __init__(self, env: GridEnv, goal: tuple[int, int], seed: int = 0,
                 alpha: float = 0.1, gamma: float = 0.95,
                 eps_start: float = 1.0, eps_end: float = 0.05,
                 use_signal: bool = True):
        self.env = env
        self.goal = goal
        self.rng = np.random.default_rng(seed)
        self.alpha, self.gamma = alpha, gamma
        self.eps_start, self.eps_end = eps_start, eps_end
        self.use_signal = use_signal
        self.q = np.zeros((env.size, env.size, len(ACTIONS)))

    def _reward(self, x, y, nx, ny):
        if (nx, ny) == self.goal:
            return GOAL_REWARD
        moved = (nx, ny) != (x, y)
        r = STEP_COST if moved else WALL_COST
        if moved:
            d_old = abs(x - self.goal[0]) + abs(y - self.goal[1])
            d_new = abs(nx - self.goal[0]) + abs(ny - self.goal[1])
            r += SHAPING * (d_old - d_new)
        if self.use_signal:
            r -= SIGNAL_WEIGHT_RL * (100 - self.env.cell_signal(nx, ny))
        return r

    def train(self, start, episodes=6000, max_steps=300):
        history = []
        starts = start if isinstance(start, list) else [start]
        for ep in range(episodes):
            eps = max(self.eps_end,
                      self.eps_start - (self.eps_start - self.eps_end) * ep / (episodes * 0.8))
            x, y = starts[self.rng.integers(len(starts))]
            total, reached, steps = 0.0, False, 0
            for steps in range(1, max_steps + 1):
                if self.rng.random() < eps:
                    a = int(self.rng.integers(len(ACTIONS)))
                else:
                    a = int(np.argmax(self.q[y, x]))
                nx, ny = self.env.step(x, y, a)
                r = self._reward(x, y, nx, ny)
                best_next = 0.0 if (nx, ny) == self.goal else self.q[ny, nx].max()
                self.q[y, x, a] += self.alpha * (r + self.gamma * best_next - self.q[y, x, a])
                total += r
                x, y = nx, ny
                if (x, y) == self.goal:
                    reached = True
                    break
            history.append({"episode": ep, "reward": total, "steps": steps,
                            "success": reached, "epsilon": eps})
        return history

    def route(self, start, max_steps=300):
        x, y = start
        path = [(x, y)]
        for _ in range(max_steps):
            a = int(np.argmax(self.q[y, x]))
            nx, ny = self.env.step(x, y, a)
            if (nx, ny) == (x, y) or (nx, ny) in path:
                return None
            path.append((nx, ny))
            x, y = nx, ny
            if (x, y) == self.goal:
                return path
        return None