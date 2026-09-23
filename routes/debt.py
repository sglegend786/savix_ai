from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import Debt
from services.debt_service import (
    compute_emi, months_to_payoff, total_interest,
    debt_avalanche_order, debt_snowball_order, early_payoff_savings
)

debt_bp = Blueprint("debt", __name__)

LOAN_TYPES = ["Personal Loan", "Home Loan", "Car Loan", "Education Loan",
              "Credit Card", "Business Loan", "Gold Loan", "Other"]


@debt_bp.route("/debt")
@login_required
def debt_page():
    debts = Debt.query.filter_by(user_id=current_user.id).order_by(
        Debt.is_active.desc(), Debt.interest_rate.desc()
    ).all()
    debt_data = []
    for d in debts:
        mo = months_to_payoff(d.outstanding, d.interest_rate, d.emi) if d.emi else None
        ti = total_interest(d.outstanding, d.interest_rate, d.tenure_months) if d.tenure_months else None
        debt_data.append({"debt": d, "months_to_payoff": mo, "total_interest": ti})

    avalanche = debt_avalanche_order([d["debt"] for d in debt_data if d["debt"].is_active])
    snowball   = debt_snowball_order([d["debt"] for d in debt_data if d["debt"].is_active])
    total_emi  = sum((d.emi or 0) for d in debts if d.is_active)
    total_outstanding = sum(d.outstanding for d in debts if d.is_active)

    return render_template(
        "debt.html",
        debt_data=debt_data, avalanche=avalanche, snowball=snowball,
        total_emi=total_emi, total_outstanding=total_outstanding,
        loan_types=LOAN_TYPES, today=date.today(),
    )


@debt_bp.route("/debt/add", methods=["POST"])
@login_required
def add_debt():
    try:
        loan_name   = request.form.get("loan_name", "").strip()
        loan_type   = request.form.get("loan_type", "Personal Loan")
        principal   = float(request.form.get("principal", 0))
        outstanding = float(request.form.get("outstanding", principal))
        interest_rate = float(request.form.get("interest_rate", 0))
        tenure      = request.form.get("tenure_months", "")
        emi_val     = request.form.get("emi", "")
        due_day     = request.form.get("due_day", "")
        notes       = request.form.get("notes", "").strip()

        if not loan_name or principal <= 0:
            flash("Loan name and principal amount are required.", "danger")
            return redirect(url_for("debt.debt_page"))

        tenure_val = int(tenure) if tenure else None
        emi_computed = float(emi_val) if emi_val else (
            compute_emi(outstanding, interest_rate, tenure_val) if tenure_val else None
        )
        due_day_val = int(due_day) if due_day else None

        debt = Debt(
            user_id=current_user.id, loan_name=loan_name, loan_type=loan_type,
            principal=principal, outstanding=outstanding, interest_rate=interest_rate,
            emi=emi_computed, tenure_months=tenure_val, due_day=due_day_val, notes=notes,
        )
        db.session.add(debt)
        db.session.commit()
        flash(f'Debt "{loan_name}" added.', "success")
    except (ValueError, TypeError):
        flash("Invalid data - please check all fields.", "danger")
    return redirect(url_for("debt.debt_page"))


@debt_bp.route("/debt/<int:debt_id>/update", methods=["POST"])
@login_required
def update_debt(debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first_or_404()
    action = request.form.get("action")
    try:
        if action == "payment":
            amount = float(request.form.get("amount", 0))
            debt.outstanding = max(0, debt.outstanding - amount)
            if debt.outstanding == 0:
                debt.is_active = False
            db.session.commit()
            flash(f'Payment of {amount:.0f} recorded for "{debt.loan_name}".', "success")
        elif action == "toggle":
            debt.is_active = not debt.is_active
            db.session.commit()
            flash("Debt status updated.", "success")
    except (ValueError, TypeError):
        flash("Invalid amount.", "danger")
    return redirect(url_for("debt.debt_page"))


@debt_bp.route("/debt/<int:debt_id>/delete", methods=["POST"])
@login_required
def delete_debt(debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first_or_404()
    name = debt.loan_name
    db.session.delete(debt)
    db.session.commit()
    flash(f'Debt "{name}" removed.', "success")
    return redirect(url_for("debt.debt_page"))


@debt_bp.route("/api/debt/emi-calculator")
@login_required
def emi_calculator():
    try:
        principal = float(request.args.get("principal", 0))
        rate      = float(request.args.get("rate", 0))
        tenure    = int(request.args.get("tenure", 12))
        emi = compute_emi(principal, rate, tenure)
        ti  = total_interest(principal, rate, tenure)
        return jsonify({"emi": emi, "total_interest": ti, "total_payable": round(emi * tenure, 2)})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid parameters"}), 400
