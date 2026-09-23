"""SAVIX Financial Brain - computes a normalized financial profile
for a user from their DB data. All values are deterministic Python.
No external AI calls happen here.
"""
from datetime import date
from calendar import month_name as MONTH_NAMES
from sqlalchemy import func, case

from extensions import db
from models import Transaction, Budget, Investment, FinancialGoal, Debt, Asset


def _month_sum(uid, txn_type, month, year):
    return float(db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == uid,
        Transaction.transaction_type == txn_type,
        func.strftime("%m", Transaction.date) == f"{month:02d}",
        func.strftime("%Y", Transaction.date) == str(year),
    ).scalar() or 0)


def get_financial_profile(user_id: int) -> dict:
    """Build a comprehensive financial profile for the given user."""
    today = date.today()
    uid = user_id

    agg = db.session.query(
        func.sum(case((Transaction.transaction_type == "CREDIT", Transaction.amount), else_=0)).label("total_credit"),
        func.sum(case((Transaction.transaction_type == "DEBIT",  Transaction.amount), else_=0)).label("total_debit"),
        func.count(Transaction.id).label("count"),
    ).filter(Transaction.user_id == uid).one()

    total_income   = float(agg.total_credit or 0)
    total_expenses = float(agg.total_debit or 0)
    balance        = total_income - total_expenses
    txn_count      = agg.count or 0

    this_month_income   = _month_sum(uid, "CREDIT", today.month, today.year)
    this_month_expenses = _month_sum(uid, "DEBIT",  today.month, today.year)
    this_month_savings  = this_month_income - this_month_expenses
    savings_rate = (this_month_savings / this_month_income * 100) if this_month_income > 0 else 0

    last_month      = 12 if today.month == 1 else today.month - 1
    last_month_year = today.year - 1 if today.month == 1 else today.year
    last_month_expenses = _month_sum(uid, "DEBIT", last_month, last_month_year)

    cat_rows = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == uid,
        Transaction.transaction_type == "DEBIT",
        func.strftime("%m", Transaction.date) == f"{today.month:02d}",
        func.strftime("%Y", Transaction.date) == str(today.year),
    ).group_by(Transaction.category).all()
    category_breakdown = {row.category: round(float(row.total), 2) for row in cat_rows}
    top_category = max(category_breakdown, key=category_breakdown.get) if category_breakdown else None

    budget_obj = Budget.query.filter_by(user_id=uid, month=today.month, year=today.year).first()
    monthly_budget     = float(budget_obj.amount) if budget_obj else 0
    budget_utilization = (this_month_expenses / monthly_budget * 100) if monthly_budget > 0 else 0

    investments      = Investment.query.filter_by(user_id=uid).all()
    total_invested   = sum(inv.amount for inv in investments)
    investment_count = len(investments)

    goals = FinancialGoal.query.filter_by(user_id=uid, is_active=True).all()
    goal_summary = [
        {"name": g.name, "target": g.target_amount, "current": g.current_amount,
         "progress_pct": g.progress_pct, "deadline": g.deadline.isoformat() if g.deadline else None}
        for g in goals
    ]

    debts = Debt.query.filter_by(user_id=uid, is_active=True).all()
    total_outstanding_debt = sum(d.outstanding for d in debts)
    total_monthly_emi      = sum((d.emi or 0) for d in debts)
    debt_to_income = (total_outstanding_debt / total_income * 100) if total_income > 0 else 0

    assets       = Asset.query.filter_by(user_id=uid).all()
    total_assets = sum(a.current_value for a in assets) + balance
    net_worth    = total_assets - total_outstanding_debt

    monthly_totals = []
    for i in range(1, 7):
        m_idx = today.month - i
        m = (m_idx - 1) % 12 + 1
        y = today.year if m_idx > 0 else today.year - 1
        monthly_totals.append(_month_sum(uid, "DEBIT", m, y))
    avg_monthly_expense   = sum(monthly_totals) / len(monthly_totals) if monthly_totals else 0
    emergency_fund_target = avg_monthly_expense * 6

    return {
        "user_id": uid, "computed_at": today.isoformat(), "current_month": MONTH_NAMES[today.month],
        "balance": round(balance, 2), "total_income_alltime": round(total_income, 2),
        "total_expenses_alltime": round(total_expenses, 2), "txn_count": txn_count,
        "this_month_income": round(this_month_income, 2), "this_month_expenses": round(this_month_expenses, 2),
        "this_month_savings": round(this_month_savings, 2), "savings_rate": round(savings_rate, 1),
        "last_month_expenses": round(last_month_expenses, 2), "category_breakdown": category_breakdown,
        "top_category": top_category, "monthly_budget": round(monthly_budget, 2),
        "budget_utilization": round(budget_utilization, 1), "total_invested": round(total_invested, 2),
        "investment_count": investment_count, "goals": goal_summary, "active_goal_count": len(goal_summary),
        "total_outstanding_debt": round(total_outstanding_debt, 2), "total_monthly_emi": round(total_monthly_emi, 2),
        "debt_to_income_ratio": round(debt_to_income, 1), "total_assets": round(total_assets, 2),
        "net_worth": round(net_worth, 2), "avg_monthly_expense": round(avg_monthly_expense, 2),
        "emergency_fund_target": round(emergency_fund_target, 2),
        "expense_trend": round(this_month_expenses - last_month_expenses, 2),
    }
