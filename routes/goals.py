from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import FinancialGoal
from services.goal_service import (
    required_monthly_contribution, projected_completion_months, goal_health
)
from config import Config

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/goals")
@login_required
def goals_page():
    goals = FinancialGoal.query.filter_by(user_id=current_user.id).order_by(
        FinancialGoal.priority, FinancialGoal.created_at.desc()
    ).all()
    goal_data = []
    for g in goals:
        req_monthly = None
        proj_months = None
        if g.deadline and g.progress_pct < 100:
            req_monthly = required_monthly_contribution(g.target_amount, g.current_amount, g.deadline)
        if g.monthly_contribution and g.monthly_contribution > 0:
            proj_months = projected_completion_months(g.target_amount, g.current_amount, g.monthly_contribution)
        goal_data.append({
            "goal": g,
            "health": goal_health(g),
            "required_monthly": req_monthly,
            "projected_months": proj_months,
        })
    return render_template("goals.html", goal_data=goal_data, goal_types=Config.GOAL_TYPES, today=date.today())


@goals_bp.route("/goals/add", methods=["POST"])
@login_required
def add_goal():
    try:
        name        = request.form.get("name", "").strip()
        goal_type   = request.form.get("goal_type", "Custom")
        target      = float(request.form.get("target_amount", 0))
        current     = float(request.form.get("current_amount", 0))
        monthly     = request.form.get("monthly_contribution", "")
        priority    = int(request.form.get("priority", 2))
        deadline_s  = request.form.get("deadline", "")
        notes       = request.form.get("notes", "").strip()

        if not name or target <= 0:
            flash("Goal name and a positive target amount are required.", "danger")
            return redirect(url_for("goals.goals_page"))

        deadline = datetime.strptime(deadline_s, "%Y-%m-%d").date() if deadline_s else None
        monthly_val = float(monthly) if monthly else None

        goal = FinancialGoal(
            user_id=current_user.id, name=name, goal_type=goal_type,
            target_amount=target, current_amount=current,
            monthly_contribution=monthly_val, priority=priority,
            deadline=deadline, notes=notes,
        )
        db.session.add(goal)
        db.session.commit()
        flash(f'Goal "{name}" created!', "success")
    except (ValueError, TypeError) as e:
        flash("Invalid data - please check all fields.", "danger")
    return redirect(url_for("goals.goals_page"))


@goals_bp.route("/goals/<int:goal_id>/update", methods=["POST"])
@login_required
def update_goal(goal_id):
    goal = FinancialGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    try:
        action = request.form.get("action")
        if action == "add_funds":
            amount = float(request.form.get("amount", 0))
            goal.current_amount = min(goal.current_amount + amount, goal.target_amount)
            db.session.commit()
            flash(f'Added {amount:.0f} to "{goal.name}".', "success")
        elif action == "toggle":
            goal.is_active = not goal.is_active
            db.session.commit()
            flash("Goal status updated.", "success")
    except (ValueError, TypeError):
        flash("Invalid amount.", "danger")
    return redirect(url_for("goals.goals_page"))


@goals_bp.route("/goals/<int:goal_id>/delete", methods=["POST"])
@login_required
def delete_goal(goal_id):
    goal = FinancialGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    name = goal.name
    db.session.delete(goal)
    db.session.commit()
    flash(f'Goal "{name}" deleted.', "success")
    return redirect(url_for("goals.goals_page"))
