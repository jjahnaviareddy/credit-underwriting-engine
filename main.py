"""
Credit Underwriting Decision Engine
=====================================
Entry point — processes a CSV of applicants and prints
a formatted underwriting report to the terminal.

Usage:
    python main.py                    # uses default data.csv
    python main.py --file custom.csv  # custom file
    python main.py --export           # also saves results to output.csv
"""

import pandas as pd
import argparse
import sys
import os
from logic import calculate_risk

# ─── ANSI Colors ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
ORANGE = "\033[38;5;208m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

DECISION_COLORS = {
    "APPROVED":    GREEN,
    "REVIEW":      YELLOW,
    "CONDITIONAL": ORANGE,
    "REJECTED":    RED,
}

RISK_BARS = {
    (0,  20): "██████████ Minimal",
    (21, 35): "████████░░ Low",
    (36, 50): "██████░░░░ Moderate",
    (51, 65): "████░░░░░░ High",
    (66,100): "██░░░░░░░░ Critical",
}


def risk_bar(score: int) -> str:
    for (lo, hi), label in RISK_BARS.items():
        if lo <= score <= hi:
            return label
    return "░░░░░░░░░░ Unknown"


def color_decision(decision_class: str, text: str) -> str:
    return DECISION_COLORS.get(decision_class, RESET) + BOLD + text + RESET


def print_header():
    print(f"\n{CYAN}{BOLD}{'═' * 72}{RESET}")
    print(f"{CYAN}{BOLD}{'  CREDIT UNDERWRITING DECISION ENGINE':^72}{RESET}")
    print(f"{CYAN}{BOLD}{'  Simulating JPMorgan-Level Loan Assessment':^72}{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 72}{RESET}\n")


def print_applicant_report(row: pd.Series, result: dict, idx: int):
    name = row.get("Name", f"Applicant #{idx+1}")
    dec_class = result["decision_class"]
    col = DECISION_COLORS.get(dec_class, RESET)

    print(f"{BOLD}{'─' * 72}{RESET}")
    print(f"{BOLD}  #{idx+1}  {name}{RESET}")
    print(f"{'─' * 72}")

    # Input summary
    print(f"  {DIM}Annual Income   :{RESET}  ₹{row['Income']:>12,.0f}")
    print(f"  {DIM}Credit Score    :{RESET}  {row['CreditScore']}")
    print(f"  {DIM}Loan Requested  :{RESET}  ₹{row['LoanAmount']:>12,.0f}  ({row['LoanDuration']}mo)")
    print(f"  {DIM}Existing Debt   :{RESET}  ₹{row['ExistingDebt']:>12,.0f}")
    print(f"  {DIM}Collateral      :{RESET}  ₹{row.get('CollateralValue',0):>12,.0f}")
    print(f"  {DIM}Employment      :{RESET}  {row.get('EmploymentYears',0)} years")
    print()

    # Risk factors table
    print(f"  {BOLD}Risk Factor Breakdown:{RESET}")
    for f in result["factors"]:
        bar = "▓" * min(f["score"] // 5, 10) + "░" * max(0, 10 - f["score"] // 5)
        print(f"  {f['factor']:<30}  [{bar}]  {f['detail']}")

    print()
    print(f"  {BOLD}DTI Ratio      :{RESET}  {result['dti_monthly']}%")
    print(f"  {BOLD}Risk Score     :{RESET}  {result['risk_score']}/100  →  {risk_bar(result['risk_score'])}")
    print(f"  {BOLD}Credit Limit   :{RESET}  ₹{result['credit_limit']:,.2f}")
    print()
    print(f"  {BOLD}Decision       :{RESET}  {col}{BOLD}{result['decision']}{RESET}")
    print(f"  {BOLD}Reason         :{RESET}  {result['explanation']}")
    print()


def print_summary(df_results: pd.DataFrame):
    total = len(df_results)
    counts = df_results["DecisionClass"].value_counts()

    approved    = counts.get("APPROVED",    0)
    review      = counts.get("REVIEW",      0)
    conditional = counts.get("CONDITIONAL", 0)
    rejected    = counts.get("REJECTED",    0)

    avg_risk = df_results["RiskScore"].mean()

    print(f"\n{CYAN}{BOLD}{'═' * 72}{RESET}")
    print(f"{CYAN}{BOLD}{'  PORTFOLIO SUMMARY':^72}{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 72}{RESET}")
    print(f"  Total Applications  : {total}")
    print(f"  {GREEN}✅ Approved         : {approved}{RESET}")
    print(f"  {YELLOW}🔍 Manual Review    : {review}{RESET}")
    print(f"  {ORANGE}⚠️  Conditional      : {conditional}{RESET}")
    print(f"  {RED}❌ Rejected         : {rejected}{RESET}")
    print(f"  Average Risk Score  : {avg_risk:.1f}/100")
    print(f"  Approval Rate       : {(approved/total*100):.1f}%")
    print(f"{CYAN}{BOLD}{'═' * 72}{RESET}\n")


def process_file(filepath: str, export: bool = False):
    if not os.path.exists(filepath):
        print(f"{RED}Error: File not found → {filepath}{RESET}")
        sys.exit(1)

    df = pd.read_csv(filepath)
    print_header()

    records = []
    for idx, row in df.iterrows():
        result = calculate_risk(
            income=row["Income"],
            credit_score=row["CreditScore"],
            loan_amount=row["LoanAmount"],
            loan_duration_months=row["LoanDuration"],
            existing_debt=row["ExistingDebt"],
            collateral_value=row.get("CollateralValue", 0),
            employment_years=row.get("EmploymentYears", 3),
        )
        print_applicant_report(row, result, idx)
        records.append({
            "Name": row.get("Name", f"Applicant#{idx+1}"),
            "RiskScore": result["risk_score"],
            "Decision": result["decision"],
            "DecisionClass": result["decision_class"],
            "CreditLimit": result["credit_limit"],
            "DTI_Percent": result["dti_monthly"],
            "Explanation": result["explanation"],
        })

    df_results = pd.DataFrame(records)
    print_summary(df_results)

    if export:
        out = filepath.replace(".csv", "_results.csv")
        df_results.to_csv(out, index=False)
        print(f"  {GREEN}Results exported → {out}{RESET}\n")

    return df_results


# ─── CLI Entry ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Credit Underwriting Decision Engine"
    )
    parser.add_argument(
        "--file", default="data.csv",
        help="Path to applicant CSV (default: data.csv)"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Export results to CSV"
    )
    args = parser.parse_args()
    process_file(args.file, args.export)
