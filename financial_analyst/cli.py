from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import FinancialAnalyst


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Financial analyst for statements and budgets")
    parser.add_argument("--transactions", type=Path, required=True, help="CSV file with transactions")
    parser.add_argument("--balances", type=Path, required=True, help="CSV file with account balances")
    parser.add_argument("--category-rules", type=Path, help="JSON file with category keyword rules")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"), help="Output directory for reports")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    category_rules = None
    if args.category_rules:
        category_rules = FinancialAnalyst.load_category_rules(args.category_rules)

    analyst = FinancialAnalyst(category_rules=category_rules)
    transactions = analyst.load_transactions(args.transactions)
    balances = analyst.load_balances(args.balances)

    wealth_report = analyst.build_wealth_report(balances)
    monthly_summaries = analyst.monthly_cash_flow(transactions)
    budget_assessment = analyst.budget_assessment(transactions)
    opportunities = analyst.improvement_opportunities(transactions)

    output_dir = args.output_dir
    analyst.export_report(output_dir / "financial_report.json", wealth_report, monthly_summaries, budget_assessment, opportunities)
    analyst.build_budget_plan(monthly_summaries, output_dir / "budget_plan.csv")
    analyst.build_management_tracker(monthly_summaries, output_dir / "management_tracker.csv")


if __name__ == "__main__":
    main()
