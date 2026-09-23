from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from models import Budget, Transaction

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/budget")
@login_required
def budget_page():
    today = date.today()
    uid = current_user.id

    budget = Budget.query.filter_by(user_id=uid, month=today.month, year=today.year).first()

    # SQL aggregation — no N+1 query
    month_spent_row = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == uid,
        Transaction.transaction_type == "DEBIT",
        func.strftime("%m", Transaction.date) == f"{today.month:02d}",
        func.strftime("%Y", Transaction.date) == str(today.year),
    ).scalar()
    month_spent = float(month_spent_row or 0)

    amount = budget.amount if budget else 0
    remaining = amount - month_spent
    pct = (month_spent / amount * 100) if amount else 0

    if pct >= 100:
        status, message = "exceeded", "Budget exceeded — you have spent more than your monthly budget."
    elif pct >= 90:
        status, message = "critical", "Critical — you are close to reaching your monthly budget."
    elif pct >= 70:
        status, message = "warning", "Warning — you have used most of your monthly budget."
    else:
        status, message = "normal", "You are within your budget for this month."

    return render_template(
        "budget.html",
        budget_amount=amount,
        month_spent=round(month_spent, 2),
        remaining=round(remaining, 2),
        pct=min(round(pct, 1), 100),
        status=status,
        message=message,
    )


@budget_bp.route("/budget/save", methods=["POST"])
@login_required
def save_budget():
    today = date.today()
    try:
        amount = float(request.form.get("amount", 0))
        if amount < 0:
            raise ValueError
    except ValueError:
        flash("Please enter a valid budget amount.", "danger")
        return redirect(url_for("budget.budget_page"))

    budget = Budget.query.filter_by(user_id=current_user.id, month=today.month, year=today.year).first()
    if budget:
        budget.amount = amount
    else:
        budget = Budget(user_id=current_user.id, month=today.month, year=today.year, amount=amount)
        db.session.add(budget)

    db.session.commit()
    flash("Monthly budget saved.", "success")
    return redirect(url_for("budget.budget_page"))


