import os
from flask import Flask, render_template
from flask_login import current_user

from config import Config
from extensions import db, login_manager, oauth
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    if app.config["GOOGLE_OAUTH_ENABLED"]:
        oauth.init_app(app)
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.transactions import transactions_bp
    from routes.analytics import analytics_bp
    from routes.budget import budget_bp
    from routes.investments import investments_bp
    from routes.profile import profile_bp
    from routes.insights import insights_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(investments_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(insights_bp)

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
