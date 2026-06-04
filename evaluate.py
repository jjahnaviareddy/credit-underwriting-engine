"""
Single Applicant Evaluator
===========================
Interactive CLI for evaluating one customer at a time.
Perfect for demo use during interviews.

Usage:
    python evaluate.py
"""

from logic import calculate_risk

GREEN  = "\033[92m"
YELLOW = "\033[93m"
ORANGE = "\033[38;5;208m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

SAMPLE_PROFILES = {
    "1": {
        "name": "High-Value Customer",
        "income": 120000, "credit_score": 780, "loan_amount": 30000,
        "loan_duration_months": 36, "existing_debt": 5000,
        "collateral_value": 60000, "employment_years": 8,
    },
    "2": {
        "name": "Average Applicant",
        "income": 55000, "credit_score": 690, "loan_amount": 22000,
        "loan_duration_months": 48, "existing_debt": 12000,
        "collateral_value": 20000, "employment_years": 4,
    },
    "3": {
        "name": "High-Risk Customer",
        "income": 28000, "credit_score": 590, "loan_amount": 18000,
        "loan_duration_months": 60, "existing_debt": 16000,
        "collateral_value": 0, "employment_years": 0.5,
    },
}


def get_input(prompt, cast=float, default=None):
    try:
        val = input(f"  {prompt}: ").strip()
        if not val and default is not None:
            return default
        return cast(val)
    except (ValueError, KeyboardInterrupt):
        if default is not None:
            return default
        raise


def print_result(result: dict, name: str = "Applicant"):
    dec = result["decision_class"]
    colors = {"APPROVED": GREEN, "REVIEW": YELLOW, "CONDITIONAL": ORANGE, "REJECTED": RED}
    col = colors.get(dec, RESET)

    print(f"\n{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}  UNDERWRITING REPORT: {name}{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")

    for f in result["factors"]:
        bar = "▓" * min(f["score"] // 5, 10) + "░" * (10 - min(f["score"] // 5, 10))
        print(f"  {f['factor']:<30} [{bar}]")
        print(f"  {' '*32} {f['detail']}")

    print()
    print(f"  {'Risk Score':<20}: {result['risk_score']}/100")
    print(f"  {'DTI Ratio':<20}: {result['dti_monthly']}%")
    print(f"  {'Credit Limit':<20}: ₹{result['credit_limit']:,.2f}")
    print(f"\n  {'DECISION':<20}: {col}{BOLD}{result['decision']}{RESET}")
    print(f"  {result['explanation']}")
    print(f"{CYAN}{'─'*60}{RESET}\n")


def run_interactive():
    print(f"\n{CYAN}{BOLD}  CREDIT UNDERWRITING EVALUATOR{RESET}")
    print(f"{CYAN}  Enter applicant details or choose a preset profile.{RESET}\n")

    print("  Load a preset? (saves time for demos)")
    for k, v in SAMPLE_PROFILES.items():
        print(f"    [{k}] {v['name']}")
    print("    [0] Enter manually")

    choice = input("\n  Your choice: ").strip()

    if choice in SAMPLE_PROFILES:
        p = SAMPLE_PROFILES[choice]
        name = p["name"]
        result = calculate_risk(
            income=p["income"],
            credit_score=p["credit_score"],
            loan_amount=p["loan_amount"],
            loan_duration_months=p["loan_duration_months"],
            existing_debt=p["existing_debt"],
            collateral_value=p["collateral_value"],
            employment_years=p["employment_years"],
        )
        print_result(result, name)
    else:
        print()
        name = input("  Applicant Name: ").strip() or "Applicant"
        income = get_input("Annual Income (₹)", float)
        credit_score = get_input("Credit Score (300-850)", int)
        loan_amount = get_input("Loan Amount Requested (₹)", float)
        loan_duration = get_input("Loan Duration (months)", int, 36)
        existing_debt = get_input("Existing Annual Debt (₹)", float, 0)
        collateral = get_input("Collateral Value (₹, 0 if none)", float, 0)
        employment = get_input("Years Employed", float, 3)

        result = calculate_risk(
            income=income,
            credit_score=credit_score,
            loan_amount=loan_amount,
            loan_duration_months=loan_duration,
            existing_debt=existing_debt,
            collateral_value=collateral,
            employment_years=employment,
        )
        print_result(result, name)


if __name__ == "__main__":
    run_interactive()
