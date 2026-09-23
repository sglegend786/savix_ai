"""SAVIX Financial Health Score engine - 0 to 100, fully explainable.
Every component is based on real user data from the Financial Brain profile.
"""

WEIGHTS = {
    "savings_rate":    20,
    "expense_control": 15,
    "budget_adherence":15,
    "emergency_fund":  15,
    "debt_burden":     15,
    "investment":      10,
    "goal_progress":   10,
}


def _score_savings_rate(savings_rate):
    if savings_rate >= 30:
        return 100, "Excellent savings rate (30%+)"
    elif savings_rate >= 20:
        return 80,  "Good savings rate (20-30%)"
    elif savings_rate >= 10:
        return 55,  "Moderate savings rate (10-20%)"
    elif savings_rate > 0:
        return 30,  "Low savings rate (<10%) - aim to save more"
    else:
        return 0,   "Spending exceeds income this month"


def _score_expense_control(this_month, last_month):
    if last_month == 0:
        return 70, "No comparison data yet"
    change_pct = (this_month - last_month) / last_month * 100
    if change_pct <= -10:
        return 100, f"Spending reduced by {abs(change_pct):.0f}% vs last month"
    elif change_pct <= 0:
        return 85,  "Spending slightly lower vs last month"
    elif change_pct <= 10:
        return 65,  f"Spending up {change_pct:.0f}% vs last month"
    elif change_pct <= 25:
        return 40,  f"Spending up {change_pct:.0f}% vs last month - review"
    else:
        return 15,  f"Spending increased significantly ({change_pct:.0f}%) vs last month"


def _score_budget_adherence(utilization, budget_set):
    if not budget_set:
        return 40, "No monthly budget set - set a budget to track adherence"
    if utilization <= 70:
        return 100, f"Well within budget ({utilization:.0f}% used)"
    elif utilization <= 85:
        return 75,  f"Budget utilization at {utilization:.0f}% - monitor spending"
    elif utilization <= 100:
        return 40,  f"Budget utilization at {utilization:.0f}% - near limit"
    else:
        return 0,   f"Budget exceeded by {utilization - 100:.0f}%"


def _score_emergency_fund(balance, target):
    if target <= 0:
        return 60, "Not enough transaction history to estimate emergency fund target"
    ratio = (balance / target) * 100
    if ratio >= 100:
        return 100, "Emergency fund fully funded (6+ months of expenses)"
    elif ratio >= 50:
        return 65,  f"Emergency fund at {ratio:.0f}% of target (3+ months)"
    elif ratio >= 25:
        return 35,  f"Emergency fund at {ratio:.0f}% of target - prioritize building it"
    else:
        return 10,  "Emergency fund very low - aim for 3-6 months of expenses"


def _score_debt(debt_to_income, has_debt):
    if not has_debt:
        return 100, "No tracked debt - great position"
    if debt_to_income <= 20:
        return 90,  f"Debt-to-income ratio {debt_to_income:.0f}% - healthy"
    elif debt_to_income <= 40:
        return 65,  f"Debt-to-income ratio {debt_to_income:.0f}% - manageable but watch EMIs"
    elif debt_to_income <= 60:
        return 35,  f"Debt-to-income ratio {debt_to_income:.0f}% - consider debt reduction"
    else:
        return 10,  f"High debt-to-income ratio ({debt_to_income:.0f}%) - prioritize payoff"


def _score_investments(investment_count, total_invested, monthly_income):
    if investment_count == 0:
        return 20, "No tracked investments - consider starting a SIP or FD"
    if monthly_income > 0:
        inv_rate = (total_invested / monthly_income) * 100
        if inv_rate >= 20:
            return 100, "Strong investment portfolio relative to income"
        elif inv_rate >= 10:
            return 75,  "Good investment activity"
        else:
            return 50,  "Investing, but consider increasing allocation"
    return 60, f"{investment_count} investment(s) tracked"


def _score_goals(goals):
    if not goals:
        return 30, "No financial goals set - create goals to stay motivated"
    avg_progress = sum(g["progress_pct"] for g in goals) / len(goals)
    if avg_progress >= 75:
        return 100, f"Goals on track - avg {avg_progress:.0f}% progress"
    elif avg_progress >= 50:
        return 75,  f"Goals progressing - avg {avg_progress:.0f}% progress"
    elif avg_progress >= 25:
        return 50,  f"Goals at {avg_progress:.0f}% avg - increase contributions"
    else:
        return 20,  f"Goals at {avg_progress:.0f}% avg - consistent contributions needed"


def compute_health_score(profile: dict) -> dict:
    """Compute the Financial Health Score from a financial profile dict."""
    s_savings,   e_savings   = _score_savings_rate(profile["savings_rate"])
    s_expense,   e_expense   = _score_expense_control(profile["this_month_expenses"], profile["last_month_expenses"])
    s_budget,    e_budget    = _score_budget_adherence(profile["budget_utilization"], profile["monthly_budget"] > 0)
    s_emergency, e_emergency = _score_emergency_fund(profile["balance"], profile["emergency_fund_target"])
    s_debt,      e_debt      = _score_debt(profile["debt_to_income_ratio"], profile["total_outstanding_debt"] > 0)
    s_invest,    e_invest    = _score_investments(profile["investment_count"], profile["total_invested"], profile["this_month_income"])
    s_goals,     e_goals     = _score_goals(profile["goals"])

    raw = {
        "savings_rate":    s_savings,
        "expense_control": s_expense,
        "budget_adherence":s_budget,
        "emergency_fund":  s_emergency,
        "debt_burden":     s_debt,
        "investment":      s_invest,
        "goal_progress":   s_goals,
    }
    total_score = round(sum(raw[k] * WEIGHTS[k] / 100 for k in WEIGHTS), 1)

    if total_score >= 80:
        grade, grade_color = "Excellent", "success"
    elif total_score >= 65:
        grade, grade_color = "Good", "primary"
    elif total_score >= 50:
        grade, grade_color = "Fair", "warning"
    else:
        grade, grade_color = "Needs Attention", "danger"

    exps = [e_savings, e_expense, e_budget, e_emergency, e_debt, e_invest, e_goals]
    names = ["Savings Rate", "Expense Control", "Budget Adherence", "Emergency Fund", "Debt Burden", "Investment", "Goal Progress"]
    scores = [s_savings, s_expense, s_budget, s_emergency, s_debt, s_invest, s_goals]

    strengths, risks, actions = [], [], []
    for name, score, exp in zip(names, scores, exps):
        if score >= 75:
            strengths.append({"name": name, "score": score, "explanation": exp})
        elif score < 50:
            risks.append({"name": name, "score": score, "explanation": exp})
            if len(actions) < 3:
                actions.append(f"Improve {name}: {exp}")

    if not actions:
        actions = ["Keep maintaining your excellent financial habits!"]

    keys = list(WEIGHTS.keys())
    return {
        "total_score": total_score,
        "grade": grade,
        "grade_color": grade_color,
        "component_scores": {
            keys[i]: {"score": scores[i], "explanation": exps[i], "weight": WEIGHTS[keys[i]]}
            for i in range(len(keys))
        },
        "strengths": strengths,
        "risks": risks,
        "recommended_actions": actions,
    }
