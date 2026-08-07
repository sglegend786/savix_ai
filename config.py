import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Central configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "savix.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    # Whether Google OAuth is actually configured
    GOOGLE_OAUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    EXPENSE_CATEGORIES = [
        "Food", "Transport", "Shopping", "Bills", "Entertainment",
        "Education", "Healthcare", "Travel", "Rent", "Investment", "Other",
    ]

    PAYMENT_METHODS = ["Cash", "UPI", "Card", "Bank Transfer", "Other"]

    APP_PLATFORMS = [
        "Swiggy", "Zomato", "Amazon", "Flipkart", "Uber", "Ola",
        "Netflix", "Other",
    ]
