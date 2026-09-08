from flask import request, session, Blueprint, jsonify, Response

from app.extensions import db
from app.models.credit_card import CreditCard

credit_cards_bp = Blueprint("credit_cards", __name__)


@credit_cards_bp.get("/api/credit_cards")
def get_credit_cards():
    pass
