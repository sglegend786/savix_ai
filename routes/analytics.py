from calendar import month_name
from collections import defaultdict
from datetime import date

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from models import Transaction

analytics_bp = Blueprint("analytics", __name__)


def _monthly_credit_debit(txns):
    """Returns ordered month labels + credit/debit totals for months that have data
    in the current year (falls back to last 6 months layout)."""
    today = date.today()
    year = today.year
    totals = {m: {"credit": 0.0, "debit": 0.0} for m in range(1, 13)}

    for t in txns:
        if t.date.year == year:
            key = "credit" if t.transaction_type == "CREDIT" else "debit"
            totals[t.date.month][key] += t.amount

    months_with_data = [m for m in range(1, 13) if totals[m]["credit"] or totals[m]["debit"]]
    months_to_show = months_with_data if months_with_data else list(range(1, today.month + 1))

    labels = [month_name[m][:3] for m in months_to_show]
    credit_series = [round(totals[m]["credit"], 2) for m in months_to_show]
    debit_series = [round(totals[m]["debit"], 2) for m in months_to_show]
    return labels, credit_series, debit_series, months_to_show


@analytics_bp.route("/analytics")
@login_required
def analytics():
    txns = Transaction.query.filter_by(user_id=current_user.id).all()
    labels, credit_series, debit_series, months = _monthly_credit_debit(txns)

    category_totals = defaultdict(float)
    for t in txns:
        if t.transaction_type == "DEBIT":
            category_totals[t.category] += t.amount

    total_income = sum(t.amount for t in txns if t.transaction_type == "CREDIT")
    total_expense = sum(t.amount for t in txns if t.transaction_type == "DEBIT")
    net_savings = total_income - total_expense
    avg_txn = (sum(t.amount for t in txns) / len(txns)) if txns else 0
    top_category = max(category_totals, key=category_totals.get) if category_totals else "N/A"

    month_totals_debit = defaultdict(float)
    for t in txns:
        if t.transaction_type == "DEBIT":
            month_totals_debit[t.date.month] += t.amount
    top_month = month_name[max(month_totals_debit, key=month_totals_debit.get)] if month_totals_debit else "N/A"

    return render_template(
        "analytics.html",
        chart_labels=labels,
        credit_series=credit_series,
        debit_series=debit_series,
        category_labels=list(category_totals.keys()),
        category_values=[round(v, 2) for v in category_totals.values()],
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net_savings=round(net_savings, 2),
        avg_txn=round(avg_txn, 2),
        top_category=top_category,
        top_month=top_month,
        transaction_count=len(txns),
        months=[month_name[m] for m in range(1, 13)],
    )


@analytics_bp.route("/api/analytics/monthly")
@login_required
def api_monthly():
    txns = Transaction.query.filter_by(user_id=current_user.id).all()
    labels, credit_series, debit_series, _ = _monthly_credit_debit(txns)
    return jsonify({"labels": labels, "credit": credit_series, "debit": debit_series})


@analytics_bp.route("/api/analytics/category")
@login_required
def api_category():
    txns = Transaction.query.filter_by(user_id=current_user.id, transaction_type="DEBIT").all()
    totals = defaultdict(float)
    for t in txns:
        totals[t.category] += t.amount
    return jsonify({"labels": list(totals.keys()), "values": [round(v, 2) for v in totals.values()]})


@analytics_bp.route("/api/analytics/platform")
@login_required
def api_platform():
    txns = Transaction.query.filter_by(user_id=current_user.id, transaction_type="DEBIT").all()
    totals = defaultdict(float)
    counts = defaultdict(int)
    for t in txns:
        platform = t.app_platform or "Other"
        totals[platform] += t.amount
        counts[platform] += 1
    total_all = sum(totals.values()) or 1
    result = [
        {
            "platform": p,
            "amount": round(v, 2),
            "percentage": round(v / total_all * 100, 1),
            "count": counts[p],
        }
        for p, v in totals.items()
    ]
    result.sort(key=lambda x: x["amount"], reverse=True)
    return jsonify(result)


@analytics_bp.route("/api/dashboard/summary")
@login_required
def api_dashboard_summary():
    txns = Transaction.query.filter_by(user_id=current_user.id).all()
    total_credit = sum(t.amount for t in txns if t.transaction_type == "CREDIT")
    total_debit = sum(t.amount for t in txns if t.transaction_type == "DEBIT")
    return jsonify({
        "total_credit": round(total_credit, 2),
        "total_debit": round(total_debit, 2),
        "balance": round(total_credit - total_debit, 2),
        "total_transactions": len(txns),
    })
