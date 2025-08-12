from ..extensions import db
from ..models.wage import WageRate
from ..models.settings import GlobalSettings

def get_effective_wage(user_id, work_date) -> float:
    # Most recent rate whose effective_date <= work_date
    rate = (WageRate.query
            .filter(WageRate.user_id == user_id, WageRate.effective_date <= work_date)
            .order_by(WageRate.effective_date.desc())
            .first())
    return float(rate.hourly_rate) if rate else 0.0

def get_current_burden_percent() -> float:
    s = GlobalSettings.query.first()
    return float(s.burden_percent if s else 0.0)

def assign_snapshot_cost(entry):
    """
    Mutates a TimeEntry to set snapshot cost fields based on hours, effective wage at work_date,
    and current global burden %. Does not commit.
    """
    rate = get_effective_wage(entry.user_id, entry.work_date)
    burden = get_current_burden_percent()
    labor = (entry.hours or 0.0) * rate
    total = labor * (1.0 + burden / 100.0)

    entry.hourly_rate_applied = rate
    entry.burden_percent_applied = burden
    entry.labor_cost = round(labor, 2)
    entry.total_cost = round(total, 2)
    return entry

def get_cost_for_entry(entry):
    """
    Returns a dict of cost values for reporting. Prefers stored snapshot; if missing (e.g. unsubmitted),
    computes using current effective wage + current burden.
    """
    if (entry.hourly_rate_applied is not None and
        entry.burden_percent_applied is not None and
        entry.labor_cost is not None and
        entry.total_cost is not None):
        return {
            "rate": float(entry.hourly_rate_applied),
            "burden_percent": float(entry.burden_percent_applied),
            "labor_cost": float(entry.labor_cost),
            "total_cost": float(entry.total_cost),
        }

    # Fallback compute (not persisted)
    rate = get_effective_wage(entry.user_id, entry.work_date)
    burden = get_current_burden_percent()
    labor = (entry.hours or 0.0) * rate
    total = labor * (1.0 + burden / 100.0)
    return {
        "rate": float(rate),
        "burden_percent": float(burden),
        "labor_cost": round(labor, 2),
        "total_cost": round(total, 2),
    }
