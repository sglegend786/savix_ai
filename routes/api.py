from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

from extensions import db
from models import User, InvestmentScheme, FinancialAlert

api_bp = Blueprint("api", __name__, url_prefix="/api")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # token expected in the format: Bearer <token>
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        
        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, current_app.config.get("JWT_SECRET_KEY", current_app.config["SECRET_KEY"]), algorithms=["HS256"])
            current_user = User.query.filter_by(id=data["user_id"]).first()
        except Exception as e:
            return jsonify({"success": False, "message": "Token is invalid"}), 401

        if not current_user:
            return jsonify({"success": False, "message": "User not found"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    secret = current_app.config.get("JWT_SECRET_KEY", current_app.config["SECRET_KEY"])
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.utcnow() + timedelta(days=7)},
        secret,
        algorithm="HS256"
    )

    return jsonify({
        "success": True, 
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "profile_picture": user.profile_picture
            }
        }
    })


@api_bp.route("/auth/me", methods=["GET"])
@token_required
def get_me(current_user):
    return jsonify({
        "success": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "monthly_income": current_user.monthly_income,
            "profile_picture": current_user.profile_picture
        }
    })


@api_bp.route("/notifications/my", methods=["GET"])
@token_required
def get_my_notifications(current_user):
    alerts = FinancialAlert.query.filter_by(user_id=current_user.id, is_read=False).order_by(FinancialAlert.created_at.desc()).all()
    data = []
    for alert in alerts:
        data.append({
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "created_at": alert.created_at.isoformat()
        })
    return jsonify({"success": True, "data": data})


@api_bp.route("/schemes/", methods=["GET"])
def get_schemes():
    schemes = InvestmentScheme.query.all()
    return jsonify({"success": True, "data": [s.to_dict() for s in schemes]})


@api_bp.route("/schemes/new", methods=["GET"])
def get_new_schemes():
    # Return 3 newest schemes for dashboard widgets
    schemes = InvestmentScheme.query.order_by(InvestmentScheme.id.desc()).limit(3).all()
    return jsonify({"success": True, "data": [s.to_dict() for s in schemes]})
