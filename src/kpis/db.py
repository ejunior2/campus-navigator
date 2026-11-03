import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/campus.db")
TABLES = ["grid_cells", "access_points", "signal_readings"]


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def load_csvs_to_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        # Recria as tabelas a cada execução
        for table in TABLES:
            df = pd.read_csv(f"data/{table}.csv")
            df.to_sql(table, conn, if_exists="replace", index=False)

        # Índice acelera os JOINs por coordenada
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_signal_xy "
            "ON signal_readings (x, y)"
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    load_csvs_to_db()
    print("Banco criado em data/campus.db")