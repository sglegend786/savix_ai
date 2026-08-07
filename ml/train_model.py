"""
Trains a simple TF-IDF + Logistic Regression classifier that predicts an
expense category from a free-text transaction description.

Run with:
    python ml/train_model.py

Produces:
    ml/expense_model.pkl
"""
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_PATH = os.path.join(os.path.dirname(__file__), "expense_model.pkl")

TRAINING_DATA = [
    ("swiggy dinner order", "Food"),
    ("zomato lunch delivery", "Food"),
    ("dominos pizza", "Food"),
    ("restaurant bill dinner", "Food"),
    ("grocery store vegetables", "Food"),
    ("street food snacks", "Food"),
    ("coffee shop latte", "Food"),
    ("uber ride to office", "Transport"),
    ("ola cab airport", "Transport"),
    ("petrol fuel bike", "Transport"),
    ("metro card recharge", "Transport"),
    ("bus ticket", "Transport"),
    ("parking fee", "Transport"),
    ("amazon shopping order", "Shopping"),
    ("flipkart new shoes", "Shopping"),
    ("myntra clothes purchase", "Shopping"),
    ("electronics store purchase", "Shopping"),
    ("mall shopping clothes", "Shopping"),
    ("electricity bill payment", "Bills"),
    ("water bill payment", "Bills"),
    ("mobile recharge bill", "Bills"),
    ("broadband internet bill", "Bills"),
    ("gas cylinder bill", "Bills"),
    ("netflix subscription", "Entertainment"),
    ("movie tickets pvr", "Entertainment"),
    ("spotify premium subscription", "Entertainment"),
    ("gaming purchase steam", "Entertainment"),
    ("concert tickets", "Entertainment"),
    ("course fee udemy", "Education"),
    ("college tuition fee", "Education"),
    ("books purchase", "Education"),
    ("exam registration fee", "Education"),
    ("online certification course", "Education"),
    ("hospital consultation fee", "Healthcare"),
    ("pharmacy medicine purchase", "Healthcare"),
    ("doctor appointment fee", "Healthcare"),
    ("health checkup lab test", "Healthcare"),
    ("dental clinic visit", "Healthcare"),
    ("flight ticket booking", "Travel"),
    ("hotel booking makemytrip", "Travel"),
    ("train ticket irctc", "Travel"),
    ("holiday trip package", "Travel"),
    ("visa application fee", "Travel"),
    ("monthly house rent", "Rent"),
    ("apartment rent payment", "Rent"),
    ("pg rent payment", "Rent"),
    ("sip mutual fund investment", "Investment"),
    ("fixed deposit investment", "Investment"),
    ("stock market purchase", "Investment"),
    ("ppf contribution", "Investment"),
    ("gold purchase investment", "Investment"),
    ("miscellaneous expense", "Other"),
    ("cash withdrawal atm", "Other"),
    ("gift purchase for friend", "Other"),
    ("donation charity", "Other"),
]


def train_and_save():
    descriptions = [d for d, _ in TRAINING_DATA]
    labels = [c for _, c in TRAINING_DATA]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipeline.fit(descriptions, labels)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model trained on {len(descriptions)} samples and saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()
