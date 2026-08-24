import datetime

from app.budgeting import (
    budget_status,
    detect_recurring_bills,
    get_or_create_category,
    net_cash_position_cents,
    suggest_category,
    total_cash_cents,
    total_credit_owed_cents,
)
from app.models import Account, Transaction


def test_suggest_category_matches_known_keywords():
    assert suggest_category("COSTCO WHSE #123", None) == "Groceries"
    assert suggest_category("Uber Trip", None) == "Transport"
    assert suggest_category("Golf Galaxy - grips", None) == "Golf/Hobbies"


def test_suggest_category_matches_user_specified_merchants():
    assert suggest_category("FRESH THYME MARKET #123", None) == "Groceries"
    assert suggest_category("HAMLIN PUB 5", None) == "Dining"
    assert suggest_category("RECURRING PMT - SOME SERVICE", None) == "Subscriptions"
    assert suggest_category("PLANET FITNESS MEMBERSHIP", None) == "Subscriptions"
    assert suggest_category("AMAZON PRIME MEMBERSHIP", None) == "Subscriptions"


def test_suggest_category_gc_matches_golf_course_as_whole_word():
    assert suggest_category("STONEY CREEK GC", None) == "Golf/Hobbies"


def test_suggest_category_gc_does_not_false_positive_inside_words():
    # 'gc' appears as a substring of 'magcargo' but should not trigger Golf/Hobbies
    assert suggest_category("MAGCARGO CORP", None) != "Golf/Hobbies"


def test_suggest_category_falls_back_to_uncategorized():
    assert suggest_category("Some Totally Unknown Merchant", None) == "Uncategorized"


def _make_account(db, balance_cents=0, acct_type="depository"):
    account = Account(name="Test", type=acct_type, is_manual=True, current_balance_cents=balance_cents)
    db.add(account)
    db.flush()
    return account


def test_budget_status_tracks_spend_and_flags_over_budget(db_session):
    account = _make_account(db_session)
    category = get_or_create_category(db_session, "Dining")
    category.monthly_budget_cents = 10000  # $100
    db_session.flush()

    now = datetime.datetime.now(datetime.timezone.utc)
    db_session.add(
        Transaction(account_id=account.id, category_id=category.id, amount_cents=12000, date=now, description="x")
    )
    db_session.commit()

    results = budget_status(db_session, now.year, now.month)
    dining = next(r for r in results if r["category"] == "Dining")
    assert dining["spent_cents"] == 12000
    assert dining["remaining_cents"] == -2000
    assert dining["over_budget"] is True


def test_budget_status_ignores_income_transactions(db_session):
    account = _make_account(db_session)
    category = get_or_create_category(db_session, "Income", is_income=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    db_session.add(
        Transaction(account_id=account.id, category_id=category.id, amount_cents=-200000, date=now, description="payroll")
    )
    db_session.commit()

    results = budget_status(db_session, now.year, now.month)
    assert all(r["category"] != "Income" for r in results)  # is_income categories excluded from spend view


def test_cash_and_credit_totals(db_session):
    _make_account(db_session, balance_cents=100000, acct_type="depository")
    _make_account(db_session, balance_cents=25000, acct_type="credit")
    db_session.commit()

    assert total_cash_cents(db_session) == 100000
    assert total_credit_owed_cents(db_session) == 25000
    assert net_cash_position_cents(db_session) == 75000


def test_detect_recurring_bills_requires_at_least_two_months(db_session):
    account = _make_account(db_session)
    now = datetime.datetime.now(datetime.timezone.utc)
    last_month = now - datetime.timedelta(days=31)

    db_session.add_all(
        [
            Transaction(
                account_id=account.id, amount_cents=1599, date=now, description="Netflix", merchant_name="Netflix"
            ),
            Transaction(
                account_id=account.id,
                amount_cents=1599,
                date=last_month,
                description="Netflix",
                merchant_name="Netflix",
            ),
            Transaction(
                account_id=account.id, amount_cents=500, date=now, description="One-off", merchant_name="CornerStore"
            ),
        ]
    )
    db_session.commit()

    recurring = detect_recurring_bills(db_session)
    merchants = {r["merchant"] for r in recurring}
    assert "Netflix" in merchants
    assert "CornerStore" not in merchants
