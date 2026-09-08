from flask import request, session, abort

from app.extensions import db
from app.models.account import Account


def _current_account() -> Account:
    """Возвращает текущий аккаунт из сессии. (ставится в POST /api/account).

    Returns:
        Account: Текущий пользователь.
    """
    account_id = session.get("account_id")
    if account_id is None:
        abort(400, "сначала выберите пользователя: POST /api/account")

    account = db.session.get(Account, account_id)
    if account is None:
        abort(404, "Аккаунт не найден")

    return account
