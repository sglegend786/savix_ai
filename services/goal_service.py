"""Goal planning calculations - required monthly contribution, projected completion."""
from datetime import date
import math


def months_between(start: date, end: date) -> int:
    return max(1, (end.year - start.year) * 12 + (end.month - start.month))


def required_monthly_contribution(target: float, current: float, deadline: date) -> float:
    """How much to save per month to reach target by deadline."""
    remaining = max(0, target - current)
    months = months_between(date.today(), deadline)
    return round(remaining / months, 2) if months > 0 else remaining


def projected_completion_months(target: float, current: float, monthly: float) -> int:
    """How many months until goal is complete at current monthly contribution."""
    remaining = target - current
    if remaining <= 0:
        return 0
    if monthly <= 0:
        return None
    return math.ceil(remaining / monthly)


def goal_health(goal) -> str:
    """Returns 'on_track', 'at_risk', or 'behind'."""
    if goal.progress_pct >= 100:
        return "completed"
    if not goal.deadline or not goal.monthly_contribution:
        return "no_data"
    required = required_monthly_contribution(goal.target_amount, goal.current_amount, goal.deadline)
    if goal.monthly_contribution >= required:
        return "on_track"
    elif goal.monthly_contribution >= required * 0.7:
        return "at_risk"
    return "behind"
