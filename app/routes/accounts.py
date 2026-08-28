from flask import request, session, Blueprint, jsonify, Response

from app.extensions import db
from app.models.account import Account

accounts_bp = Blueprint("accounts", __name__)

@accounts_bp.get("/api/accounts")
def accounts() -> Response:
    """Эндпоинт для получения списка аккаунтов.

    Returns:
        Response: Список аккаунтов в формате JSON.
    """
    users = Account.query.order_by(Account.id).all()
    return jsonify(
        [
            {
                "id": u.id,
                "name": u.name,
                "initials": u.initials,
            }
            for u in users
        ]
    )

@accounts_bp.post("/api/account")
def account() -> Response:
    """Эндпоинт для назначения пользователя в сессии.

    Returns:
        Response: Статус назначения пользователя.
    """
    data = request.get_json()
    session["account_id"] = data["account_id"]

    return jsonify({"status": "connected"})
