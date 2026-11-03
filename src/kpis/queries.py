import pandas as pd

from src.kpis.db import get_connection

WEAK_THRESHOLD = 40


def avg_signal_by_zone() -> pd.DataFrame:
    sql = """
        SELECT g.zone,
               ROUND(AVG(s.signal_quality), 1) AS avg_signal
        FROM signal_readings s
        JOIN grid_cells g ON g.x = s.x AND g.y = s.y
        GROUP BY g.zone
        ORDER BY avg_signal DESC
    """
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def weak_signal_pct_by_zone(threshold: int = WEAK_THRESHOLD) -> pd.DataFrame:
    sql = """
        SELECT g.zone,
               ROUND(100.0 * SUM(s.signal_quality < :t) / COUNT(*), 1)
                   AS weak_pct
        FROM signal_readings s
        JOIN grid_cells g ON g.x = s.x AND g.y = s.y
        GROUP BY g.zone
        ORDER BY weak_pct DESC
    """
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn, params={"t": threshold})
    finally:
        conn.close()


def avg_signal_by_hour() -> pd.DataFrame:
    sql = """
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) AS hour,
               ROUND(AVG(signal_quality), 1) AS avg_signal
        FROM signal_readings
        GROUP BY hour
        ORDER BY hour
    """
    conn = get_connection()
    try:
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    print(avg_signal_by_zone())
    print(weak_signal_pct_by_zone())
    print(avg_signal_by_hour())