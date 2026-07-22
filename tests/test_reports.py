import datetime

from app.models import Account, Category, Transaction
from app.reports import category_spend_over_period, render_category_bar_chart


def test_category_spend_over_period_ranks_by_spend_descending(db_session):
    account = Account(name="Checking", type="depository")
    db_session.add(account)
    db_session.flush()

    dining = Category(name="Dining")
    groceries = Category(name="Groceries")
    db_session.add_all([dining, groceries])
    db_session.flush()

    now = datetime.datetime.now(datetime.timezone.utc)
    db_session.add_all(
        [
            Transaction(account_id=account.id, category_id=dining.id, amount_cents=2000, date=now, description="a"),
            Transaction(account_id=account.id, category_id=groceries.id, amount_cents=5000, date=now, description="b"),
            # income should be excluded from spend ranking
            Transaction(account_id=account.id, category_id=groceries.id, amount_cents=-9999, date=now, description="refund"),
        ]
    )
    db_session.commit()

    start = now - datetime.timedelta(days=1)
    end = now + datetime.timedelta(days=1)
    result = category_spend_over_period(db_session, start, end)

    assert result[0]["category"] == "Groceries"
    assert result[0]["spent_cents"] == 5000
    assert result[1]["category"] == "Dining"


def test_category_spend_over_period_excludes_transactions_outside_window(db_session):
    account = Account(name="Checking", type="depository")
    db_session.add(account)
    db_session.flush()
    category = Category(name="Dining")
    db_session.add(category)
    db_session.flush()

    old_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
    db_session.add(
        Transaction(account_id=account.id, category_id=category.id, amount_cents=1500, date=old_date, description="old")
    )
    db_session.commit()

    now = datetime.datetime.now(datetime.timezone.utc)
    result = category_spend_over_period(db_session, now - datetime.timedelta(days=7), now)
    assert result == []


def test_category_spend_falls_back_to_uncategorized_label(db_session):
    account = Account(name="Checking", type="depository")
    db_session.add(account)
    db_session.flush()
    now = datetime.datetime.now(datetime.timezone.utc)
    db_session.add(
        Transaction(account_id=account.id, category_id=None, amount_cents=1200, date=now, description="mystery")
    )
    db_session.commit()

    result = category_spend_over_period(db_session, now - datetime.timedelta(days=1), now + datetime.timedelta(days=1))
    assert result == [{"category": "Uncategorized", "spent_cents": 1200}]


def test_render_category_bar_chart_produces_valid_png():
    chart_bytes = render_category_bar_chart([{"category": "Dining", "spent_cents": 4200}])
    assert chart_bytes[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic number
