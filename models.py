from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


# ---------------------------------------------------------------------------
# EXISTING MODELS (preserved, extended where noted)
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(150), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW: financial profile fields
    monthly_income = db.Column(db.Float, nullable=True)
    preferred_language = db.Column(db.String(10), default="en")

    transactions = db.relationship("Transaction", backref="user", lazy=True,
                                    cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="user", lazy=True,
                               cascade="all, delete-orphan")
    investments = db.relationship("Investment", backref="user", lazy=True,
                                   cascade="all, delete-orphan")
    goals = db.relationship("FinancialGoal", backref="user", lazy=True,
                             cascade="all, delete-orphan")
    debts = db.relationship("Debt", backref="user", lazy=True,
                             cascade="all, delete-orphan")
    assets = db.relationship("Asset", backref="user", lazy=True,
                              cascade="all, delete-orphan")
    preferences = db.relationship("UserPreference", backref="user", lazy=True,
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
    ml_confidence = db.Column(db.Float, nullable=True)          # NEW: 0-100
    is_anomaly = db.Column(db.Boolean, default=False)           # NEW
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    payment_method = db.Column(db.String(50), nullable=True)
    app_platform = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)                    # NEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW: composite index for user+date queries (analytics, dashboard)
    __table_args__ = (
        db.Index("ix_txn_user_date", "user_id", "date"),
        db.Index("ix_txn_user_type", "user_id", "transaction_type"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "transaction_type": self.transaction_type,
            "category": self.category,
            "predicted_category": self.predicted_category,
            "ml_confidence": self.ml_confidence,
            "is_anomaly": self.is_anomaly,
            "date": self.date.isoformat(),
            "payment_method": self.payment_method,
            "app_platform": self.app_platform,
            "notes": self.notes,
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
    scheme_type = db.Column(db.String(50), nullable=False)
    provider = db.Column(db.String(150), nullable=True)
    interest_rate = db.Column(db.Float, nullable=True)
    minimum_investment = db.Column(db.Float, nullable=True)
    maximum_investment = db.Column(db.Float, nullable=True)
    tenure = db.Column(db.String(100), nullable=True)
    risk_level = db.Column(db.String(30), nullable=True)
    tax_notes = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    premature_withdrawal_info = db.Column(db.Text, nullable=True)
    official_link = db.Column(db.String(500), nullable=True)
    investment_steps = db.Column(db.Text, nullable=True)
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
            "official_link": self.official_link,
            "investment_steps": self.investment_steps,
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # NEW

    scheme = db.relationship("InvestmentScheme")


# ---------------------------------------------------------------------------
# NEW MODELS — Phase 2+
# ---------------------------------------------------------------------------

class FinancialGoal(db.Model):
    __tablename__ = "financial_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False, default="Custom")
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Integer, default=1)  # 1=High, 2=Medium, 3=Low
    monthly_contribution = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def progress_pct(self):
        if self.target_amount and self.target_amount > 0:
            return min(round(self.current_amount / self.target_amount * 100, 1), 100)
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "goal_type": self.goal_type,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "monthly_contribution": self.monthly_contribution,
            "is_active": self.is_active,
            "progress_pct": self.progress_pct,
        }


class Debt(db.Model):
    __tablename__ = "debts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    loan_name = db.Column(db.String(150), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False, default="Personal Loan")
    principal = db.Column(db.Float, nullable=False)
    outstanding = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)   # % p.a.
    emi = db.Column(db.Float, nullable=True)
    tenure_months = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    due_day = db.Column(db.Integer, nullable=True)         # day of month EMI is due
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "loan_name": self.loan_name,
            "loan_type": self.loan_type,
            "principal": self.principal,
            "outstanding": self.outstanding,
            "interest_rate": self.interest_rate,
            "emi": self.emi,
            "tenure_months": self.tenure_months,
            "due_day": self.due_day,
            "is_active": self.is_active,
        }


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    asset_name = db.Column(db.String(150), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # cash/investment/property/gold/other
    current_value = db.Column(db.Float, nullable=False)
    purchase_value = db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NetWorthSnapshot(db.Model):
    __tablename__ = "net_worth_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    total_assets = db.Column(db.Float, nullable=False)
    total_liabilities = db.Column(db.Float, nullable=False)
    net_worth = db.Column(db.Float, nullable=False)
    snapshot_date = db.Column(db.Date, nullable=False, default=date.today)


class FinancialHealthScore(db.Model):
    __tablename__ = "financial_health_scores"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    score = db.Column(db.Float, nullable=False)                    # 0-100
    savings_rate_score = db.Column(db.Float, nullable=True)
    expense_control_score = db.Column(db.Float, nullable=True)
    budget_adherence_score = db.Column(db.Float, nullable=True)
    emergency_fund_score = db.Column(db.Float, nullable=True)
    debt_score = db.Column(db.Float, nullable=True)
    investment_score = db.Column(db.Float, nullable=True)
    goal_score = db.Column(db.Float, nullable=True)
    breakdown_json = db.Column(db.Text, nullable=True)             # JSON string
    computed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), default="monthly")       # monthly/annual/weekly
    category = db.Column(db.String(50), nullable=True)
    detected_from_txn = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default="active")           # active/inactive/ignored
    last_charged = db.Column(db.Date, nullable=True)
    next_expected = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FinancialAlert(db.Model):
    __tablename__ = "financial_alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), default="attention")      # normal/attention/warning/critical
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)


class AIConversation(db.Model):
    __tablename__ = "ai_conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)               # user/assistant
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "preference_key", name="uq_user_pref_key"),
    )


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(300), nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
