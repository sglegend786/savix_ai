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
    dict(name="SBI Fixed Deposit (FD)", scheme_type="Fixed Deposits (FD)", provider="State Bank of India (SBI)",
         interest_rate=7.0, minimum_investment=1000, maximum_investment=None,
         tenure="7 days - 10 years", risk_level="Low",
         tax_notes="Interest is taxable as per income slab; TDS applies.",
         premature_withdrawal_info="Allowed with penalty.",
         description="SBI Fixed Deposit offering secure returns.",
         official_link="https://sbi.co.in/web/personal-banking/investments-deposits/deposits",
         investment_steps="1. Log in to SBI YONO or NetBanking.\n2. Go to 'Deposits' -> 'Open Fixed Deposit'.\n3. Enter amount and tenure.\n4. Confirm to open instantly."),
    dict(name="HDFC Fixed Deposit (FD)", scheme_type="Fixed Deposits (FD)", provider="HDFC Bank",
         interest_rate=7.1, minimum_investment=5000, maximum_investment=None,
         tenure="7 days - 10 years", risk_level="Low",
         tax_notes="Interest is taxable as per income slab.",
         premature_withdrawal_info="Allowed with penalty.",
         description="HDFC Bank Fixed Deposit for steady growth.",
         official_link="https://www.hdfcbank.com/personal/save/deposits/fixed-deposit",
         investment_steps="1. Log in to HDFC NetBanking.\n2. Navigate to 'Transact' -> 'Open Fixed Deposit'.\n3. Fill in the deposit details.\n4. Authenticate and submit."),
    dict(name="ICICI Fixed Deposit (FD)", scheme_type="Fixed Deposits (FD)", provider="ICICI Bank",
         interest_rate=7.1, minimum_investment=10000, maximum_investment=None,
         tenure="7 days - 10 years", risk_level="Low",
         tax_notes="Interest is taxable as per income slab.",
         premature_withdrawal_info="Allowed with penalty.",
         description="ICICI Bank FD offering competitive interest rates.",
         official_link="https://www.icicibank.com/personal-banking/deposits/fixed-deposit",
         investment_steps="1. Log in to ICICI iMobile or NetBanking.\n2. Go to 'Deposits' -> 'Open FD'.\n3. Enter amount, tenure, and payout preference.\n4. Submit to open the FD."),
    dict(name="Axis Bank Fixed Deposit (FD)", scheme_type="Fixed Deposits (FD)", provider="Axis Bank",
         interest_rate=7.2, minimum_investment=5000, maximum_investment=None,
         tenure="7 days - 10 years", risk_level="Low",
         tax_notes="Interest is taxable as per income slab.",
         premature_withdrawal_info="Allowed with penalty.",
         description="Axis Bank FD with flexible tenure options.",
         official_link="https://www.axisbank.com/retail/investment/fixed-deposit",
         investment_steps="1. Log in to Axis Mobile App.\n2. Click on 'Deposits' -> 'Open FD'.\n3. Choose amount and tenure.\n4. Complete the process digitally."),

    dict(name="SBI Recurring Deposit (RD)", scheme_type="Recurring Deposits (RD)", provider="State Bank of India (SBI)",
         interest_rate=6.8, minimum_investment=100, maximum_investment=None,
         tenure="12 months - 10 years", risk_level="Low",
         tax_notes="Interest is taxable.",
         premature_withdrawal_info="Allowed with penalty.",
         description="Save a fixed amount monthly with SBI RD.",
         official_link="https://sbi.co.in/web/personal-banking/investments-deposits/deposits",
         investment_steps="1. Log in to SBI YONO.\n2. Go to 'Deposits' -> 'Recurring Deposit'.\n3. Set monthly amount and tenure.\n4. Set auto-debit account and confirm."),
    dict(name="HDFC Recurring Deposit (RD)", scheme_type="Recurring Deposits (RD)", provider="HDFC Bank",
         interest_rate=7.0, minimum_investment=1000, maximum_investment=None,
         tenure="6 months - 10 years", risk_level="Low",
         tax_notes="Interest is taxable.",
         premature_withdrawal_info="Allowed with penalty.",
         description="HDFC RD for disciplined monthly savings.",
         official_link="https://www.hdfcbank.com/personal/save/deposits/recurring-deposit",
         investment_steps="1. Log in to HDFC NetBanking.\n2. Transact -> Open Recurring Deposit.\n3. Choose monthly amount and tenure.\n4. Confirm auto-deduction."),

    dict(name="Groww Mutual Fund (SIP)", scheme_type="Mutual Fund SIPs", provider="Groww",
         interest_rate=12.0, minimum_investment=100, maximum_investment=None,
         tenure="Flexible", risk_level="Market-linked",
         tax_notes="LTCG/STCG rules apply.",
         premature_withdrawal_info="Redeemable anytime (exit load may apply).",
         description="Invest in mutual funds via SIP using the Groww platform.",
         official_link="https://groww.in/mutual-funds",
         investment_steps="1. Download Groww app and complete KYC.\n2. Select a mutual fund.\n3. Click 'Start SIP'.\n4. Enter monthly amount and date.\n5. Approve AutoPay mandate."),
    dict(name="Zerodha Coin (SIP)", scheme_type="Mutual Fund SIPs", provider="Zerodha",
         interest_rate=12.0, minimum_investment=500, maximum_investment=None,
         tenure="Flexible", risk_level="Market-linked",
         tax_notes="LTCG/STCG rules apply.",
         premature_withdrawal_info="Redeemable anytime.",
         description="Direct mutual fund SIPs via Zerodha Coin.",
         official_link="https://coin.zerodha.com/",
         investment_steps="1. Open a Zerodha Demat account.\n2. Log in to Coin.\n3. Choose a direct mutual fund.\n4. Create an AMC SIP or Coin SIP.\n5. Ensure funds in trading account/mandate."),

    dict(name="Post Office Public Provident Fund (PPF)", scheme_type="Public Provident Fund (PPF)", provider="Post Office",
         interest_rate=7.1, minimum_investment=500, maximum_investment=150000,
         tenure="15 years", risk_level="Low",
         tax_notes="EEE status (Completely Tax Free).",
         premature_withdrawal_info="Partial withdrawal from 7th year.",
         description="Traditional Post Office PPF scheme.",
         official_link="https://www.indiapost.gov.in/",
         investment_steps="1. Visit the nearest Post Office.\n2. Fill the PPF account opening form.\n3. Submit KYC documents and initial deposit.\n4. Get your PPF passbook."),
    dict(name="SBI Public Provident Fund (PPF)", scheme_type="Public Provident Fund (PPF)", provider="State Bank of India (SBI)",
         interest_rate=7.1, minimum_investment=500, maximum_investment=150000,
         tenure="15 years", risk_level="Low",
         tax_notes="EEE status (Completely Tax Free).",
         premature_withdrawal_info="Partial withdrawal from 7th year.",
         description="SBI PPF account with online management.",
         official_link="https://sbi.co.in/web/personal-banking/investments-deposits/govt-schemes/ppf",
         investment_steps="1. Log in to SBI NetBanking.\n2. Go to 'Request & Enquiries' -> 'New PPF Account'.\n3. Fill details and print the form.\n4. Visit branch with KYC to activate."),

    dict(name="Post Office Monthly Income Scheme (MIS)", scheme_type="Monthly Income Scheme (MIS)", provider="Post Office",
         interest_rate=7.4, minimum_investment=1000, maximum_investment=900000,
         tenure="5 years", risk_level="Low",
         tax_notes="Interest is taxable.",
         premature_withdrawal_info="Allowed after 1 year with penalty.",
         description="Govt-backed scheme with fixed monthly payout.",
         official_link="https://www.indiapost.gov.in/",
         investment_steps="1. Visit Post Office branch.\n2. Submit MIS form with KYC.\n3. Deposit via cheque.\n4. Link Post Office savings account for monthly interest."),
    
    dict(name="Kisan Vikas Patra (KVP)", scheme_type="Kisan Vikas Patra (KVP)", provider="Post Office",
         interest_rate=7.5, minimum_investment=1000, maximum_investment=None,
         tenure="~115 months", risk_level="Low",
         tax_notes="Interest is taxable.",
         premature_withdrawal_info="Allowed after 2.5 years.",
         description="Doubles the invested amount over a fixed period.",
         official_link="https://www.indiapost.gov.in/",
         investment_steps="1. Visit the Post Office.\n2. Fill Form A for KVP.\n3. Submit KYC and payment.\n4. Receive KVP certificate."),

    dict(name="Sukanya Samriddhi Yojana (SSY)", scheme_type="Sukanya Samriddhi Yojana (SSY)", provider="SBI / Post Office",
         interest_rate=8.2, minimum_investment=250, maximum_investment=150000,
         tenure="21 years", risk_level="Low",
         tax_notes="EEE status (Completely Tax Free).",
         premature_withdrawal_info="Allowed for education after age 18.",
         description="Scheme for the welfare of a girl child.",
         official_link="https://www.indiapost.gov.in/",
         investment_steps="1. Visit SBI or Post Office.\n2. Submit SSY form, child's birth certificate, and parent's KYC.\n3. Make initial deposit.\n4. Receive passbook.")
]

def seed():
    with app.app_context():
        for data in SCHEMES:
            exists = InvestmentScheme.query.filter_by(name=data["name"]).first()
            if not exists:
                db.session.add(InvestmentScheme(**data))
            else:
                exists.official_link = data.get("official_link")
                exists.investment_steps = data.get("investment_steps")
        db.session.commit()
        print(f"Seeded/Updated {len(SCHEMES)} investment schemes.")

if __name__ == "__main__":
    seed()
