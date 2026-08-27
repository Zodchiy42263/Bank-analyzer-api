from flask import Blueprint, jsonify, abort

from app.extensions import db
from app.models.saving_account import SavingsAccount

saving_accounts_bp = Blueprint("saving_accounts", __name__)


@saving_accounts_bp.get("/api/saving_accounts")
def get_saving_accounts():
    pass
