import os
from flask import Flask, render_template
from flask_login import current_user
from flask_cors import CORS

from config import Config
from extensions import db, login_manager, oauth, csrf, limiter
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for the REST API
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

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

    # Phase 2+: new blueprints
    from routes.health import health_bp
    from routes.goals import goals_bp
    from routes.debt import debt_bp
    from routes.api import api_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(debt_bp)
    app.register_blueprint(api_bp)

    # CSRF exempt for API endpoints that use JSON (not forms)
    csrf.exempt(transactions_bp)   # /transactions/predict uses JSON POST
    csrf.exempt(analytics_bp)      # pure GET APIs
    csrf.exempt(investments_bp)    # /api/investments/calculate uses JSON POST
    csrf.exempt(health_bp)         # GET API
    csrf.exempt(debt_bp)           # /api/debt/emi-calculator
    csrf.exempt(api_bp)            # REST API (uses JWT)


    @app.context_processor
    def inject_globals():
        return {"current_user": current_user}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    @app.errorhandler(429)
    def ratelimit_error(e):
        return render_template("429.html"), 429

    with app.app_context():
        db.create_all()

    return app


app = create_app()

def keep_alive():
    import time
    import requests
    import os
    
    # Try to get the live URL from env, otherwise use localhost
    app_url = os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000")
    
    while True:
        try:
            time.sleep(10 * 60) # Sleep for 10 minutes
            requests.get(f"{app_url}/")
            print("Keep-alive ping sent to prevent sleep.")
        except Exception as e:
            print(f"Keep-alive ping failed: {e}")

import threading
# Start keep-alive thread in daemon mode so it closes when app closes
threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
