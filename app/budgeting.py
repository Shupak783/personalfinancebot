import datetime
from collections import defaultdict

from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.models import Account, Category, Transaction

# Keyword -> category name, checked against merchant_name/description (case-insensitive).
# First match wins. Falls back to "Uncategorized".
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Groceries", ["grocery", "safeway", "kroger", "trader joe", "whole foods", "costco"]),
    ("Dining", ["restaurant", "starbucks", "coffee", "doordash", "uber eats", "grubhub", "chipotle"]),
    ("Transport", ["uber", "lyft", "shell", "chevron", "exxon", "gas station", "parking"]),
    ("Subscriptions", ["netflix", "spotify", "hulu", "disney+", "prime video", "apple.com/bill"]),
    ("Shopping", ["amazon", "target", "walmart", "best buy"]),
    ("Golf/Hobbies", ["golf", "pro shop", "dick's sporting", "callaway", "titleist"]),
    ("Utilities", ["electric", "water bill", "comcast", "internet", "pg&e", "utility"]),
    ("Rent/Mortgage", ["rent", "mortgage", "property management"]),
    ("Income", ["payroll", "direct deposit", "salary"]),
]

DEFAULT_CATEGORIES = [name for name, _ in CATEGORY_RULES] + ["Uncategorized"]


def suggest_category(description: str, merchant_name: str | None) -> str:
    haystack = f"{description} {merchant_name or ''}".lower()
    for category_name, keywords in CATEGORY_RULES:
        if any(kw in haystack for kw in keywords):
            return category_name
    return "Uncategorized"


def get_or_create_category(db: Session, name: str, is_income: bool = False) -> Category:
    category = db.query(Category).filter(Category.name == name).one_or_none()
    if category is None:
        category = Category(name=name, is_income=is_income)
        db.add(category)
        db.flush()
    return category


def month_bounds(year: int, month: int) -> tuple[datetime.datetime, datetime.datetime]:
    start = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)
    if month == 12:
        end = datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)
    else:
        end = datetime.datetime(year, month + 1, 1, tzinfo=datetime.timezone.utc)
    return start, end


def budget_status(db: Session, year: int, month: int) -> list[dict]:
    """Spend vs. budget per category for the given month."""
    rows = (
        db.query(Transaction)
        .filter(extract("year", Transaction.date) == year, extract("month", Transaction.date) == month)
        .all()
    )
    spent_by_category: dict[int | None, int] = defaultdict(int)
    for t in rows:
        if t.amount_cents > 0:  # expenses only
            spent_by_category[t.category_id] += t.amount_cents

    results = []
    for category in db.query(Category).filter(Category.is_income.is_(False)).all():
        spent = spent_by_category.get(category.id, 0)
        budget = category.monthly_budget_cents
        results.append(
            {
                "category": category.name,
                "spent_cents": spent,
                "budget_cents": budget,
                "remaining_cents": (budget - spent) if budget is not None else None,
                "pct_used": round(spent / budget * 100, 1) if budget else None,
                "over_budget": budget is not None and spent > budget,
            }
        )
    return sorted(results, key=lambda r: r["spent_cents"], reverse=True)


def total_cash_cents(db: Session) -> int:
    accounts = db.query(Account).filter(Account.type.in_(["depository"])).all()
    return sum(a.current_balance_cents for a in accounts)


def total_credit_owed_cents(db: Session) -> int:
    accounts = db.query(Account).filter(Account.type == "credit").all()
    return sum(a.current_balance_cents for a in accounts)


def net_cash_position_cents(db: Session) -> int:
    return total_cash_cents(db) - total_credit_owed_cents(db)


def detect_recurring_bills(db: Session, lookback_months: int = 3) -> list[dict]:
    """Flag merchants billed in at least 2 of the last N months with a stable amount -
    used so affordability checks don't ignore rent/subscriptions due next week."""
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(days=31 * lookback_months)
    rows = (
        db.query(Transaction)
        .filter(Transaction.date >= cutoff, Transaction.amount_cents > 0, Transaction.merchant_name.isnot(None))
        .all()
    )
    by_merchant: dict[str, list[Transaction]] = defaultdict(list)
    for t in rows:
        by_merchant[t.merchant_name].append(t)

    recurring = []
    for merchant, txns in by_merchant.items():
        months_seen = {(t.date.year, t.date.month) for t in txns}
        if len(months_seen) >= 2:
            avg_amount = sum(t.amount_cents for t in txns) // len(txns)
            recurring.append({"merchant": merchant, "avg_amount_cents": avg_amount, "occurrences": len(txns)})
    return sorted(recurring, key=lambda r: r["avg_amount_cents"], reverse=True)
