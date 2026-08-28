from flask import Blueprint, abort, jsonify, request, Response, session

from app.extensions import db
from app.models.account import Account
from app.models.period import Period


overview_bp = Blueprint("overview", __name__)

# Разбивка активов: доля от баланса + цвет (как в моке фронтенда).
ASSET_BREAKDOWN = [
    ("Вклады", 0.45, "hsl(150, 30%, 46%)"),
    ("Дебетовые счета", 0.25, "hsl(95, 26%, 52%)"),
    ("Инвестиции", 0.30, "hsl(210, 35%, 55%)"),
]

# TODO: временные константы для заглушки баланса. Удалить вместе с ней.
PLACEHOLDER_BALANCE = 482340.00
PLACEHOLDER_DEBT = 15200.00


def _current_user() -> Account:
    """Пользователь из сессии (ставится в POST /api/account).

    Returns:
        Account: Текущий пользователь.
    """
    user_id = session.get("account_id")
    if user_id is None:
        abort(400, "сначала выберите пользователя: POST /api/account")

    user = db.session.get(Account, user_id)
    if user is None:
        abort(404, "user не найден")

    return user


def calc_balance(user: Account) -> dict[str, float]:
    """Считает общий и чистый баланс пользователя.

    TODO: ЗАГЛУШКА. Здесь должен быть реальный расчёт: баланс собирается
    из таблиц с деньгами (debit_cards, savings_accounts,
    minimum_balance_accounts, deposits), чистый баланс — за вычетом
    задолженности (loans, credit_cards). Никакой колонки balance
    в таблице accounts больше нет.

    Args:
        user (Account): Пользователь, для которого считается баланс.

    Returns:
        dict[str, float]: Ключи `balance` и `netBalance`.
    """
    mult = float(user.mult)
    balance = PLACEHOLDER_BALANCE * mult
    net_balance = balance - PLACEHOLDER_DEBT * mult

    return {"balance": balance, "netBalance": net_balance}


@overview_bp.get("/api/overview/balance")
def balance() -> Response:
    """Эндпоинт для получения баланса и чистого баланса пользователя.

    Второй шаг после POST /api/account. Результат этого запроса —
    источник баланса и для карточки, и для запроса графиков.

    Returns:
        Response: Общий и чистый баланс в формате JSON.
    """
    user = _current_user()

    return jsonify(calc_balance(user))


@overview_bp.get("/api/overview/charts")
def charts() -> Response:
    """Эндпоинт для получения данных графиков за период.

    Баланс для разбивки активов берётся из расчёта баланса
    (`calc_balance`), а не из данных аккаунта.

    Returns:
        Response: Ряды графиков, итоги за период и разбивка активов.
    """
    period_key = request.args.get("period", type=str)
    if not period_key:
        abort(400, "period обязателен")

    user = _current_user()
    period = db.session.get(Period, period_key)
    if period is None:
        abort(404, "period не найден")

    mult = float(user.mult)
    balance = calc_balance(user)["balance"]
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
