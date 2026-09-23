from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import InvestmentScheme, Investment

investments_bp = Blueprint("investments", __name__)


@investments_bp.route("/investments")
@login_required
def investments_page():
    schemes = InvestmentScheme.query.order_by(InvestmentScheme.scheme_type).all()
    my_investments = Investment.query.filter_by(user_id=current_user.id).all()
    return render_template("investments.html", schemes=schemes, my_investments=my_investments)


@investments_bp.route("/investments/<int:scheme_id>")
@login_required
def scheme_detail(scheme_id):
    scheme = InvestmentScheme.query.get_or_404(scheme_id)
    return jsonify(scheme.to_dict())


@investments_bp.route("/investments/invest/<int:scheme_id>", methods=["POST"])
@login_required
def invest_in_scheme(scheme_id):
    scheme = InvestmentScheme.query.get_or_404(scheme_id)
    try:
        amount = float(request.form.get("amount", 0))
        tenure = int(request.form.get("tenure", 1))
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Please enter a valid amount and tenure.", "danger")
        return redirect(url_for("investments.investments_page"))

    investment = Investment(
        user_id=current_user.id,
        scheme_id=scheme.id,
        amount=amount,
        start_date=date.today(),
        tenure=tenure,
        expected_rate=scheme.interest_rate,
    )
    db.session.add(investment)
    db.session.commit()
    flash(f"Recorded your investment in {scheme.name}. This is a tracking entry, not a live transaction.", "success")
    return redirect(url_for("investments.investments_page"))


@investments_bp.route("/investments/compare")
@login_required
def compare_page():
    scheme_ids = request.args.getlist("scheme_id", type=int)
    schemes = InvestmentScheme.query.filter(InvestmentScheme.id.in_(scheme_ids)).all() if scheme_ids else []
    all_schemes = InvestmentScheme.query.order_by(InvestmentScheme.scheme_type).all()
    return render_template("compare.html", schemes=schemes, all_schemes=all_schemes)


@investments_bp.route("/api/investments/calculate", methods=["POST"])
@login_required
def calculate_returns():
    """Illustrative maturity/return calculator. Supports lump-sum (FD/RD/PPF style)
    and SIP (monthly contribution) calculations."""
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "lumpsum")

    try:
        rate = float(data.get("rate", 0)) / 100
        years = float(data.get("years", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400

    if mode == "sip":
        try:
            monthly = float(data.get("monthly_amount", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid input"}), 400
        months = int(years * 12)
        monthly_rate = rate / 12
        if monthly_rate > 0:
            future_value = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            future_value = monthly * months
        invested = monthly * months
        return jsonify({
            "invested": round(invested, 2),
            "estimated_interest": round(future_value - invested, 2),
            "estimated_maturity": round(future_value, 2),
        })
    else:
        try:
            principal = float(data.get("amount", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid input"}), 400
        # Standard compound interest, compounded annually (illustrative only)
        maturity = principal * ((1 + rate) ** years)
        return jsonify({
            "invested": round(principal, 2),
            "estimated_interest": round(maturity - principal, 2),
            "estimated_maturity": round(maturity, 2),
        })

@investments_bp.route("/investments/remove/<int:investment_id>", methods=["POST"])
@login_required
def remove_investment(investment_id):
    investment = Investment.query.get_or_404(investment_id)
    if investment.user_id != current_user.id:
        flash("You are not authorized to remove this investment.", "danger")
        return redirect(url_for("investments.investments_page"))
    
    db.session.delete(investment)
    db.session.commit()
    flash("Tracked investment removed successfully.", "success")
    return redirect(url_for("investments.investments_page"))
