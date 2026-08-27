from flask import Blueprint, jsonify, abort

from app.extensions import db
from app.models.bank import Bank

banks_bp = Blueprint("banks", __name__)


@banks_bp.get("/api/banks")
def get_banks():
    pass
