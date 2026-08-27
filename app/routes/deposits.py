from flask import Blueprint, jsonify, abort

from app.extensions import db
from app.models.deposit import Deposit

deposits_bp = Blueprint("deposits", __name__)


@deposits_bp.get("/api/deposits")
def get_deposits():
    pass
