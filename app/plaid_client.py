import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from app.config import settings

_ENV_HOSTS = {
    "sandbox": plaid.Environment.Sandbox,
    "development": getattr(plaid.Environment, "Development", plaid.Environment.Sandbox),
    "production": plaid.Environment.Production,
}


def get_client() -> plaid_api.PlaidApi:
    if not settings.plaid_client_id or not settings.plaid_secret:
        raise RuntimeError(
            "Plaid is not configured. Set PLAID_CLIENT_ID and PLAID_SECRET in your .env "
            "(get free sandbox keys at https://dashboard.plaid.com)."
        )
    configuration = plaid.Configuration(
        host=_ENV_HOSTS.get(settings.plaid_env, plaid.Environment.Sandbox),
        api_key={"clientId": settings.plaid_client_id, "secret": settings.plaid_secret},
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def create_link_token(client_user_id: str) -> str:
    client = get_client()
    request = LinkTokenCreateRequest(
        products=[Products(p) for p in settings.plaid_products_list],
        client_name="Personal Finance Bot",
        country_codes=[CountryCode(c) for c in settings.plaid_country_codes_list],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id=client_user_id),
    )
    response = client.link_token_create(request)
    return response.link_token


def exchange_public_token(public_token: str) -> tuple[str, str]:
    """Returns (access_token, item_id)."""
    client = get_client()
    response = client.item_public_token_exchange(ItemPublicTokenExchangeRequest(public_token=public_token))
    return response.access_token, response.item_id


def get_accounts(access_token: str):
    client = get_client()
    response = client.accounts_get(AccountsGetRequest(access_token=access_token))
    return response.accounts


def sync_transactions(access_token: str, cursor: str | None = None):
    """Pulls added/modified/removed transactions since the last cursor.

    Returns (added, modified, removed_ids, next_cursor, has_more).
    """
    client = get_client()
    added, modified, removed = [], [], []
    has_more = True
    next_cursor = cursor
    while has_more:
        request = TransactionsSyncRequest(access_token=access_token, cursor=next_cursor or "")
        response = client.transactions_sync(request)
        added.extend(response.added)
        modified.extend(response.modified)
        removed.extend(response.removed)
        has_more = response.has_more
        next_cursor = response.next_cursor
    return added, modified, [r.transaction_id for r in removed], next_cursor
