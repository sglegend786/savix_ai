from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_name":
            name = request.form.get("name", "").strip()
            if name:
                current_user.name = name
                db.session.commit()
                flash("Name updated.", "success")
            else:
                flash("Name cannot be empty.", "danger")

        elif action == "change_password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if current_user.has_password and not current_user.check_password(current_password):
                flash("Current password is incorrect.", "danger")
            elif len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "danger")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Password changed successfully.", "success")

        return redirect(url_for("profile.profile_page"))

    return render_template("profile.html")
