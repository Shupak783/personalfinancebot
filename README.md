# Personal Finance Bot

A self-hosted personal finance dashboard with a Claude-powered chat assistant. It tracks
income/expenses, tracks budgets per category, and can pull real transactions from your bank
via Plaid. The chat assistant answers spending questions ("can I afford a new golf driver?")
using your *actual* balances and budget status - it won't just make numbers up.

Everything runs locally on your own machine. Your data lives in a single `finbot.db` file
next to the code; nothing is sent anywhere except to Anthropic (for chat) and Plaid (for bank
sync), and only when you actively use those features.

## 1. One-time setup

You'll need Python 3.11+ installed. Then, from this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Now open `.env` in any text editor and fill in:

- **`ANTHROPIC_API_KEY`** - get one at https://console.anthropic.com (needed for the chat
  assistant; without it the dashboard still works, just no chat).
- **`PLAID_CLIENT_ID`** / **`PLAID_SECRET`** - get free sandbox keys at
  https://dashboard.plaid.com (needed only if you want bank sync; the app runs fine without
  it, using manual entry instead).

Leave `PLAID_ENV=sandbox` for now - that's Plaid's fake-bank testing mode, no real bank
credentials involved. See "Going to a real bank" below for switching later.

## 2. (Optional) Load some demo data

If you want to see the dashboard with realistic numbers before connecting anything real:

```bash
python -m scripts.seed_demo_data
```

This creates a fake "Demo Checking" account with ~3 months of sample transactions and
budgets. Delete `finbot.db` any time to start over with a clean slate.

## 3. Run it

```bash
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 in your browser. That's the dashboard: balances, budget
progress bars, recent transactions, and a chat panel on the right.

## 4. Link a bank account (optional)

Click "Link a bank account" on the dashboard. In sandbox mode, pick any institution and
when prompted for credentials use:

- username: `user_good`
- password: `pass_good`

This pulls in fake-but-realistic transactions and balances so you can test the real sync
flow without using your actual bank login.

## 5. Log spending manually (no bank needed)

You don't need Plaid at all to use this day to day - just tell the chat assistant things
like:

> spent $85 at Costco
> got paid $2200 today

It logs them, auto-categorizes them, and they show up on the dashboard immediately.

## 6. The "autonomous" check-in

Run this on a schedule (daily or weekly) to have it sync your bank, check your budgets, and
leave you an honest nudge (visible at the top of the dashboard next time you open it):

```bash
python -m scripts.daily_check_in
```

To automate it:

- **macOS/Linux (cron)**: `crontab -e`, then add a line like
  `0 8 * * * cd /path/to/personalfinancebot && .venv/bin/python -m scripts.daily_check_in`
  to run it every morning at 8am.
- **Windows**: use Task Scheduler to run
  `C:\path\to\personalfinancebot\.venv\Scripts\python.exe -m scripts.daily_check_in` on a
  daily trigger.

Note this only runs while your computer is on and the schedule fires - it isn't a 24/7
cloud service. If you want that later, the app would need to be deployed somewhere (a small
server or a host like Railway/Fly.io) - happy to help with that when you're ready.

## 7. Weekly email recap

A once-a-week email summarizing your spending: total for the past 7 days, a bar chart
ranking categories by spend (highest at top), and a breakdown table. Clicking any category
on the dashboard itself also filters the transaction list down to just that category, so you
can see what actually landed in e.g. "Uncategorized."

This uses your own email account to send, via an **app password** rather than your real
login password - a separate, revocable code your email provider generates specifically for
letting a script send mail. For Gmail:

1. Turn on 2-Step Verification if you haven't already (https://myaccount.google.com/security).
2. Generate an app password at https://myaccount.google.com/apppasswords.
3. In `.env`, set `EMAIL_USERNAME` to your Gmail address, `EMAIL_APP_PASSWORD` to the
   generated code, and `EMAIL_TO` to whichever address you want the recap sent to (can be
   the same address).

Then send a recap on demand with:

```bash
python -m scripts.weekly_email_recap
```

To automate it weekly:

- **macOS/Linux (cron)**: `crontab -e`, add
  `0 18 * * 0 cd /path/to/personalfinancebot && .venv/bin/python -m scripts.weekly_email_recap`
  to send it every Sunday at 6pm.
- **Windows**: Task Scheduler, weekly trigger, same command as the daily check-in but
  pointing at `scripts.weekly_email_recap`.

If there's no spending in the last 7 days, it skips sending rather than emailing an empty
recap.

## Market news panel

The bottom-right panel on the dashboard shows a rotating carousel of real financial
headlines (stocks/bonds/ETFs/markets), pulled from a fixed allowlist of established outlets
(MarketWatch, CNBC Markets) - not user-editable feed URLs, so it can't be pointed at an
arbitrary or untrusted source. Clicking a headline opens the original article on the
source's own site in a new tab; the app never renders full article content itself.

Above the carousel is a short "what's happening in the markets" overview, written by Claude
from the headlines. That call is deliberately isolated: it has no access to your accounts,
budgets, or any tool the chat assistant has, and its instructions explicitly forbid
recommending that you buy, sell, or hold anything - it only describes trends. This only runs
if `ANTHROPIC_API_KEY` is set; without it, the carousel still works, just without the
overview blurb.

## Going to a real bank (Plaid production)

Plaid's sandbox (the default) uses fake data and works immediately. To connect a *real* bank
account you'd need to apply for Plaid production access through their dashboard (their
approval process, not something this app controls), then set `PLAID_ENV=production` in
`.env` with your production keys. Don't do this until you're comfortable with how the app
behaves in sandbox mode.

## Running tests

```bash
pytest
```

## Project layout

```
app/
  models.py          - database tables (accounts, transactions, categories, budgets, chat)
  budgeting.py        - categorization rules + budget/net-worth math
  plaid_client.py      - Plaid API wrapper
  sync_service.py      - pulls Plaid transactions/balances into the local database
  agent.py            - the Claude-powered chat assistant and its tools
  news.py             - market headline fetch/cache + isolated trend-overview summarizer
  reports.py          - category spend aggregation + bar chart rendering
  email_service.py     - sends HTML emails with inline images via SMTP/app password
  routers/            - web API endpoints
  templates/, static/  - the dashboard web page
scripts/
  seed_demo_data.py    - loads fake sample data
  daily_check_in.py    - the scheduled autonomous check-in
  weekly_email_recap.py - sends the weekly spending recap email
```

## Security

See [SECURITY.md](./SECURITY.md) for the actual security/access/data-retention practices
this project follows - written honestly for what this is (a single-user local app), not
padded with enterprise controls that don't apply. Includes how to run a dependency
vulnerability scan with `pip-audit`.
