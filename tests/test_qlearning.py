import pytest

from src.data_gen.generate import build_grid, compute_signal, place_access_points
from src.router.env import GridEnv
from src.router.qlearning import QLearningAgent

START, GOAL = (1, 1), (18, 18)


@pytest.fixture(scope="module")
def env():
    g = build_grid()
    aps = place_access_points(g)
    return GridEnv(g, compute_signal(g, aps, days=1))


def test_qlearning_reaches_goal(env):
    agent = QLearningAgent(env, GOAL, seed=0)
    history = agent.train(START)
    path = agent.route(START)
    assert path is not None
    assert path[0] == START and path[-1] == GOAL


def test_qlearning_is_reproducible(env):
    a = QLearningAgent(env, GOAL, seed=1)
    b = QLearningAgent(env, GOAL, seed=1)
    a.train(START, episodes=500)
    b.train(START, episodes=500)
    assert (a.q == b.q).all()