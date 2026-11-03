from src.data_gen.generate import (
    build_grid,
    place_access_points,
    compute_signal,
)


def test_same_seed_same_data():
    g1 = build_grid(seed=42)
    g2 = build_grid(seed=42)
    assert g1.equals(g2)

    s1 = compute_signal(g1, place_access_points(g1), days=1)
    s2 = compute_signal(g2, place_access_points(g2), days=1)
    assert s1.equals(s2)


def test_signal_between_0_and_100():
    g = build_grid()
    s = compute_signal(g, place_access_points(g), days=1)
    assert s["signal_quality"].between(0, 100).all()


def test_no_readings_on_walls():
    g = build_grid()
    s = compute_signal(g, place_access_points(g), days=1)
    walls = g.loc[~g["walkable"], ["x", "y"]]
    merged = s.merge(walls, on=["x", "y"])
    assert merged.empty