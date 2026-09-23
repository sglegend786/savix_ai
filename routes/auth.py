import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from extensions import db, oauth, limiter
from models import User, AuditLog

auth_bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 8  # Increased from 6 for financial app security


def _log_audit(action, user_id=None, details=None):
    """Write an audit log entry."""
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:300] if request.user_agent else None,
            details=details,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass  # Never crash the app because of audit logging


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")  # Rate limit: 10 login attempts per minute per IP
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", google_enabled=current_app.config["GOOGLE_OAUTH_ENABLED"])

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            _log_audit("login_success", user_id=user.id, details=f"email={email}")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.dashboard"))

        _log_audit("login_failed", details=f"email={email}")
        flash("Invalid email or password.", "danger")

    return render_template("login.html", google_enabled=current_app.config["GOOGLE_OAUTH_ENABLED"])


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < MIN_PASSWORD_LENGTH:
            flash(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
            return render_template("register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        _log_audit("register", user_id=user.id, details=f"email={email}")
        login_user(user)
        flash("Account created successfully. Welcome to SAVIX AI!", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html")


@auth_bp.route("/auth/google")
def google_login():
    if not current_app.config["GOOGLE_OAUTH_ENABLED"]:
        flash("Google login is not configured on this server yet.", "warning")
        return redirect(url_for("auth.login"))
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/auth/google/callback")
def google_callback():
    if not current_app.config["GOOGLE_OAUTH_ENABLED"]:
        return redirect(url_for("auth.login"))

    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get("userinfo") or oauth.google.userinfo()
    except Exception as e:
        current_app.logger.warning(f"Google OAuth failed: {e}")
        flash("Google authentication failed. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    google_id = userinfo.get("sub")
    email = (userinfo.get("email") or "").lower()
    name = userinfo.get("name", email.split("@")[0] if email else "SAVIX User")
    picture = userinfo.get("picture")

    if not email:
        flash("Could not retrieve email from Google account.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, google_id=google_id, profile_picture=picture)
        db.session.add(user)
        db.session.commit()
        _log_audit("register_google", user_id=user.id, details=f"email={email}")
    elif not user.google_id:
        user.google_id = google_id
        if picture:
            user.profile_picture = picture
        db.session.commit()

    login_user(user)
    _log_audit("login_google", user_id=user.id, details=f"email={email}")

    if not user.has_password:
        return redirect(url_for("auth.set_password"))

    return redirect(url_for("dashboard.dashboard"))


@auth_bp.route("/set-password", methods=["GET", "POST"])
@login_required
def set_password():
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(password) < MIN_PASSWORD_LENGTH:
            flash(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "danger")
            return render_template("set_password.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("set_password.html")

        current_user.set_password(password)
        db.session.commit()
        _log_audit("set_password", user_id=current_user.id)
        flash("Password set successfully. You can now log in with email + password too.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("set_password.html")


@auth_bp.route("/logout")
@login_required
def logout():
    _log_audit("logout", user_id=current_user.id)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


