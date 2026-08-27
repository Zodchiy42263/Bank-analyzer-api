from flask import Blueprint, jsonify, abort

from app.extensions import db
from app.models.minimum_balance_account import MinimumBalanceAccount

minimum_balance_accounts_bp = Blueprint("minimum_balance_accounts", __name__)


@minimum_balance_accounts_bp.get("/api/minimum_balance_accounts")
def get_minimum_balance_accounts():
    pass
