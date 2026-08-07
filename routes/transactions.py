from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user

from extensions import db
from models import Transaction
from ml.predict import predict_category

transactions_bp = Blueprint("transactions", __name__)


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return datetime.utcnow().date()


@transactions_bp.route("/transactions")
@login_required
def list_transactions():
    txns = (Transaction.query
            .filter_by(user_id=current_user.id)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .all())
    return render_template(
        "transactions.html",
        transactions=txns,
        categories=current_app.config["EXPENSE_CATEGORIES"],
        payment_methods=current_app.config["PAYMENT_METHODS"],
        platforms=current_app.config["APP_PLATFORMS"],
    )


@transactions_bp.route("/transactions/predict", methods=["POST"])
@login_required
def predict():
    """JSON endpoint used by the Add Transaction form to live-predict a category."""
    data = request.get_json(silent=True) or {}
    description = data.get("description", "")
    category = predict_category(description)
    return jsonify({"predicted_category": category})


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "")
        transaction_type = request.form.get("transaction_type", "DEBIT").upper()
        category = request.form.get("category", "").strip()
        date_raw = request.form.get("date", "")
        payment_method = request.form.get("payment_method", "Other")
        app_platform = request.form.get("app_platform", "Other")

        errors = []
        if not description:
            errors.append("Description is required.")
        try:
            amount = float(amount_raw)
            if amount <= 0:
                errors.append("Amount must be greater than zero.")
        except ValueError:
            errors.append("Amount must be a valid number.")
            amount = 0

        if transaction_type not in ("CREDIT", "DEBIT"):
            errors.append("Invalid transaction type.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "transactions.html",
                transactions=Transaction.query.filter_by(user_id=current_user.id)
                    .order_by(Transaction.date.desc()).all(),
                categories=current_app.config["EXPENSE_CATEGORIES"],
                payment_methods=current_app.config["PAYMENT_METHODS"],
                platforms=current_app.config["APP_PLATFORMS"],
            )

        predicted = predict_category(description)
        final_category = category if category else predicted

        txn = Transaction(
            user_id=current_user.id,
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            category=final_category,
            predicted_category=predicted,
            date=_parse_date(date_raw),
            payment_method=payment_method,
            app_platform=app_platform,
        )
        db.session.add(txn)
        db.session.commit()
        flash("Transaction added successfully.", "success")
        return redirect(url_for("transactions.list_transactions"))

    return render_template(
        "transactions.html",
        transactions=Transaction.query.filter_by(user_id=current_user.id)
            .order_by(Transaction.date.desc()).all(),
        categories=current_app.config["EXPENSE_CATEGORIES"],
        payment_methods=current_app.config["PAYMENT_METHODS"],
        platforms=current_app.config["APP_PLATFORMS"],
        show_add_form=True,
    )


@transactions_bp.route("/transactions/edit/<int:txn_id>", methods=["POST"])
@login_required
def edit_transaction(txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first_or_404()

    txn.description = request.form.get("description", txn.description).strip()
    try:
        txn.amount = float(request.form.get("amount", txn.amount))
    except ValueError:
        flash("Invalid amount.", "danger")
        return redirect(url_for("transactions.list_transactions"))

    txn.transaction_type = request.form.get("transaction_type", txn.transaction_type).upper()
    txn.category = request.form.get("category", txn.category)
    txn.date = _parse_date(request.form.get("date")) if request.form.get("date") else txn.date
    txn.payment_method = request.form.get("payment_method", txn.payment_method)
    txn.app_platform = request.form.get("app_platform", txn.app_platform)

    db.session.commit()
    flash("Transaction updated.", "success")
    return redirect(url_for("transactions.list_transactions"))


@transactions_bp.route("/transactions/delete/<int:txn_id>", methods=["POST"])
@login_required
def delete_transaction(txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first_or_404()
    db.session.delete(txn)
    db.session.commit()
    flash("Transaction deleted.", "info")
    return redirect(url_for("transactions.list_transactions"))
