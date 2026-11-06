from fastapi import FastAPI

from src.agent import tools
from src.kpis import queries

app = FastAPI(title="Campus Navigator API")

ALERT_THRESHOLD_PCT = 45.0


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/kpis/zones")
def zones():
    return queries.avg_signal_by_zone().to_dict(orient="records")


@app.get("/report")
def report(threshold: int = 40):
    weak = tools.get_weak_signal_pct(threshold)
    alerts = [z for z in weak if z["weak_pct"] > ALERT_THRESHOLD_PCT]
    return {
        "worst_zone": tools.get_worst_zone(),
        "best_zone": tools.get_best_zone(),
        "weakest_hours": tools.get_weakest_hours(),
        "weak_signal_by_zone": weak,
        "alert_limit_pct": ALERT_THRESHOLD_PCT,
        "alerts": alerts,
        "has_alert": len(alerts) > 0,
    }