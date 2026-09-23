"""Debt payoff calculations - EMI formula, avalanche and snowball strategies."""
import math


def compute_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard EMI formula: P*r*(1+r)^n / ((1+r)^n - 1)"""
    if annual_rate == 0:
        return round(principal / tenure_months, 2)
    r = annual_rate / 12 / 100
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def months_to_payoff(outstanding: float, annual_rate: float, monthly_payment: float) -> int:
    """How many months to pay off a loan at a given monthly payment."""
    if annual_rate == 0:
        return math.ceil(outstanding / monthly_payment) if monthly_payment > 0 else None
    r = annual_rate / 12 / 100
    if monthly_payment <= outstanding * r:
        return None  # Payment too low, never paid off
    months = math.log(monthly_payment / (monthly_payment - outstanding * r)) / math.log(1 + r)
    return math.ceil(months)


def total_interest(outstanding: float, annual_rate: float, tenure_months: int) -> float:
    """Total interest paid over the tenure."""
    emi = compute_emi(outstanding, annual_rate, tenure_months)
    return round(emi * tenure_months - outstanding, 2)


def debt_avalanche_order(debts: list) -> list:
    """Highest interest rate first - minimizes total interest paid."""
    return sorted(debts, key=lambda d: d.interest_rate, reverse=True)


def debt_snowball_order(debts: list) -> list:
    """Lowest outstanding balance first - builds momentum."""
    return sorted(debts, key=lambda d: d.outstanding)


def early_payoff_savings(outstanding: float, annual_rate: float, tenure_months: int, extra_monthly: float) -> dict:
    """How much interest is saved and how many months are cut by paying extra monthly."""
    normal_emi   = compute_emi(outstanding, annual_rate, tenure_months)
    new_payment  = normal_emi + extra_monthly
    normal_total = round(normal_emi * tenure_months, 2)
    new_months   = months_to_payoff(outstanding, annual_rate, new_payment) or tenure_months
    new_total    = round(new_payment * new_months, 2)
    return {
        "months_saved": tenure_months - new_months,
        "interest_saved": round(normal_total - new_total, 2),
        "new_payoff_months": new_months,
    }
