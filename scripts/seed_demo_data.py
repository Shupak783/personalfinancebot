"""Populates a few months of fake data so you can try the dashboard/chat before linking
a real bank. Safe to run multiple times against a fresh finbot.db; not meant to run
against a database that already has real linked-bank data.

Usage: python -m scripts.seed_demo_data
"""

import datetime
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.budgeting import get_or_create_category, suggest_category  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.models import Account, Transaction  # noqa: E402

DEMO_BUDGETS = {
    "Groceries": 500,
    "Dining": 250,
    "Transport": 150,
    "Subscriptions": 60,
    "Shopping": 200,
    "Golf/Hobbies": 150,
    "Utilities": 200,
}

DEMO_TRANSACTIONS = [
    ("Trader Joe's", 62.14),
    ("Starbucks", 6.75),
    ("Shell Gas", 41.20),
    ("Netflix", 15.49),
    ("Amazon", 38.99),
    ("Golf Galaxy - new grips", 24.00),
    ("Chipotle", 12.35),
    ("Costco", 143.87),
    ("PG&E", 96.40),
    ("Uber", 18.60),
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        for name, budget in DEMO_BUDGETS.items():
            category = get_or_create_category(db, name)
            category.monthly_budget_cents = budget * 100

        account = db.query(Account).filter(Account.name == "Demo Checking").one_or_none()
        if account is None:
            account = Account(name="Demo Checking", type="depository", is_manual=True, current_balance_cents=320000)
            db.add(account)
            db.flush()

        today = datetime.date.today()
        for months_ago in range(2, -1, -1):
            total_month_index = today.year * 12 + (today.month - 1) - months_ago
            year, month = divmod(total_month_index, 12)
            month += 1

            max_day = min(27, today.day) if months_ago == 0 else 27
            for merchant, base_amount in DEMO_TRANSACTIONS:
                day = random.randint(1, max_day)
                amount = round(base_amount * random.uniform(0.8, 1.3), 2)
                category_name = suggest_category(merchant, merchant)
                category = get_or_create_category(db, category_name)
                txn_date = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc)
                db.add(
                    Transaction(
                        account_id=account.id,
                        category_id=category.id,
                        amount_cents=round(amount * 100),
                        date=txn_date,
                        merchant_name=merchant,
                        description=merchant,
                        is_manual=True,
                    )
                )

        db.commit()
        print("Seeded demo account, categories/budgets, and ~3 months of fake transactions.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
