from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import plaid_client, sync_service
from app.db import get_db
from app.models import PlaidItem

router = APIRouter(prefix="/plaid", tags=["plaid"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/link")
def link_page(request: Request):
    return templates.TemplateResponse("plaid_link.html", {"request": request})


class ExchangeIn(BaseModel):
    public_token: str
    institution_name: str | None = None


@router.get("/link-token")
def link_token():
    try:
        token = plaid_client.create_link_token(client_user_id="local-user")
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"link_token": token}


@router.post("/exchange")
def exchange(payload: ExchangeIn, db: Session = Depends(get_db)):
    try:
        access_token, item_id = plaid_client.exchange_public_token(payload.public_token)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    item = db.query(PlaidItem).filter(PlaidItem.item_id == item_id).one_or_none()
    if item is None:
        item = PlaidItem(item_id=item_id, access_token=access_token, institution_name=payload.institution_name)
        db.add(item)
        db.flush()

    sync_service.refresh_account_balances(db, item)
    stats = sync_service.sync_item_transactions(db, item)
    db.commit()
    return {"item_id": item_id, "sync": stats}


@router.post("/sync")
def sync(db: Session = Depends(get_db)):
    if db.query(PlaidItem).count() == 0:
        raise HTTPException(status_code=400, detail="No linked bank accounts yet. Link one via /plaid/link-token first.")
    return {"results": sync_service.sync_all_items(db)}
