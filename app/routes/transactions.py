from flask import Blueprint, jsonify

from app.extensions import db
from app.models.transaction import Transaction

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.get("/api/transactions")
def accounts():
    pass
