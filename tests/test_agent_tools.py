import datetime

from app.agent import (
    _tool_get_balances,
    _tool_get_budget_status,
    _tool_get_recent_transactions,
    _tool_log_transaction,
)
from app.models import Account, Transaction


def test_get_balances_reflects_cash_and_credit(db_session):
    db_session.add(Account(name="Checking", type="depository", current_balance_cents=50000))
    db_session.add(Account(name="Visa", type="credit", current_balance_cents=10000))
    db_session.commit()

    result = _tool_get_balances(db_session, {})
    assert result["total_cash_cents"] == 50000
    assert result["total_credit_owed_cents"] == 10000
    assert result["net_cash_position_cents"] == 40000


def test_log_transaction_creates_manual_account_and_updates_balance(db_session):
    result = _tool_log_transaction(db_session, {"amount_dollars": 85.0, "description": "Costco run"})

    assert result["logged"] is True
    assert result["amount_cents"] == 8500

    account = db_session.query(Account).filter(Account.is_manual.is_(True)).one()
    assert account.current_balance_cents == -8500  # no prior balance, expense logged

    txn = db_session.query(Transaction).one()
    assert txn.description == "Costco run"
    assert txn.category is not None


def test_log_transaction_income_is_negative_amount(db_session):
    _tool_log_transaction(db_session, {"amount_dollars": -2000.0, "description": "Paycheck"})

    txn = db_session.query(Transaction).one()
    assert txn.amount_cents == -200000
    assert txn.category.is_income is True


def test_get_budget_status_tool_uses_current_month_by_default(db_session):
    from app.budgeting import get_or_create_category

    account = Account(name="Checking", type="depository")
    db_session.add(account)
    db_session.flush()
    category = get_or_create_category(db_session, "Dining")
    category.monthly_budget_cents = 5000
    now = datetime.datetime.now(datetime.timezone.utc)
    db_session.add(
        Transaction(account_id=account.id, category_id=category.id, amount_cents=3000, date=now, description="x")
    )
    db_session.commit()

    result = _tool_get_budget_status(db_session, {})
    dining = next(c for c in result["categories"] if c["category"] == "Dining")
    assert dining["spent_cents"] == 3000


def test_get_recent_transactions_filters_by_category(db_session):
    from app.budgeting import get_or_create_category

    account = Account(name="Checking", type="depository")
    db_session.add(account)
    db_session.flush()
    dining = get_or_create_category(db_session, "Dining")
    groceries = get_or_create_category(db_session, "Groceries")
    now = datetime.datetime.now(datetime.timezone.utc)
    db_session.add_all(
        [
            Transaction(account_id=account.id, category_id=dining.id, amount_cents=1000, date=now, description="a"),
            Transaction(account_id=account.id, category_id=groceries.id, amount_cents=2000, date=now, description="b"),
        ]
    )
    db_session.commit()

    result = _tool_get_recent_transactions(db_session, {"category_name": "Dining"})
    assert len(result["transactions"]) == 1
    assert result["transactions"][0]["category"] == "Dining"
