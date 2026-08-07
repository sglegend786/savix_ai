from datetime import date
from calendar import month_name
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Transaction, Budget

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    txns = Transaction.query.filter_by(user_id=current_user.id).all()

    total_credit = sum(t.amount for t in txns if t.transaction_type == "CREDIT")
    total_debit = sum(t.amount for t in txns if t.transaction_type == "DEBIT")
    balance = total_credit - total_debit

    budget = Budget.query.filter_by(user_id=current_user.id, month=today.month, year=today.year).first()
    monthly_budget = budget.amount if budget else 0

    month_txns = [t for t in txns if t.date.month == today.month and t.date.year == today.year]
    month_spent = sum(t.amount for t in month_txns if t.transaction_type == "DEBIT")
    remaining_budget = monthly_budget - month_spent

    recent = sorted(txns, key=lambda t: (t.date, t.id), reverse=True)[:5]

    budget_pct = (month_spent / monthly_budget * 100) if monthly_budget else 0
    if budget_pct >= 100:
        budget_status = "exceeded"
    elif budget_pct >= 90:
        budget_status = "critical"
    elif budget_pct >= 70:
        budget_status = "warning"
    else:
        budget_status = "normal"

    return render_template(
        "dashboard.html",
        total_credit=total_credit,
        total_debit=total_debit,
        balance=balance,
        monthly_budget=monthly_budget,
        remaining_budget=remaining_budget,
        total_transactions=len(txns),
        recent_transactions=recent,
        budget_pct=min(budget_pct, 100),
        budget_status=budget_status,
        current_month_name=month_name[today.month],
    )
