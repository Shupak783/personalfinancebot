import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.budgeting import (
    budget_status,
    detect_recurring_bills,
    net_cash_position_cents,
    total_cash_cents,
    total_credit_owed_cents,
)
from app.db import get_db
from app.models import Account, Category, Nudge, Transaction

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(request: Request, category: str | None = None, db: Session = Depends(get_db)):
    now = datetime.datetime.now(datetime.timezone.utc)

    txn_query = db.query(Transaction).order_by(Transaction.date.desc())
    if category:
        txn_query = txn_query.join(Transaction.category).filter(Category.name == category)
        recent_transactions = txn_query.limit(200).all()
    else:
        recent_transactions = txn_query.limit(15).all()

    context = {
        "accounts": db.query(Account).all(),
        "total_cash_cents": total_cash_cents(db),
        "total_credit_owed_cents": total_credit_owed_cents(db),
        "net_cash_position_cents": net_cash_position_cents(db),
        "budgets": budget_status(db, now.year, now.month),
        "recent_transactions": recent_transactions,
        "filter_category": category,
        "nudges": db.query(Nudge).filter(Nudge.acknowledged.is_(False)).order_by(Nudge.created_at.desc()).all(),
        "month_label": now.strftime("%B %Y"),
        "recurring_bills": detect_recurring_bills(db),
    }
    return templates.TemplateResponse(request, "dashboard.html", context)
