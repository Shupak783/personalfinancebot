import datetime

from pydantic import BaseModel


class TransactionOut(BaseModel):
    id: int
    date: datetime.datetime
    description: str
    merchant_name: str | None
    amount_cents: int
    category_name: str | None
    pending: bool
    is_manual: bool

    model_config = {"from_attributes": True}


class ManualTransactionIn(BaseModel):
    amount_dollars: float
    description: str
    category_name: str | None = None
    account_id: int | None = None
    date: datetime.date | None = None


class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    reply: str
