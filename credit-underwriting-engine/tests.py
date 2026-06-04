"""
Unit Tests — Credit Underwriting Engine
========================================
Run with: python -m pytest tests.py -v
"""

import pytest
from logic import (
    calculate_risk,
    score_credit,
    score_dti,
    score_ltv,
    score_employment,
    make_decision,
    calculate_credit_limit,
)


# ─── Unit: score_credit ───────────────────────────────────────────────────────

class TestCreditScoring:
    def test_excellent_credit(self):
        score, reason = score_credit(800)
        assert score == 10
        assert "Excellent" in reason

    def test_good_credit(self):
        score, _ = score_credit(720)
        assert score == 20

    def test_fair_credit(self):
        score, _ = score_credit(660)
        assert score == 35

    def test_poor_credit(self):
        score, _ = score_credit(580)
        assert score == 55

    def test_boundary_excellent(self):
        score, _ = score_credit(750)
        assert score == 10

    def test_boundary_good(self):
        score, _ = score_credit(700)
        assert score == 20


# ─── Unit: score_dti ─────────────────────────────────────────────────────────

class TestDTIScoring:
    def test_low_dti(self):
        # Monthly income = 10000, EMI = 500, existing monthly debt = 0
        score, reason = score_dti(120000, 0, 6000, 12)
        assert score == 5
        assert "Low DTI" in reason

    def test_high_dti(self):
        # Monthly income = 2000, heavy debt
        score, reason = score_dti(24000, 20000, 15000, 12)
        assert score == 40


# ─── Unit: score_ltv ─────────────────────────────────────────────────────────

class TestLTVScoring:
    def test_no_collateral(self):
        score, reason = score_ltv(20000, 0)
        assert score == 20
        assert "unsecured" in reason.lower()

    def test_low_ltv(self):
        score, _ = score_ltv(20000, 50000)
        assert score == 0

    def test_high_ltv(self):
        score, _ = score_ltv(20000, 21000)
        assert score == 20


# ─── Unit: make_decision ─────────────────────────────────────────────────────

class TestMakeDecision:
    def test_approved(self):
        _, dc = make_decision(25)
        assert dc == "APPROVED"

    def test_review(self):
        _, dc = make_decision(45)
        assert dc == "REVIEW"

    def test_conditional(self):
        _, dc = make_decision(60)
        assert dc == "CONDITIONAL"

    def test_rejected(self):
        _, dc = make_decision(80)
        assert dc == "REJECTED"

    def test_boundary_approved(self):
        _, dc = make_decision(30)
        assert dc == "APPROVED"

    def test_boundary_rejected(self):
        _, dc = make_decision(66)
        assert dc == "REJECTED"


# ─── Integration: full risk pipeline ─────────────────────────────────────────

class TestFullRiskCalculation:
    def test_strong_applicant_approved(self):
        result = calculate_risk(
            income=120000,
            credit_score=800,
            loan_amount=20000,
            loan_duration_months=36,
            existing_debt=3000,
            collateral_value=60000,
            employment_years=10,
        )
        assert result["decision_class"] == "APPROVED"
        assert result["risk_score"] <= 30
        assert result["credit_limit"] > 0

    def test_weak_applicant_rejected(self):
        result = calculate_risk(
            income=20000,
            credit_score=550,
            loan_amount=19000,
            loan_duration_months=60,
            existing_debt=18000,
            collateral_value=0,
            employment_years=0.5,
        )
        assert result["decision_class"] in ("REJECTED", "CONDITIONAL")
        assert result["risk_score"] > 50

    def test_result_structure(self):
        result = calculate_risk(50000, 700, 20000, 36, 8000)
        required_keys = ["risk_score", "decision", "decision_class",
                         "credit_limit", "factors", "explanation", "dti_monthly"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_risk_score_bounds(self):
        result = calculate_risk(50000, 700, 20000, 36, 8000)
        assert 0 <= result["risk_score"] <= 100

    def test_credit_limit_non_negative(self):
        result = calculate_risk(25000, 580, 20000, 60, 18000)
        assert result["credit_limit"] >= 0

    def test_five_factors_always_returned(self):
        result = calculate_risk(50000, 700, 20000, 36, 8000)
        assert len(result["factors"]) == 5

    def test_explanation_non_empty(self):
        result = calculate_risk(50000, 700, 20000, 36, 8000)
        assert len(result["explanation"]) > 10


# ─── Edge Cases ───────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_zero_income(self):
        """Should not crash; high risk score expected."""
        result = calculate_risk(
            income=1,  # near-zero to avoid division by zero
            credit_score=600,
            loan_amount=10000,
            loan_duration_months=36,
            existing_debt=5000,
        )
        assert result["risk_score"] >= 0

    def test_zero_loan_amount(self):
        """Very small loan with good credit should be low risk (APPROVED or REVIEW)."""
        result = calculate_risk(
            income=80000,
            credit_score=750,
            loan_amount=1,
            loan_duration_months=12,
            existing_debt=0,
        )
        assert result["decision_class"] in ("APPROVED", "REVIEW")
        assert result["risk_score"] <= 50

    def test_max_credit_score(self):
        score, _ = score_credit(850)
        assert score == 10

    def test_minimum_credit_score(self):
        score, _ = score_credit(300)
        assert score == 55
