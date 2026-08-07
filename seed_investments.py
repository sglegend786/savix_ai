"""Seeds sample investment scheme reference data.
    python seed_investments.py

NOTE: The rates below are indicative sample figures for demo purposes only,
NOT live/current rates. Always verify with the official provider.
"""
from app import create_app
from extensions import db
from models import InvestmentScheme

app = create_app()

SCHEMES = [
    dict(name="Bank Fixed Deposit (FD)", scheme_type="FD", provider="Various Banks",
         interest_rate=7.0, minimum_investment=1000, maximum_investment=None,
         tenure="7 days - 10 years", risk_level="Low",
         tax_notes="Interest is taxable as per income slab; TDS may apply.",
         premature_withdrawal_info="Allowed with penalty, varies by bank.",
         description="A lump-sum deposit that earns a fixed interest rate over a chosen tenure."),
    dict(name="Recurring Deposit (RD)", scheme_type="RD", provider="Various Banks",
         interest_rate=6.8, minimum_investment=100, maximum_investment=None,
         tenure="6 months - 10 years", risk_level="Low",
         tax_notes="Interest is taxable as per income slab; TDS may apply.",
         premature_withdrawal_info="Allowed with penalty, varies by bank.",
         description="Invest a fixed amount every month and earn compounded interest."),
    dict(name="Systematic Investment Plan (SIP)", scheme_type="SIP", provider="Mutual Fund AMCs",
         interest_rate=12.0, minimum_investment=500, maximum_investment=None,
         tenure="Flexible / Open-ended", risk_level="Market-linked",
         tax_notes="Equity SIPs: LTCG/STCG rules apply. Debt SIPs taxed as per slab.",
         premature_withdrawal_info="Redeemable anytime; exit load may apply for short holding periods.",
         description="Invest a fixed amount monthly in a mutual fund scheme; returns are market-linked, not guaranteed."),
    dict(name="Monthly Income Scheme (MIS)", scheme_type="MIS", provider="Post Office",
         interest_rate=7.4, minimum_investment=1000, maximum_investment=900000,
         tenure="5 years", risk_level="Low",
         tax_notes="Interest is fully taxable as per income slab.",
         premature_withdrawal_info="Allowed after 1 year with a deduction from principal.",
         description="Government-backed scheme paying a fixed monthly interest payout."),
    dict(name="Public Provident Fund (PPF)", scheme_type="PPF", provider="Government of India",
         interest_rate=7.1, minimum_investment=500, maximum_investment=150000,
         tenure="15 years (extendable)", risk_level="Low",
         tax_notes="EEE status — contributions, interest, and maturity are tax-exempt (subject to current rules).",
         premature_withdrawal_info="Partial withdrawal allowed from 7th year; premature closure has restrictions.",
         description="A long-term government savings scheme with tax-free compounded interest."),
    dict(name="National Savings Certificate (NSC)", scheme_type="NSC", provider="Post Office",
         interest_rate=7.7, minimum_investment=1000, maximum_investment=None,
         tenure="5 years", risk_level="Low",
         tax_notes="Eligible for deduction under Sec 80C; interest is taxable but reinvested interest also qualifies for deduction.",
         premature_withdrawal_info="Generally not allowed except in specific circumstances (death, court order).",
         description="A fixed-income government savings certificate popular for tax-saving."),
    dict(name="Post Office Time Deposit (POTD)", scheme_type="Post Office Time Deposit", provider="Post Office",
         interest_rate=7.5, minimum_investment=1000, maximum_investment=None,
         tenure="1-5 years", risk_level="Low",
         tax_notes="Interest taxable as per slab; 5-year POTD eligible under Sec 80C.",
         premature_withdrawal_info="Allowed after 6 months with reduced interest.",
         description="Similar to a bank FD, offered through India Post with government backing."),
    dict(name="Post Office Monthly Income Scheme (POMIS)", scheme_type="Post Office Monthly Income Scheme",
         provider="Post Office", interest_rate=7.4, minimum_investment=1000, maximum_investment=900000,
         tenure="5 years", risk_level="Low",
         tax_notes="Interest is fully taxable as per income slab.",
         premature_withdrawal_info="Allowed after 1 year with a deduction from principal.",
         description="Government scheme offering a fixed monthly income on a lump-sum deposit."),
    dict(name="Kisan Vikas Patra (KVP)", scheme_type="Kisan Vikas Patra", provider="Post Office",
         interest_rate=7.5, minimum_investment=1000, maximum_investment=None,
         tenure="~115 months (approx. doubling period)", risk_level="Low",
         tax_notes="No Sec 80C deduction; interest is taxable as per slab.",
         premature_withdrawal_info="Allowed after 2.5 years.",
         description="A government certificate scheme designed to double the invested amount over a fixed period."),
    dict(name="Senior Citizen Savings Scheme (SCSS)", scheme_type="Senior Citizen Savings Scheme",
         provider="Post Office / Banks", interest_rate=8.2, minimum_investment=1000, maximum_investment=3000000,
         tenure="5 years (extendable by 3 years)", risk_level="Low",
         tax_notes="Eligible under Sec 80C; interest is taxable and TDS applies above threshold.",
         premature_withdrawal_info="Allowed after 1 year with a penalty.",
         description="A government scheme for individuals aged 60+, offering regular quarterly interest payouts."),
    dict(name="Sukanya Samriddhi Yojana (SSY)", scheme_type="Sukanya Samriddhi Scheme", provider="Post Office / Banks",
         interest_rate=8.2, minimum_investment=250, maximum_investment=150000,
         tenure="21 years from account opening", risk_level="Low",
         tax_notes="EEE status — contributions, interest, and maturity are tax-exempt (subject to current rules).",
         premature_withdrawal_info="Partial withdrawal allowed for higher education after age 18; premature closure restricted.",
         description="A government savings scheme for the welfare of a girl child, opened by a parent/guardian."),
]


def seed():
    with app.app_context():
        for data in SCHEMES:
            exists = InvestmentScheme.query.filter_by(name=data["name"]).first()
            if not exists:
                db.session.add(InvestmentScheme(**data))
        db.session.commit()
        print(f"Seeded {len(SCHEMES)} investment schemes (skipping duplicates).")


if __name__ == "__main__":
    seed()
