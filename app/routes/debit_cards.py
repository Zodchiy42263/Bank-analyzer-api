from flask import request, session, Blueprint, jsonify, Response

from app.extensions import db
from app.models.debit_card import DebitCard

debit_card_bp = Blueprint("debit_card", __name__)


@debit_card_bp.get("/api/debit_card")
def get_debit_card():
    pass