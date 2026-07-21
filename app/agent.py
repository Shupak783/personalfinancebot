import datetime
import json

import anthropic
from sqlalchemy.orm import Session

from app.budgeting import budget_status, detect_recurring_bills, net_cash_position_cents, total_cash_cents, total_credit_owed_cents
from app.config import settings
from app.models import ChatMessage, Transaction

SYSTEM_PROMPT = """You are the user's personal finance agent. You have direct, real read access to \
their bank balances, transactions, and budgets via tools - always call a tool to get current numbers \
before answering anything about money. Never guess or make up figures.

Your job:
- Keep the user honest about their spending and budgets - if they're overspending, say so plainly, \
don't soften it just to be agreeable.
- Help with everyday spending decisions ("can I afford a new golf driver?") by actually checking cash \
on hand, upcoming recurring bills, and this month's budget status before answering.
- Be concise and concrete: give a clear yes/no/it depends with the actual numbers behind it, not a \
generic lecture about budgeting.
- If data is missing (e.g. no bank linked yet, no budget set for a category), say so and suggest the \
concrete next step instead of guessing.
"""

TOOLS = [
    {
        "name": "get_balances",
        "description": "Get current cash balances, credit card balances owed, and net cash position across all linked/manual accounts.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_budget_status",
        "description": "Get spend-vs-budget for every category for a given month (defaults to current month).",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Defaults to current year"},
                "month": {"type": "integer", "description": "1-12, defaults to current month"},
            },
        },
    },
    {
        "name": "get_recent_transactions",
        "description": "Get the most recent transactions, optionally filtered by category name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max rows to return, default 20"},
                "category_name": {"type": "string"},
            },
        },
    },
    {
        "name": "get_recurring_bills",
        "description": "Detect recurring bills/subscriptions from transaction history over the last few months, with their typical amount.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "log_transaction",
        "description": "Log a manual income or expense the user mentions in chat (e.g. 'spent $85 at Costco', 'got paid $2000'). Use a negative amount for income.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount_dollars": {"type": "number", "description": "Positive for an expense, negative for income"},
                "description": {"type": "string"},
                "category_name": {"type": "string"},
            },
            "required": ["amount_dollars", "description"],
        },
    },
]


def _tool_get_balances(db: Session, _args: dict) -> dict:
    return {
        "total_cash_cents": total_cash_cents(db),
        "total_credit_owed_cents": total_credit_owed_cents(db),
        "net_cash_position_cents": net_cash_position_cents(db),
    }


def _tool_get_budget_status(db: Session, args: dict) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc)
    return {"categories": budget_status(db, args.get("year") or now.year, args.get("month") or now.month)}


def _tool_get_recent_transactions(db: Session, args: dict) -> dict:
    query = db.query(Transaction).order_by(Transaction.date.desc())
    category_name = args.get("category_name")
    if category_name:
        query = query.join(Transaction.category).filter_by(name=category_name)
    limit = args.get("limit") or 20
    rows = query.limit(limit).all()
    return {
        "transactions": [
            {
                "date": t.date.date().isoformat(),
                "description": t.description,
                "merchant": t.merchant_name,
                "amount_cents": t.amount_cents,
                "category": t.category.name if t.category else None,
            }
            for t in rows
        ]
    }


def _tool_get_recurring_bills(db: Session, _args: dict) -> dict:
    return {"recurring_bills": detect_recurring_bills(db)}


def _tool_log_transaction(db: Session, args: dict) -> dict:
    from app.budgeting import get_or_create_category, suggest_category
    from app.models import Account

    account = db.query(Account).filter(Account.is_manual.is_(True)).first()
    if account is None:
        account = Account(name="Manual/Cash", type="depository", is_manual=True)
        db.add(account)
        db.flush()

    amount_cents = round(args["amount_dollars"] * 100)
    category_name = args.get("category_name") or suggest_category(args["description"], None)
    category = get_or_create_category(db, category_name, is_income=amount_cents < 0)

    txn = Transaction(
        account_id=account.id,
        category_id=category.id,
        amount_cents=amount_cents,
        date=datetime.datetime.now(datetime.timezone.utc),
        description=args["description"],
        is_manual=True,
    )
    db.add(txn)
    account.current_balance_cents -= amount_cents
    db.commit()
    return {"logged": True, "category": category.name, "amount_cents": amount_cents}


TOOL_IMPLS = {
    "get_balances": _tool_get_balances,
    "get_budget_status": _tool_get_budget_status,
    "get_recent_transactions": _tool_get_recent_transactions,
    "get_recurring_bills": _tool_get_recurring_bills,
    "log_transaction": _tool_log_transaction,
}


def _recent_history(db: Session, turns: int = 10) -> list[dict]:
    rows = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(turns).all()
    rows.reverse()
    return [{"role": m.role, "content": m.content} for m in rows]


def run_agent(db: Session, user_message: str) -> str:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in your .env")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    db.add(ChatMessage(role="user", content=user_message))
    db.commit()

    messages = _recent_history(db) + [{"role": "user", "content": user_message}]

    for _ in range(6):  # cap tool-call round trips
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )

        if response.stop_reason != "tool_use":
            reply = "".join(block.text for block in response.content if block.type == "text")
            db.add(ChatMessage(role="assistant", content=reply))
            db.commit()
            return reply

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            impl = TOOL_IMPLS.get(block.name)
            result = impl(db, block.input) if impl else {"error": f"unknown tool {block.name}"}
            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
            )
        messages.append({"role": "user", "content": tool_results})

    reply = "Sorry, I got stuck reasoning about that - try rephrasing your question."
    db.add(ChatMessage(role="assistant", content=reply))
    db.commit()
    return reply
