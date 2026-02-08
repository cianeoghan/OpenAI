from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional

from .models import AccountBalance, MonthlySummary, Transaction


class FinancialAnalyst:
    """Analyze statements and produce reports, plans, and trackers."""

    def __init__(self, category_rules: Optional[dict[str, list[str]]] = None) -> None:
        self.category_rules = category_rules or {}

    @staticmethod
    def load_category_rules(path: Path) -> dict[str, list[str]]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def load_transactions(self, path: Path) -> list[Transaction]:
        transactions: list[Transaction] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                posted_date = self._parse_date(row.get("date"))
                description = (row.get("description") or "").strip()
                amount = self._parse_decimal(row.get("amount"))
                account = (row.get("account") or "").strip()
                category = (row.get("category") or "").strip() or self._categorize(description)
                transactions.append(
                    Transaction(
                        posted_date=posted_date,
                        description=description,
                        amount=amount,
                        account=account,
                        category=category,
                    )
                )
        return transactions

    def load_balances(self, path: Path) -> list[AccountBalance]:
        balances: list[AccountBalance] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                account = (row.get("account") or "").strip()
                account_type = (row.get("account_type") or "").strip().lower()
                balance = self._parse_decimal(row.get("balance"))
                balances.append(AccountBalance(account=account, account_type=account_type, balance=balance))
        return balances

    def build_wealth_report(self, balances: Iterable[AccountBalance]) -> dict[str, Decimal]:
        assets = sum((b.balance for b in balances if b.account_type == "asset"), Decimal("0"))
        liabilities = sum((b.balance for b in balances if b.account_type == "liability"), Decimal("0"))
        net_worth = assets - liabilities
        return {
            "assets": assets,
            "liabilities": liabilities,
            "net_worth": net_worth,
        }

    def monthly_cash_flow(self, transactions: Iterable[Transaction]) -> list[MonthlySummary]:
        monthly: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"income": Decimal("0"), "expenses": Decimal("0")})
        for txn in transactions:
            month_key = txn.posted_date.strftime("%Y-%m")
            if txn.is_income:
                monthly[month_key]["income"] += txn.amount
            else:
                monthly[month_key]["expenses"] += abs(txn.amount)
        summaries: list[MonthlySummary] = []
        for month_key in sorted(monthly.keys()):
            income = monthly[month_key]["income"]
            expenses = monthly[month_key]["expenses"]
            net = income - expenses
            savings_rate = None
            if income != 0:
                savings_rate = (net / income).quantize(Decimal("0.0001"))
            summaries.append(MonthlySummary(month=month_key, income=income, expenses=expenses, net=net, savings_rate=savings_rate))
        return summaries

    def budget_assessment(self, transactions: Iterable[Transaction]) -> dict[str, Decimal]:
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for txn in transactions:
            if txn.amount < 0:
                totals[txn.category] += abs(txn.amount)
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))

    def improvement_opportunities(self, transactions: Iterable[Transaction], top_n: int = 5) -> list[dict[str, str]]:
        category_totals = self.budget_assessment(transactions)
        opportunities: list[dict[str, str]] = []
        for category, spend in list(category_totals.items())[:top_n]:
            opportunities.append(
                {
                    "category": category,
                    "spend": f"{spend}",
                    "note": "Review for potential savings or renegotiation.",
                }
            )
        return opportunities

    def build_budget_plan(self, monthly_summaries: Iterable[MonthlySummary], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["month", "planned_income", "planned_expenses", "actual_income", "actual_expenses", "notes"])
            writer.writeheader()
            for summary in monthly_summaries:
                writer.writerow(
                    {
                        "month": summary.month,
                        "planned_income": "",
                        "planned_expenses": "",
                        "actual_income": summary.income,
                        "actual_expenses": summary.expenses,
                        "notes": "",
                    }
                )

    def build_management_tracker(self, monthly_summaries: Iterable[MonthlySummary], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["month", "income", "expenses", "net", "savings_rate"])
            writer.writeheader()
            for summary in monthly_summaries:
                writer.writerow(
                    {
                        "month": summary.month,
                        "income": summary.income,
                        "expenses": summary.expenses,
                        "net": summary.net,
                        "savings_rate": summary.savings_rate or "",
                    }
                )

    def export_report(self, path: Path, wealth_report: dict[str, Decimal], monthly_summaries: Iterable[MonthlySummary],
                      budget_assessment: dict[str, Decimal], opportunities: list[dict[str, str]]) -> None:
        data = {
            "wealth_report": {key: str(value) for key, value in wealth_report.items()},
            "monthly_cash_flow": [asdict(summary) for summary in monthly_summaries],
            "budget_assessment": {key: str(value) for key, value in budget_assessment.items()},
            "improvement_opportunities": opportunities,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, default=str)

    def _categorize(self, description: str) -> str:
        description_lower = description.lower()
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        return "Uncategorized"

    @staticmethod
    def _parse_date(raw_value: Optional[str]) -> datetime.date:
        if not raw_value:
            raise ValueError("Transaction date is required.")
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(raw_value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unsupported date format: {raw_value}")

    @staticmethod
    def _parse_decimal(raw_value: Optional[str]) -> Decimal:
        if raw_value is None:
            raise ValueError("Missing numeric value")
        try:
            return Decimal(str(raw_value).replace(",", "").strip())
        except (InvalidOperation, AttributeError) as exc:
            raise ValueError(f"Invalid numeric value: {raw_value}") from exc
