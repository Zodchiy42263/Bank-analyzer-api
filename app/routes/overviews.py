from flask import Blueprint, abort, jsonify, request, Response, session

from app.extensions import db
from app.models.account import Account
from app.models.debit_card import DebitCard
from app.models.deposit import Deposit
from app.models.saving_account import SavingsAccount
from app.models.minimum_balance_account import MinimumBalanceAccount
from app.models.loan import Loan
from app.models.credit_card import CreditCard
from app.models.period import Period
from app.schemas.overview import ChartsQuery
from app.utils.validation import validate_data
from app.utils.account_validation import _current_account

total_balance_models = (DebitCard, Deposit, SavingsAccount, MinimumBalanceAccount)
debt_models = (Loan, CreditCard)
overview_bp = Blueprint("overview", __name__)

# Разбивка активов: доля от баланса + цвет (как в моке фронтенда).
ASSET_BREAKDOWN = [
    ("Вклады", 0.45, "hsl(150, 30%, 46%)"),
    ("Дебетовые счета", 0.25, "hsl(95, 26%, 52%)"),
    ("Инвестиции", 0.30, "hsl(210, 35%, 55%)"),
]


def calc_balance(account_id: Account) -> dict[str, float]:
    """Считает общий и чистый баланс пользователя.
    Расчёт баланс собирается из таблиц с деньгами;
    Чистый баланс — за вычетом задолженности.

    Args:
        account_id (Account): Пользователь, для которого считается баланс.

    Returns:
        dict[str, float]: Ключи 'balance' и 'net_balance'.
    """
    total_balance = 0
    debt = 0
    for model in total_balance_models:
        total_balance += db.session.query(
            db.func.sum(model.balance).filter(model.account_id == account_id)
        ).scalar()

    for model in debt_models:
        debt += db.session.query(
            db.func.sum(model.balance).filter(model.account_id == account_id)
        ).scalar()

    net_balance = total_balance - debt

    return {"total_balance": total_balance, "net_balance": net_balance}


@overview_bp.get("/api/overview/balance")
def balance() -> Response:
    """Эндпоинт для получения общего баланса и чистого баланса пользователя.

    Второй шаг после POST /api/account. Результат этого запроса —
    источник баланса и для карточки, и для запроса графиков.

    Returns:
        Response: Общий и чистый баланс в формате JSON.
    """
    account_id = _current_account().id

    return jsonify(calc_balance(account_id))


@overview_bp.get("/api/overview/charts")
def charts() -> Response:
    """Эндпоинт для получения данных графиков за период.

    Баланс для разбивки активов берётся из расчёта баланса
    (`calc_balance`), а не из данных аккаунта.

    Returns:
        Response: Ряды графиков, итоги за период и разбивка активов.
    """
    validated_data = validate_data(ChartsQuery, request.args.to_dict())

    account = _current_account()
    period = db.session.get(Period, validated_data.period)
    if period is None:
        abort(404, "period не найден")

    mult = float(account.mult)
    balance = calc_balance(account.id)["total_balance"]
    debt = float(period.debt) * mult

    # Кредиторка в разбивке активов берётся из годового долга (как в моке).
    year = db.session.get(Period, "G")
    year_debt = float(year.debt) * mult

    assets = [
        {"label": label, "amount": float(balance) * share, "color": color}
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
            "income": float(period.income_total) * mult,
            "expense": float(period.expense_total) * mult,
            "debt": debt,
            "incomeShape": period.income_shape,
            "expenseShape": period.expense_shape,
            "debtShape": period.debt_shape,
            "incomeMax": float(period.income_max) * mult,
            "expenseMax": float(period.expense_max) * mult,
            "debtMax": float(period.debt) * 1.35 * mult,
            "assets": assets,
        }
    )
