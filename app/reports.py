import datetime
import io
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Transaction


def category_spend_over_period(
    db: Session, start: datetime.datetime, end: datetime.datetime
) -> list[dict]:
    """Ranks categories by expense total (highest spend first) over [start, end)."""
    rows = (
        db.query(Transaction)
        .filter(Transaction.date >= start, Transaction.date < end, Transaction.amount_cents > 0)
        .all()
    )
    spend: dict[str, int] = defaultdict(int)
    for t in rows:
        name = t.category.name if t.category else "Uncategorized"
        spend[name] += t.amount_cents

    return sorted(
        ({"category": name, "spent_cents": cents} for name, cents in spend.items()),
        key=lambda r: r["spent_cents"],
        reverse=True,
    )


def render_category_bar_chart(category_spend: list[dict]) -> bytes:
    """Renders a horizontal bar chart (highest spend on top) as PNG bytes for email embedding."""
    import matplotlib

    matplotlib.use("Agg")  # headless - no display server needed
    import matplotlib.pyplot as plt

    labels = [r["category"] for r in category_spend]
    values = [r["spent_cents"] / 100 for r in category_spend]

    fig, ax = plt.subplots(figsize=(6, max(0.4 * len(labels), 1.5) + 1))
    ax.barh(labels, values, color="#4f8cff")
    ax.invert_yaxis()  # highest spend at the top
    ax.set_xlabel("Spent ($)")
    ax.set_title("This week's spending by category")
    for i, v in enumerate(values):
        ax.text(v, i, f" ${v:,.2f}", va="center", fontsize=8)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    return buf.getvalue()
