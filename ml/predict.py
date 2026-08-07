"""
Loads the trained model (if present) and predicts an expense category
from a transaction description. Falls back gracefully to a keyword-based
heuristic if the model file is missing, so the app never crashes.
"""
import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "expense_model.pkl")

_model = None
_model_loaded = False

FALLBACK_KEYWORDS = {
    "Food": ["swiggy", "zomato", "restaurant", "food", "dinner", "lunch", "cafe", "pizza"],
    "Transport": ["uber", "ola", "petrol", "fuel", "metro", "bus", "taxi", "cab"],
    "Shopping": ["amazon", "flipkart", "myntra", "shopping", "mall", "store"],
    "Bills": ["bill", "electricity", "water", "recharge", "broadband"],
    "Entertainment": ["netflix", "movie", "spotify", "game", "concert"],
    "Education": ["course", "tuition", "college", "exam", "book"],
    "Healthcare": ["hospital", "pharmacy", "doctor", "clinic", "medicine"],
    "Travel": ["flight", "hotel", "train", "irctc", "trip", "visa"],
    "Rent": ["rent"],
    "Investment": ["sip", "mutual fund", "fixed deposit", "stock", "ppf", "gold"],
}


def _load_model():
    global _model, _model_loaded
    if not _model_loaded:
        if os.path.exists(MODEL_PATH):
            try:
                _model = joblib.load(MODEL_PATH)
            except Exception:
                _model = None
        _model_loaded = True
    return _model


def _fallback_predict(description: str) -> str:
    text = description.lower()
    for category, keywords in FALLBACK_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "Other"


def predict_category(description: str) -> str:
    """Predict an expense category for the given description text."""
    if not description or not description.strip():
        return "Other"

    model = _load_model()
    if model is not None:
        try:
            return model.predict([description])[0]
        except Exception:
            return _fallback_predict(description)
    return _fallback_predict(description)
