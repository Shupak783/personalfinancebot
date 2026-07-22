"""Sends a weekly spending recap email: total spent, a category-ranked bar chart, and a
breakdown table. Run this on a schedule (see README) - e.g. Sunday evening.

Usage: python -m scripts.weekly_email_recap
"""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal, init_db  # noqa: E402
from app.email_service import send_html_email  # noqa: E402
from app.models import PlaidItem  # noqa: E402
from app.reports import category_spend_over_period, render_category_bar_chart  # noqa: E402
from app.sync_service import sync_all_items  # noqa: E402


def build_html(category_spend: list[dict], total_cents: int, start: datetime.datetime, end: datetime.datetime) -> str:
    rows_html = "".join(
        f"<tr><td style='padding:4px 10px;border-bottom:1px solid #333'>{r['category']}</td>"
        f"<td style='padding:4px 10px;border-bottom:1px solid #333;text-align:right'>"
        f"${r['spent_cents'] / 100:,.2f}</td></tr>"
        for r in category_spend
    )
    return f"""
    <div style="font-family: -apple-system, Helvetica, sans-serif; max-width: 600px; color: #111;">
      <h2 style="margin-bottom: 4px;">Weekly spending recap</h2>
      <p style="color: #555; margin-top: 0;">{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}</p>
      <p style="font-size: 1.4rem; font-weight: 600;">Total spent: ${total_cents / 100:,.2f}</p>
      <img src="cid:category_chart" style="max-width: 100%; display: block; margin: 16px 0;"
           alt="Bar chart of spending by category" />
      <table style="border-collapse: collapse; width: 100%;">
        <tr>
          <th style="text-align:left; padding:4px 10px; border-bottom:2px solid #333;">Category</th>
          <th style="text-align:right; padding:4px 10px; border-bottom:2px solid #333;">Spent</th>
        </tr>
        {rows_html}
      </table>
    </div>
    """


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        if db.query(PlaidItem).count() > 0:
            sync_all_items(db)

        period_end = datetime.datetime.now(datetime.timezone.utc)
        period_start = period_end - datetime.timedelta(days=7)
        category_spend = category_spend_over_period(db, period_start, period_end)

        if not category_spend:
            print("No spending logged in the last 7 days - skipping email.")
            return

        total_cents = sum(r["spent_cents"] for r in category_spend)
        chart_bytes = render_category_bar_chart(category_spend)
        html_body = build_html(category_spend, total_cents, period_start, period_end)

        send_html_email(
            subject=f"Weekly spending recap - ${total_cents / 100:,.2f}",
            html_body=html_body,
            inline_images={"category_chart": chart_bytes},
        )
        print(f"Sent weekly recap: ${total_cents / 100:,.2f} total across {len(category_spend)} categories.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
