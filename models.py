from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(150), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="user", lazy=True,
                                    cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="user", lazy=True,
                               cascade="all, delete-orphan")
    investments = db.relationship("Investment", backref="user", lazy=True,
                                   cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    @property
    def has_password(self):
        return bool(self.password_hash)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # CREDIT / DEBIT
    category = db.Column(db.String(50), nullable=False)
    predicted_category = db.Column(db.String(50), nullable=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(50), nullable=True)
    app_platform = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "category": self.category,
            "predicted_category": self.predicted_category,
            "date": self.date.isoformat(),
            "payment_method": self.payment_method,
            "app_platform": self.app_platform,
        }


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "month", "year", name="uq_user_month_year"),
    )


class InvestmentScheme(db.Model):
    __tablename__ = "investment_schemes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    scheme_type = db.Column(db.String(50), nullable=False)  # FD, RD, SIP, PPF ...
    provider = db.Column(db.String(150), nullable=True)
    interest_rate = db.Column(db.Float, nullable=True)  # % p.a., indicative
    minimum_investment = db.Column(db.Float, nullable=True)
    maximum_investment = db.Column(db.Float, nullable=True)
    tenure = db.Column(db.String(100), nullable=True)
    risk_level = db.Column(db.String(30), nullable=True)  # Low/Medium/High/Market-linked
    tax_notes = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    premature_withdrawal_info = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "scheme_type": self.scheme_type,
            "provider": self.provider,
            "interest_rate": self.interest_rate,
            "minimum_investment": self.minimum_investment,
            "maximum_investment": self.maximum_investment,
            "tenure": self.tenure,
            "risk_level": self.risk_level,
            "tax_notes": self.tax_notes,
            "description": self.description,
            "premature_withdrawal_info": self.premature_withdrawal_info,
            "updated_at": self.updated_at.strftime("%Y-%m-%d") if self.updated_at else None,
        }


class Investment(db.Model):
    __tablename__ = "investments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    scheme_id = db.Column(db.Integer, db.ForeignKey("investment_schemes.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    tenure = db.Column(db.Integer, nullable=True)  # in years
    expected_rate = db.Column(db.Float, nullable=True)

    scheme = db.relationship("InvestmentScheme")
