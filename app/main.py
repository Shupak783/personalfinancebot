from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.routers import budgets_router, chat_router, dashboard_router, plaid_router, transactions_router

app = FastAPI(title="Personal Finance Bot")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard_router.router)
app.include_router(plaid_router.router)
app.include_router(transactions_router.router)
app.include_router(budgets_router.router)
app.include_router(chat_router.router)


@app.on_event("startup")
def on_startup():
    init_db()
