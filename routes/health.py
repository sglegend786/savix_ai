from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from services.financial_brain import get_financial_profile
from services.health_score import compute_health_score

health_bp = Blueprint("health", __name__)


@health_bp.route("/health-score")
@login_required
def health_score_page():
    profile = get_financial_profile(current_user.id)
    score_data = compute_health_score(profile)
    return render_template("health_score.html", profile=profile, score=score_data)


@health_bp.route("/api/health-score")
@login_required
def api_health_score():
    profile = get_financial_profile(current_user.id)
    score_data = compute_health_score(profile)
    return jsonify({"success": True, "data": {**score_data, "profile": profile}})
