import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.budgeting import budget_status, net_cash_position_cents, total_cash_cents, total_credit_owed_cents
from app.db import get_db
from app.models import Account, Nudge, Transaction

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    now = datetime.datetime.now(datetime.timezone.utc)
    context = {
        "request": request,
        "accounts": db.query(Account).all(),
        "total_cash_cents": total_cash_cents(db),
        "total_credit_owed_cents": total_credit_owed_cents(db),
        "net_cash_position_cents": net_cash_position_cents(db),
        "budgets": budget_status(db, now.year, now.month),
        "recent_transactions": db.query(Transaction).order_by(Transaction.date.desc()).limit(15).all(),
        "nudges": db.query(Nudge).filter(Nudge.acknowledged.is_(False)).order_by(Nudge.created_at.desc()).all(),
        "month_label": now.strftime("%B %Y"),
    }
    return templates.TemplateResponse("dashboard.html", context)
