# Credit Underwriting Decision Engine

> A production-grade automated loan underwriting system simulating real-world bank credit analysis pipelines used at institutions like JPMorgan Chase, HDFC Bank, and Goldman Sachs.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=flat-square)
![Tests](https://img.shields.io/badge/Tests-24%20passing-00e6a0?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What This Project Does

This engine takes a customer's financial profile as input and outputs a fully reasoned loan decision — exactly the workflow a credit analyst performs manually, automated and codified into a rule-based decision engine.

**Input:**
- Annual income, credit score, existing debt
- Loan amount, duration, collateral value
- Employment history

**Output:**
- `APPROVED / MANUAL REVIEW / CONDITIONAL / REJECTED`
- Risk score (0–100, lower = safer)
- Recommended credit limit
- Human-readable decision explanation ("Rejected due to high DTI and insufficient collateral")

---

## Project Structure

```
credit-underwriting-engine/
│
├── logic.py          # Core risk engine: scoring, DTI, LTV, collateral
├── main.py           # Batch processor — runs full CSV through the engine
├── evaluate.py       # Interactive single-applicant evaluator (demo-ready)
├── tests.py          # 24 unit + integration tests (pytest)
├── data.csv          # 12 diverse sample applicants
├── dashboard.html    # Interactive web dashboard (open in any browser)
└── README.md
```

---

## Underwriting Logic

### Five Risk Dimensions

| Dimension | Weight (max) | What it Measures |
|---|---|---|
| Credit Score | 55 pts | FICO band: Excellent / Good / Fair / Poor |
| Debt-to-Income Ratio | 40 pts | (Monthly debt + EMI) / Monthly income |
| Loan-to-Value (LTV) | 20 pts | Loan amount vs. collateral value |
| Employment Stability | 30 pts | Years in current employment |
| Income Adequacy | 30 pts | Loan amount as % of annual income |

### Decision Thresholds

| Risk Score | Decision | Meaning |
|---|---|---|
| 0 – 30 | ✅ APPROVED | Strong credit profile, proceed |
| 31 – 50 | 🔍 MANUAL REVIEW | Borderline — needs human analyst |
| 51 – 65 | ⚠️ CONDITIONAL | May proceed with co-signer or reduced amount |
| 66 – 100 | ❌ REJECTED | Too risky — high default probability |

### DTI Thresholds (Industry Standard)

```
DTI ≤ 20%   →  Low risk    (standard for prime borrowers)
DTI 20–36%  →  Moderate    (acceptable for most banks)
DTI 36–43%  →  High        (near CFPB qualified mortgage limit)
DTI > 43%   →  Critical    (exceeds most lenders' hard cap)
```

### Credit Limit Formula

```python
base         = annual_income × 0.35
credit_mult  = (credit_score / 850) × 1.5
risk_mod     = max(0.1, 1 - risk_score / 150)
credit_limit = min(base × credit_mult × risk_mod, requested_amount × 1.1)
```

---

## Setup & Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/credit-underwriting-engine.git
cd credit-underwriting-engine

# 2. Install dependencies
pip install pandas pytest

# 3. Run the batch processor on sample data
python main.py

# 4. Export results to CSV
python main.py --export

# 5. Interactive single-applicant evaluator
python evaluate.py

# 6. Run unit tests
python -m pytest tests.py -v
```

---

## Sample Output

```
════════════════════════════════════════════════════════════════════════
              CREDIT UNDERWRITING DECISION ENGINE
          Simulating JPMorgan-Level Loan Assessment
════════════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────────
  #1  Arjun Sharma
────────────────────────────────────────────────────────────────────────
  Annual Income   :  ₹      85,000
  Credit Score    :  760
  Loan Requested  :  ₹      25,000  (36mo)
  Existing Debt   :  ₹       8,000
  Collateral      :  ₹      40,000
  Employment      :  7 years

  Risk Factor Breakdown:
  Credit Score                  [▓▓░░░░░░░░]  Excellent credit history
  Debt-to-Income Ratio          [▓▓▓░░░░░░░]  Moderate DTI (22.4%)
  Loan-to-Value (Collateral)    [░░░░░░░░░░]  Low LTV (62.5%)
  Employment Stability          [░░░░░░░░░░]  Stable employment (5+ years)
  Income Adequacy               [▓▓░░░░░░░░]  Loan within income range

  DTI Ratio     :  22.4%
  Risk Score    :  25/100  →  ██████████ Minimal
  Credit Limit  :  ₹27,059.12

  Decision      :  ✅ APPROVED
  Reason        :  Application approved. Excellent credit history.
```

---

## Web Dashboard

Open `dashboard.html` in any browser for a fully interactive underwriting UI:

- Real-time risk scoring as you adjust inputs
- Visual risk score ring with animated fill
- Factor-by-factor breakdown with progress bars
- Evaluation history to compare applicants side-by-side
- Three preset profiles: Prime / Standard / Subprime

No server needed — pure HTML/CSS/JavaScript, runs fully in-browser.

---

## Running Tests

```bash
python -m pytest tests.py -v
```

```
tests.py::TestCreditScoring::test_excellent_credit         PASSED
tests.py::TestCreditScoring::test_boundary_excellent       PASSED
tests.py::TestDTIScoring::test_low_dti                     PASSED
tests.py::TestLTVScoring::test_no_collateral               PASSED
tests.py::TestMakeDecision::test_approved                  PASSED
tests.py::TestMakeDecision::test_rejected                  PASSED
tests.py::TestFullRiskCalculation::test_strong_approved    PASSED
tests.py::TestFullRiskCalculation::test_weak_rejected      PASSED
tests.py::TestEdgeCases::test_zero_income                  PASSED
...

24 passed in 0.12s
```

---

## Custom CSV Format

To run the engine on your own data, create a CSV with these columns:

```csv
Name,Income,CreditScore,LoanAmount,LoanDuration,ExistingDebt,CollateralValue,EmploymentYears
John Doe,75000,720,25000,36,8000,35000,5
```

Then run:

```bash
python main.py --file your_data.csv --export
```

---

## Real-World Relevance

This project replicates the exact workflow used in:

| Bank Workflow | This Project |
|---|---|
| Analyst pulls credit bureau data | `CreditScore` input |
| Calculates monthly obligations | `score_dti()` function |
| Checks collateral coverage | `score_ltv()` function |
| Verifies employment stability | `score_employment()` function |
| Issues approval/decline letter | `build_explanation()` function |
| Sets credit limit | `calculate_credit_limit()` function |

---

## Tech Stack

- **Python 3.9+** — core engine
- **Pandas** — batch data processing
- **pytest** — unit + integration testing
- **HTML/CSS/JS** — interactive web dashboard (no framework)

---

## Skills Demonstrated

- Financial domain knowledge (DTI, LTV, FICO, EMI)
- Rule-based decision engine design
- Modular, testable Python architecture
- Data pipeline with CSV I/O
- Quantitative risk scoring formulas
- Automated underwriting logic used in real banks

---

## License

MIT — free to use, modify, and include in your portfolio.

---

*Built to demonstrate credit underwriting concepts. Not intended as financial advice or for production lending decisions.*
