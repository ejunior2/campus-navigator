import pytest

from src.data_gen.generate import (
    build_grid,
    place_access_points,
    compute_signal,
)
from src.kpis import db, queries


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    g = build_grid()
    aps = place_access_points(g)
    s = compute_signal(g, aps, days=1)

    data = tmp_path / "data"
    data.mkdir()
    g.to_csv(data / "grid_cells.csv", index=False)
    aps.to_csv(data / "access_points.csv", index=False)
    s.to_csv(data / "signal_readings.csv", index=False)

    monkeypatch.chdir(tmp_path)
    db_file = data / "test.db"
    db.load_csvs_to_db(db_file)
    monkeypatch.setattr(queries, "get_connection",
                        lambda: db.get_connection(db_file))


def test_zone_kpi_has_four_zones(temp_db):
    assert len(queries.avg_signal_by_zone()) == 4


def test_hour_kpi_has_24_rows(temp_db):
    assert len(queries.avg_signal_by_hour()) == 24


def test_weak_pct_between_0_and_100(temp_db):
    df = queries.weak_signal_pct_by_zone()
    assert df["weak_pct"].between(0, 100).all()