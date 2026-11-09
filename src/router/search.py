import heapq
from collections import deque

from src.router.env import GridEnv

SIGNAL_WEIGHT = 0.05  # custo extra por ponto de sinal abaixo de 100


def bfs(env: GridEnv, start: tuple[int, int], goal: tuple[int, int]):
    queue = deque([start])
    parent = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            return _path(parent, goal)
        for nxt in env.neighbors(*cur):
            if nxt not in parent:
                parent[nxt] = cur
                queue.append(nxt)
    return None


def _manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(env: GridEnv, start, goal, use_signal: bool = False):
    heap = [(0.0, 0, start)]
    parent = {start: None}
    cost = {start: 0.0}
    counter = 0
    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur == goal:
            return _path(parent, goal)
        for nxt in env.neighbors(*cur):
            step = 1.0
            if use_signal:
                step += SIGNAL_WEIGHT * (100 - env.cell_signal(*nxt))
            new_cost = cost[cur] + step
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                parent[nxt] = cur
                counter += 1
                priority = new_cost + _manhattan(nxt, goal)
                heapq.heappush(heap, (priority, counter, nxt))
    return None


def _path(parent, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]