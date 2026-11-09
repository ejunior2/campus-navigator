import numpy as np
import pandas as pd
import pytest

from src.data_gen.generate import GRID_SIZE, build_grid, compute_signal, place_access_points
from src.router.env import GridEnv
from src.router.search import astar, bfs


@pytest.fixture(scope="module")
def env():
    g = build_grid()
    aps = place_access_points(g)
    s = compute_signal(g, aps, days=1)
    return GridEnv(g, s)


START, GOAL = (1, 1), (18, 18)


def test_bfs_and_astar_same_length(env):
    assert len(bfs(env, START, GOAL)) == len(astar(env, START, GOAL))


def test_signal_aware_not_shorter_than_optimal(env):
    assert len(astar(env, START, GOAL, use_signal=True)) >= len(bfs(env, START, GOAL))


def test_path_endpoints_and_validity(env):
    path = astar(env, START, GOAL, use_signal=True)
    assert path[0] == START and path[-1] == GOAL
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        assert abs(x0 - x1) + abs(y0 - y1) == 1
        assert env.is_walkable(x1, y1)


def test_unreachable_returns_none(env):
    wall = tuple(np.argwhere(~env.walkable)[0][::-1])
    assert bfs(env, START, wall) is None