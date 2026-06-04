"""
Credit Underwriting Engine - Core Risk Logic
============================================
Simulates real-world bank underwriting decisions using
industry-standard metrics: DTI, LTV, credit score bands,
and collateral evaluation.
"""

# ─── Risk Band Thresholds ────────────────────────────────────────────────────
CREDIT_SCORE_BANDS = {
    "excellent": 750,
    "good": 700,
    "fair": 650,
    "poor": 0,
}

DTI_THRESHOLDS = {
    "low": 0.20,
    "moderate": 0.36,
    "high": 0.43,
}

LTV_THRESHOLDS = {
    "low": 0.60,
    "moderate": 0.80,
}


# ─── Individual Scoring Modules ──────────────────────────────────────────────

def score_credit(credit_score: int) -> tuple[int, str]:
    """Score based on FICO credit score bands."""
    if credit_score >= CREDIT_SCORE_BANDS["excellent"]:
        return 10, "Excellent credit history"
    elif credit_score >= CREDIT_SCORE_BANDS["good"]:
        return 20, "Good credit history"
    elif credit_score >= CREDIT_SCORE_BANDS["fair"]:
        return 35, "Fair credit – moderate risk"
    else:
        return 55, "Poor credit – high default risk"


def score_dti(income: float, existing_debt: float, loan_amount: float, loan_duration_months: int) -> tuple[int, str]:
    """
    Debt-to-Income Ratio scoring.
    DTI = (existing monthly debt + proposed EMI) / monthly income
    """
    monthly_income = income / 12
    emi = loan_amount / loan_duration_months
    total_monthly_debt = (existing_debt / 12) + emi
    dti = total_monthly_debt / monthly_income if monthly_income > 0 else 1.0

    if dti <= DTI_THRESHOLDS["low"]:
        return 5, f"Low DTI ({dti:.1%}) – excellent repayment capacity"
    elif dti <= DTI_THRESHOLDS["moderate"]:
        return 15, f"Moderate DTI ({dti:.1%}) – manageable debt load"
    elif dti <= DTI_THRESHOLDS["high"]:
        return 25, f"High DTI ({dti:.1%}) – near repayment limits"
    else:
        return 40, f"Critical DTI ({dti:.1%}) – exceeds safe threshold"


def score_ltv(loan_amount: float, collateral_value: float) -> tuple[int, str]:
    """
    Loan-to-Value ratio (collateral evaluation).
    Lower LTV = better secured lending.
    """
    if collateral_value <= 0:
        return 20, "No collateral – unsecured loan, higher risk"
    ltv = loan_amount / collateral_value
    if ltv <= LTV_THRESHOLDS["low"]:
        return 0, f"Low LTV ({ltv:.1%}) – well-secured collateral"
    elif ltv <= LTV_THRESHOLDS["moderate"]:
        return 10, f"Moderate LTV ({ltv:.1%}) – adequate collateral"
    else:
        return 20, f"High LTV ({ltv:.1%}) – under-collateralized"


def score_employment(employment_years: float) -> tuple[int, str]:
    """Employment stability scoring."""
    if employment_years >= 5:
        return 0, "Stable employment (5+ years)"
    elif employment_years >= 2:
        return 10, "Moderate employment stability (2–5 years)"
    elif employment_years >= 1:
        return 20, "Limited employment history (1–2 years)"
    else:
        return 30, "Insufficient employment history (<1 year)"


def score_income_adequacy(income: float, loan_amount: float) -> tuple[int, str]:
    """Income-to-loan adequacy check."""
    ratio = loan_amount / income if income > 0 else 99
    if ratio <= 0.3:
        return 0, "Loan well within income range"
    elif ratio <= 0.5:
        return 10, "Loan moderate relative to income"
    elif ratio <= 1.0:
        return 20, "Loan high relative to annual income"
    else:
        return 30, "Loan amount exceeds annual income – high risk"


# ─── Master Risk Calculator ───────────────────────────────────────────────────

def calculate_risk(
    income: float,
    credit_score: int,
    loan_amount: float,
    loan_duration_months: int,
    existing_debt: float,
    collateral_value: float = 0,
    employment_years: float = 3,
) -> dict:
    """
    Master underwriting function.
    Returns a full risk assessment dict with score, decision, limit, and factors.
    """
    factors = []

    # Score each dimension
    s_credit, r_credit = score_credit(credit_score)
    s_dti, r_dti = score_dti(income, existing_debt, loan_amount, loan_duration_months)
    s_ltv, r_ltv = score_ltv(loan_amount, collateral_value)
    s_emp, r_emp = score_employment(employment_years)
    s_inc, r_inc = score_income_adequacy(income, loan_amount)

    factors = [
        {"factor": "Credit Score", "score": s_credit, "detail": r_credit},
        {"factor": "Debt-to-Income Ratio", "score": s_dti, "detail": r_dti},
        {"factor": "Loan-to-Value (Collateral)", "score": s_ltv, "detail": r_ltv},
        {"factor": "Employment Stability", "score": s_emp, "detail": r_emp},
        {"factor": "Income Adequacy", "score": s_inc, "detail": r_inc},
    ]

    # Composite risk score (0–100, lower = safer)
    raw_score = s_credit + s_dti + s_ltv + s_emp + s_inc
    risk_score = min(raw_score, 100)

    # Decision engine
    decision, decision_class = make_decision(risk_score)

    # Recommended credit limit
    credit_limit = calculate_credit_limit(income, credit_score, risk_score, loan_amount)

    # Primary rejection/flag reason
    explanation = build_explanation(factors, decision)

    return {
        "risk_score": risk_score,
        "decision": decision,
        "decision_class": decision_class,   # APPROVED / REVIEW / REJECTED
        "credit_limit": credit_limit,
        "factors": factors,
        "explanation": explanation,
        "dti_monthly": _get_dti(income, existing_debt, loan_amount, loan_duration_months),
    }


# ─── Decision Engine ──────────────────────────────────────────────────────────

def make_decision(risk_score: int) -> tuple[str, str]:
    if risk_score <= 30:
        return "✅ APPROVED", "APPROVED"
    elif risk_score <= 50:
        return "🔍 MANUAL REVIEW", "REVIEW"
    elif risk_score <= 65:
        return "⚠️  CONDITIONAL", "CONDITIONAL"
    else:
        return "❌ REJECTED", "REJECTED"


def calculate_credit_limit(income: float, credit_score: int, risk_score: int, requested: float) -> float:
    """
    Calculate recommended credit limit based on income, creditworthiness, and risk.
    Standard bank formula: base limit × credit multiplier × risk modifier.
    """
    base = income * 0.35          # Max 35% of annual income
    credit_multiplier = (credit_score / 850) * 1.5
    risk_modifier = max(0.1, 1 - (risk_score / 150))
    limit = base * credit_multiplier * risk_modifier
    return round(min(limit, requested * 1.1), 2)   # Cap at 110% of request


def build_explanation(factors: list, decision: str) -> str:
    """Build a human-readable explanation like a real underwriter would write."""
    top_risks = sorted(factors, key=lambda f: f["score"], reverse=True)[:2]
    if "APPROVED" in decision:
        primary = top_risks[0]["detail"]
        return f"Application approved. {primary}."
    elif "REVIEW" in decision:
        reasons = "; ".join(f["detail"] for f in top_risks)
        return f"Manual review required. Key concerns: {reasons}."
    elif "CONDITIONAL" in decision:
        reasons = top_risks[0]["detail"]
        return f"Conditional approval possible with co-signer or reduced loan. Risk factor: {reasons}."
    else:
        reasons = "; ".join(f["detail"] for f in top_risks)
        return f"Rejected. Primary risk factors: {reasons}."


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_dti(income, existing_debt, loan_amount, loan_duration_months):
    monthly_income = income / 12
    emi = loan_amount / loan_duration_months
    total_debt = (existing_debt / 12) + emi
    return round((total_debt / monthly_income) * 100, 1) if monthly_income > 0 else 100.0
