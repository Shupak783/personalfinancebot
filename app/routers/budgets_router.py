import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.budgeting import budget_status, get_or_create_category
from app.db import get_db

router = APIRouter(prefix="/budgets", tags=["budgets"])


class BudgetSetIn(BaseModel):
    category_name: str
    monthly_budget_dollars: float


@router.get("")
def get_budget_status(year: int | None = None, month: int | None = None, db: Session = Depends(get_db)):
    now = datetime.datetime.now(datetime.timezone.utc)
    return budget_status(db, year or now.year, month or now.month)


@router.post("")
def set_budget(payload: BudgetSetIn, db: Session = Depends(get_db)):
    category = get_or_create_category(db, payload.category_name)
    category.monthly_budget_cents = round(payload.monthly_budget_dollars * 100)
    db.commit()
    return {"category": category.name, "monthly_budget_cents": category.monthly_budget_cents}
