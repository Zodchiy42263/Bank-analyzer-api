from flask import Blueprint, jsonify

from app.extensions import db
from app.models.user import User

users_bp = Blueprint("accounts", __name__)


@users_bp.get("/api/accounts")
def accounts():
    users = User.query.order_by(User.id).all()
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
