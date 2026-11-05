from src.kpis import queries


def get_worst_zone() -> dict:
    df = queries.avg_signal_by_zone()
    worst = df.iloc[-1]
    return {"zone": worst["zone"], "avg_signal": float(worst["avg_signal"])}


def get_best_zone() -> dict:
    df = queries.avg_signal_by_zone()
    best = df.iloc[0]
    return {"zone": best["zone"], "avg_signal": float(best["avg_signal"])}


def get_weak_signal_pct(threshold: int = 40) -> list[dict]:
    df = queries.weak_signal_pct_by_zone(threshold)
    return df.to_dict(orient="records")


def get_signal_by_hour(hour: int) -> dict:
    df = queries.avg_signal_by_hour()
    row = df[df["hour"] == hour]
    if row.empty:
        return {"error": f"hour {hour} not found (use 0-23)"}
    return {"hour": hour, "avg_signal": float(row.iloc[0]["avg_signal"])}


if __name__ == "__main__":
    print(get_worst_zone())
    print(get_best_zone())
    print(get_weak_signal_pct())
    print(get_signal_by_hour(10))