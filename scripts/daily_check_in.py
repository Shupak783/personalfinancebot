"""Run this on a schedule (cron/Task Scheduler) to get the 'autonomous' part of the bot:
it syncs your bank, checks budgets, and leaves an honest nudge for you to see next time
you open the dashboard. Safe to run with no bank linked yet - it just skips the sync step.

Usage: python -m scripts.daily_check_in
"""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.budgeting import budget_status, detect_recurring_bills, net_cash_position_cents  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.models import Nudge, PlaidItem  # noqa: E402
from app.sync_service import sync_all_items  # noqa: E402


def build_fallback_message(budgets: list[dict], net_cash_cents: int, over_budget: list[dict]) -> str:
    if over_budget:
        names = ", ".join(b["category"] for b in over_budget)
        return f"Heads up: you're over budget this month in {names}. Net cash position is ${net_cash_cents / 100:.2f}."
    return f"On track this month. Net cash position is ${net_cash_cents / 100:.2f}."


def build_ai_message(budgets: list[dict], net_cash_cents: int, recurring: list[dict]) -> str | None:
    if not settings.anthropic_api_key:
        return None
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    facts = {
        "net_cash_position_cents": net_cash_cents,
        "budgets": budgets,
        "recurring_bills": recurring,
    }
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=300,
        system=(
            "You write a short (2-4 sentence), plain, honest daily/weekly financial check-in for the user "
            "based on the JSON facts given. Call out overspending directly, don't soften it. If everything "
            "looks fine, say so briefly - don't invent problems."
        ),
        messages=[{"role": "user", "content": str(facts)}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(PlaidItem).count() > 0:
            sync_all_items(db)

        now = datetime.datetime.now(datetime.timezone.utc)
        budgets = budget_status(db, now.year, now.month)
        over_budget = [b for b in budgets if b["over_budget"]]
        net_cash_cents = net_cash_position_cents(db)
        recurring = detect_recurring_bills(db)

        message = build_ai_message(budgets, net_cash_cents, recurring) or build_fallback_message(
            budgets, net_cash_cents, over_budget
        )
        kind = "alert" if over_budget or net_cash_cents < 0 else "summary"

        db.add(Nudge(kind=kind, message=message))
        db.commit()
        print(f"[{kind}] {message}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
