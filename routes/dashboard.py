from datetime import date
from calendar import month_name
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from models import Transaction, Budget

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    uid = current_user.id

    # SQL aggregation — no N+1 query
    agg = db.session.query(
        func.sum(Transaction.amount).filter(Transaction.transaction_type == "CREDIT").label("total_credit"),
        func.sum(Transaction.amount).filter(Transaction.transaction_type == "DEBIT").label("total_debit"),
        func.count(Transaction.id).label("total_count"),
    ).filter(Transaction.user_id == uid).one()

    total_credit = float(agg.total_credit or 0)
    total_debit = float(agg.total_debit or 0)
    balance = total_credit - total_debit
    total_transactions = agg.total_count or 0

    # Monthly spending via SQL
    month_spent_row = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == uid,
        Transaction.transaction_type == "DEBIT",
        func.strftime("%m", Transaction.date) == f"{today.month:02d}",
        func.strftime("%Y", Transaction.date) == str(today.year),
    ).scalar()
    month_spent = float(month_spent_row or 0)

    budget = Budget.query.filter_by(user_id=uid, month=today.month, year=today.year).first()
    monthly_budget = budget.amount if budget else 0
    remaining_budget = monthly_budget - month_spent

    # Recent 5 transactions only
    recent = (Transaction.query
              .filter_by(user_id=uid)
              .order_by(Transaction.date.desc(), Transaction.id.desc())
              .limit(5).all())

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
        total_transactions=total_transactions,
        recent_transactions=recent,
        budget_pct=min(budget_pct, 100),
        budget_status=budget_status,
        current_month_name=month_name[today.month],
    )

