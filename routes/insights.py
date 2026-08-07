"""Rule-based AI spending insights (combined with categories the ML model
already assigned to transactions). No guarantees are made about outcomes."""
from calendar import month_name
from collections import defaultdict
from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Transaction

insights_bp = Blueprint("insights", __name__)


def generate_insights(user_id):
    txns = Transaction.query.filter_by(user_id=user_id).all()
    today = date.today()
    this_month = today.month
    last_month = 12 if this_month == 1 else this_month - 1
    this_year = today.year
    last_month_year = this_year - 1 if this_month == 1 else this_year

    def totals_for(month, year):
        cat_totals = defaultdict(float)
        total_debit = 0.0
        for t in txns:
            if t.date.month == month and t.date.year == year and t.transaction_type == "DEBIT":
                cat_totals[t.category] += t.amount
                total_debit += t.amount
        return cat_totals, total_debit

    this_cat, this_total = totals_for(this_month, this_year)
    last_cat, last_total = totals_for(last_month, last_month_year)

    insights = []

    for category, amount in this_cat.items():
        prev = last_cat.get(category, 0)
        if prev > 0:
            change = (amount - prev) / prev * 100
            if change >= 15:
                insights.append(f"You spent {change:.0f}% more on {category} this month than last month.")
            elif change <= -15:
                insights.append(f"You spent {abs(change):.0f}% less on {category} this month than last month.")

    if this_cat:
        sorted_cats = sorted(this_cat.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_cats) >= 2:
            insights.append(f"{sorted_cats[1][0]} is your second-highest spending category this month.")
        insights.append(f"{sorted_cats[0][0]} is your top spending category this month.")

    total_income = sum(t.amount for t in txns if t.transaction_type == "CREDIT"
                        and t.date.month == this_month and t.date.year == this_year)
    net = total_income - this_total
    insights.append(f"Your current net savings this month are ₹{net:,.0f}.")

    if not insights:
        insights.append("Add a few transactions to start seeing personalized spending insights.")

    return insights


@insights_bp.route("/insights")
@login_required
def insights_page():
    return render_template("insights.html", insights=generate_insights(current_user.id))
