from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.user import User
from app.models.period import Period


overview_bp = Blueprint("overview", __name__)

# Разбивка активов: доля от баланса + цвет (как в моке фронтенда).
ASSET_BREAKDOWN = [
    ("Вклады", 0.45, "hsl(150, 30%, 46%)"),
    ("Дебетовые счета", 0.25, "hsl(95, 26%, 52%)"),
    ("Инвестиции", 0.30, "hsl(210, 35%, 55%)"),
]


@overview_bp.get("/api/overview")
def overview():
    user_id = request.args.get("user", type=int)
    period_key = request.args.get("period", type=str)
    if user_id is None or not period_key:
        abort(400, "user и period обязательны")

    user = db.session.get(User, user_id)
    period = db.session.get(Period, period_key)
    if user is None or period is None:
        abort(404, "user или period не найдены")

    mult = float(user.mult)
    balance = float(user.balance)
    debt = float(period.debt) * mult

    # Кредиторка в разбивке активов берётся из годового долга (как в моке).
    year = db.session.get(Period, "G")
    year_debt = float(year.debt) * mult

    assets = [
        {"label": label, "amount": balance * share, "color": color}
        for (label, share, color) in ASSET_BREAKDOWN
    ]
    assets.append(
        {
            "label": "Кредиторская задолженность",
            "amount": year_debt,
            "color": "hsl(8, 42%, 50%)",
        }
    )

    return jsonify(
        {
            "period": period.key,
            "datePrefix": period.date_prefix,
            "axis": period.axis,
            "balance": balance,
            "debt": debt,
            "netBalance": balance - debt,
            "income": float(period.income_total) * mult,
            "expense": float(period.expense_total) * mult,
            "incomeShape": period.income_shape,
            "expenseShape": period.expense_shape,
            "debtShape": period.debt_shape,
            "incomeMax": float(period.income_max) * mult,
            "expenseMax": float(period.expense_max) * mult,
            "debtMax": float(period.debt) * 1.35 * mult,
            "assets": assets,
        }
    )
