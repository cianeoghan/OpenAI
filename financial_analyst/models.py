from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Transaction:
    posted_date: date
    description: str
    amount: Decimal
    account: str
    category: str

    @property
    def is_income(self) -> bool:
        return self.amount > 0


@dataclass(frozen=True)
class AccountBalance:
    account: str
    account_type: str
    balance: Decimal


@dataclass(frozen=True)
class MonthlySummary:
    month: str
    income: Decimal
    expenses: Decimal
    net: Decimal
    savings_rate: Optional[Decimal]
