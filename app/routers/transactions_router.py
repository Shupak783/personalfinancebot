import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.budgeting import get_or_create_category, suggest_category
from app.db import get_db
from app.models import Account, Transaction
from app.schemas import ManualTransactionIn, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()
    return [
        TransactionOut(
            id=t.id,
            date=t.date,
            description=t.description,
            merchant_name=t.merchant_name,
            amount_cents=t.amount_cents,
            category_name=t.category.name if t.category else None,
            pending=t.pending,
            is_manual=t.is_manual,
        )
        for t in rows
    ]


@router.post("", response_model=TransactionOut)
def add_manual_transaction(payload: ManualTransactionIn, db: Session = Depends(get_db)):
    if payload.account_id is not None:
        account = db.query(Account).get(payload.account_id)
    else:
        account = db.query(Account).filter(Account.is_manual.is_(True)).first()
        if account is None:
            account = Account(name="Manual/Cash", type="depository", is_manual=True)
            db.add(account)
            db.flush()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    category_name = payload.category_name or suggest_category(payload.description, None)
    category = get_or_create_category(db, category_name, is_income=payload.amount_dollars < 0)

    amount_cents = round(payload.amount_dollars * 100)
    date_value = datetime.datetime.combine(
        payload.date or datetime.date.today(), datetime.time(), tzinfo=datetime.timezone.utc
    )
    txn = Transaction(
        account_id=account.id,
        category_id=category.id,
        amount_cents=amount_cents,
        date=date_value,
        description=payload.description,
        is_manual=True,
    )
    db.add(txn)
    if account.is_manual:
        account.current_balance_cents -= amount_cents
    db.commit()
    db.refresh(txn)
    return TransactionOut(
        id=txn.id,
        date=txn.date,
        description=txn.description,
        merchant_name=txn.merchant_name,
        amount_cents=txn.amount_cents,
        category_name=category.name,
        pending=txn.pending,
        is_manual=txn.is_manual,
    )
