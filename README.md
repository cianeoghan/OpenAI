# Financial Analyst Toolkit

This repository contains a lightweight financial analyst that ingests bank and credit card statements, answers queries, and produces:

1. A wealth report (assets, liabilities, net worth).
2. Monthly cash flow statements with budget assessment.
3. Areas for improvement based on top spending categories.
4. A live budget planner CSV template.
5. An ongoing management tracker CSV for progress tracking.

## Input files

### Transactions CSV
Required columns:

| column | description |
| --- | --- |
| `date` | Transaction date (YYYY-MM-DD, YYYY/MM/DD, or MM/DD/YYYY). |
| `description` | Merchant or memo text. |
| `amount` | Positive for income, negative for expenses. |
| `account` | Account name or identifier. |
| `category` | Optional. If blank, auto-categorization uses keyword rules. |

### Balances CSV
Required columns:

| column | description |
| --- | --- |
| `account` | Account name. |
| `account_type` | `asset` or `liability`. |
| `balance` | Current balance. |

### Category rules (optional)
A JSON map of category names to keyword lists. See `financial_analyst/templates/category_rules.json`.

## Usage

```bash
python -m financial_analyst.cli \
  --transactions path/to/transactions.csv \
  --balances path/to/balances.csv \
  --category-rules financial_analyst/templates/category_rules.json \
  --output-dir reports
```

## Outputs

The command produces:

- `reports/financial_report.json` with wealth report, monthly cash flow, budget assessment, and improvement opportunities.
- `reports/budget_plan.csv` for a live budget planner (fill in planned values).
- `reports/management_tracker.csv` for ongoing tracking.

## Notes

- This toolkit operates locally and expects CSV statements you export from your financial institutions.
- Keep all sensitive data local and private.
