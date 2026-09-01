from flask import request, session, Blueprint, jsonify, Response, abort

from app.extensions import db
from app.models.account import Account
from app.schemas.session import SessionRequests
from app.utils.validation import validate_data

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.get("/api/accounts")
def accounts() -> Response:
    """Эндпоинт для получения списка аккаунтов.

    Returns:
        Response: Список аккаунтов в формате JSON.
    """
    accounts = Account.query.order_by(Account.id).all()
    return jsonify(
        [
            {
                "id": account.id,
                "account_name": account.account_name,
                "initials": account.initials,
            }
            for account in accounts
        ]
    )


@accounts_bp.post("/api/account")
def account() -> Response:
    """Эндпоинт для назначения пользователя в сессии.

    Returns:
        Response: Статус назначения пользователя.
    """
    validated_data = validate_data(SessionRequests, request.get_json())

    account = db.session.get(Account, validated_data.account_id)
    if not account:
        abort(404, "Аккаунт не найден")

    session["account_id"] = validated_data.account_id

    return jsonify({"status": "connected"})
