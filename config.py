import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Central configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me-in-production")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "savix.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security — CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour token validity

    # Security — Session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_OAUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    # AI Provider (optional — app works without this)
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "local")  # "local" or "gemini"
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"

    EXPENSE_CATEGORIES = [
        "Food", "Transport", "Shopping", "Bills", "Entertainment",
        "Education", "Healthcare", "Travel", "Rent", "Investment",
        "Savings", "EMI", "Subscription", "Other",
    ]

    PAYMENT_METHODS = ["Cash", "UPI", "Card", "Net Banking", "Bank Transfer", "Other"]

    APP_PLATFORMS = [
        "Swiggy", "Zomato", "Amazon", "Flipkart", "Uber", "Ola",
        "Netflix", "Spotify", "PhonePe", "Paytm", "IRCTC", "MakeMyTrip",
        "Myntra", "BigBasket", "Dunzo", "Blinkit", "Other",
    ]

    GOAL_TYPES = [
        "Emergency Fund", "Bike", "Car", "House Down Payment",
        "Education", "Marriage", "Travel", "Retirement",
        "Child Education", "Investment Corpus", "Custom",
    ]
