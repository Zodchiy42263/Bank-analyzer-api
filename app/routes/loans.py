from flask import request, session, Blueprint, jsonify, Response

from app.extensions import db
from app.models.loan import Loan

loans_bp = Blueprint("loans", __name__)


@loans_bp.get("/api/loans")
def get_loans():
    pass
