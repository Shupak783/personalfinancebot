import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class PlaidItem(Base):
    """One bank login (Plaid 'Item'). access_token stays local, never leaves this DB file."""

    __tablename__ = "plaid_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[str] = mapped_column(String, unique=True)
    access_token: Mapped[str] = mapped_column(String)
    institution_name: Mapped[str | None] = mapped_column(String, nullable=True)
    cursor: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    accounts: Mapped[list["Account"]] = relationship(back_populates="plaid_item")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plaid_item_id: Mapped[int | None] = mapped_column(ForeignKey("plaid_items.id"), nullable=True)
    plaid_account_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String)
    official_name: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, default="depository")  # depository, credit, loan, investment
    subtype: Mapped[str | None] = mapped_column(String, nullable=True)
    mask: Mapped[str | None] = mapped_column(String, nullable=True)
    current_balance_cents: Mapped[int] = mapped_column(Integer, default=0)
    available_balance_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")
    is_manual: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    plaid_item: Mapped["PlaidItem | None"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    is_income: Mapped[bool] = mapped_column(Boolean, default=False)
    monthly_budget_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    color: Mapped[str] = mapped_column(String, default="#6b7280")

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    plaid_transaction_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    # Plaid convention: positive amount = money out (expense), negative = money in (income/refund).
    amount_cents: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True))
    merchant_name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String)
    pending: Mapped[bool] = mapped_column(Boolean, default=False)
    is_manual: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped["Category | None"] = relationship(back_populates="transactions")

    @property
    def is_expense(self) -> bool:
        return self.amount_cents > 0


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String)  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Nudge(Base):
    """Autonomous check-in output: budget alerts, weekly summaries, honesty nudges."""

    __tablename__ = "nudges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String, default="summary")  # summary | alert
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
