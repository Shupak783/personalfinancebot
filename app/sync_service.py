import datetime

from sqlalchemy.orm import Session

from app import plaid_client
from app.budgeting import get_or_create_category, suggest_category
from app.models import Account, PlaidItem, Transaction


def refresh_account_balances(db: Session, item: PlaidItem) -> None:
    plaid_accounts = plaid_client.get_accounts(item.access_token)
    for pa in plaid_accounts:
        account = db.query(Account).filter(Account.plaid_account_id == pa.account_id).one_or_none()
        balances = pa.balances
        current_cents = round((balances.current or 0) * 100)
        available_cents = round(balances.available * 100) if balances.available is not None else None
        if account is None:
            account = Account(
                plaid_item_id=item.id,
                plaid_account_id=pa.account_id,
                name=pa.name,
                official_name=pa.official_name,
                type=str(pa.type),
                subtype=str(pa.subtype) if pa.subtype else None,
                mask=pa.mask,
                current_balance_cents=current_cents,
                available_balance_cents=available_cents,
            )
            db.add(account)
        else:
            account.current_balance_cents = current_cents
            account.available_balance_cents = available_cents
    db.flush()


def sync_item_transactions(db: Session, item: PlaidItem) -> dict:
    added, modified, removed_ids, next_cursor = plaid_client.sync_transactions(item.access_token, item.cursor)
    item.cursor = next_cursor

    for t in [*added, *modified]:
        account = db.query(Account).filter(Account.plaid_account_id == t.account_id).one_or_none()
        if account is None:
            continue  # account will appear after refresh_account_balances runs
        existing = (
            db.query(Transaction).filter(Transaction.plaid_transaction_id == t.transaction_id).one_or_none()
        )
        amount_cents = round(t.amount * 100)
        category_name = suggest_category(t.name, t.merchant_name)
        category = get_or_create_category(db, category_name, is_income=amount_cents < 0)
        date_value = datetime.datetime.combine(t.date, datetime.time(), tzinfo=datetime.timezone.utc)

        if existing is None:
            db.add(
                Transaction(
                    account_id=account.id,
                    category_id=category.id,
                    plaid_transaction_id=t.transaction_id,
                    amount_cents=amount_cents,
                    date=date_value,
                    merchant_name=t.merchant_name,
                    description=t.name,
                    pending=t.pending,
                    is_manual=False,
                )
            )
        else:
            existing.amount_cents = amount_cents
            existing.date = date_value
            existing.merchant_name = t.merchant_name
            existing.description = t.name
            existing.pending = t.pending

    if removed_ids:
        db.query(Transaction).filter(Transaction.plaid_transaction_id.in_(removed_ids)).delete(
            synchronize_session=False
        )

    db.flush()
    return {"added": len(added), "modified": len(modified), "removed": len(removed_ids)}


def sync_all_items(db: Session) -> list[dict]:
    results = []
    for item in db.query(PlaidItem).all():
        refresh_account_balances(db, item)
        stats = sync_item_transactions(db, item)
        results.append({"item_id": item.item_id, **stats})
    db.commit()
    return results
