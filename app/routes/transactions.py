from copy import deepcopy
from datetime import datetime
from decimal import Decimal

from flask import request, Blueprint, jsonify, Response
from sqlalchemy.engine.row import Row
from sqlalchemy.sql.selectable import Select

from app.extensions import db
from app.routes.overviews import calc_balance
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.bank import Bank
from app.schemas.transactions import TransactionsQuery
from app.utils.validation import validate_data
from app.utils.account_validation import _current_account
from app.constants.transactions import TRANSACTION_TYPES
from app.intervals import now, periods, periods_models, operations_intervals

transactions_bp = Blueprint("transactions", __name__)


def create_transactions_command() -> Select:
    """Функция создания команды для получения всех транзакций.

    Returns:
        Select: Команда для получения всех транзакций из БД.
    """
    command = db.select(
        Transaction.id,
        Account.account_name,
        Bank.bank_name,
        Transaction.record_date,
        Transaction.amount,
        Transaction.type
    ).join(
        Account, Transaction.account_id == Account.id
    ).join(
        Bank,
        Transaction.bank_id == Bank.id
    )

    return command


def add_period_filter(command: Select, period: str, account_id: int) -> Select:
    """Функция для добавления фильтров период и аккаунт в команду на получение транзакций.

    Args:
        command (Select): Команда для получения транзакций.
        period (str): Период, за который надо получить транзакции.
        account_id (int): Текущий аккаунт.

    Returns:
        Select: Команда с фильтром (WHERE).
    """
    if period != "V":
        filtered_command = command.filter(
            Transaction.account_id == account_id,
            Transaction.record_date <= now,
            Transaction.record_date >= periods[period]
        )
    else:
        filtered_command = command.filter(
            Transaction.account_id == account_id
        )

    return filtered_command


def divide_transactions_by_type(transactions: list[Row]) -> dict[str, list]:
    """Функция деления транзакций на доходы, расходы, задолженность.

    Args:
        transactions (list[Row]): Транзакции за запрошенный период.

    Returns:
        dict[str, list]: Транзакции распределённые по одному из 3х типов.
    """
    divided_transactions = {
        "income": [],
        "expense": [],
        "debt": [],
    }
    for transaction in transactions:
        if transaction.type in ["loan", "mortgage"]:
            data = "debt"
        elif transaction.type in TRANSACTION_TYPES["income"]:
            data = "income"
        else:
            data = "expense"

        divided_transactions[data].append((transaction.record_date, transaction.amount))

    return divided_transactions


def calculate_totals(divided_transactions: dict[list]) -> dict[str, float]:
    """Функция расчёта общих сумм доходов, расходов и задолженности за переданный период.

    Args:
        divided_transactions (dict[list]): Транзакции распределённые на доходы, расходы и задолженность.

    Returns:
        dict[str, float]: Общие сумму по доходам, расходам и задолженности.
    """
    totals = {
        "income": 0.0,
        "expense": 0.0,
        "debt": 0.0,
    }

    for key, values in divided_transactions.items():
        totals[key] = sum([round(float(value[1]), 2) for value in values])

    return totals


def aggregate_by_hours(
    transaction_groups: dict[str, dict],
    transaction_type: str,
    value: tuple[datetime, Decimal]
) -> dict[str, dict]:
    """Функция определения, к какому из 3-х 8-ми часовых интервалов дня относится транзакция (Распределение за день).
    см. шаблон для заполнения типов в intervals.py operations_intervals["D"] и periods_models["D"][axis]

    Args:
        transaction_groups (dict[str, dict]): Шаблон для формирования общих сумм доходов, расходов и задолженности
                                              в интервалах переданного периода, постепенно заполняющийся данными.
        transaction_type (str): Тип транзакции, которую надо поместить в соответствующий интервал.
        value (tuple[datetime, Decimal]): Дата и сумма операции.

    Returns:
        dict[str, dict]: Обновленный transaction_groups с добавлением переданной транзакции в соответствующие
                         тип и интервал.
    """
    for hour in transaction_groups[transaction_type].keys():
        if value[0].hour < hour:
            transaction_groups[transaction_type][hour] += float(value[1])
            break

    return transaction_groups


def aggregate_by_days(
    transaction_groups: dict[str, dict],
    transaction_type: str,
    value: tuple[datetime, Decimal]
) -> dict[str, dict]:
    """Функция определения, к какому дню недели относится транзакция (Распределение за неделю).
    см. шаблон для заполнения типов в intervals.py operations_intervals["N"] и periods_models["N"][axis]

    Args:
        transaction_groups (dict[str, dict]): Шаблон для формирования общих сумм доходов, расходов и задолженности
                                              в интервалах переданного периода, постепенно заполняющийся данными.
        transaction_type (str): Тип транзакции, которую надо поместить в соответствующий интервал.
        value (tuple[datetime, Decimal]): Дата и сумма операции.

    Returns:
        dict[str, dict]: Обновленный transaction_groups с добавлением переданной транзакции в соответствующие
                         тип и интервал.
    """
    for day in transaction_groups[transaction_type].keys():
        if value[0].day == day:
            transaction_groups[transaction_type][day] += float(value[1])
            break

    return transaction_groups


def aggregate_by_date_range(
    transaction_groups: dict[str, dict],
    transaction_type: str,
    value: tuple[datetime, Decimal]
) -> dict[str, dict]:
    """Функция определения, к какой группе дней относится транзакция (Распределение за месяц).
    см. шаблон для заполнения типов в intervals.py operations_intervals["M"] и periods_models["M"][axis]

    Args:
        transaction_groups (dict[str, dict]): Шаблон для формирования общих сумм доходов, расходов и задолженности
                                              в интервалах переданного периода, постепенно заполняющийся данными.
        transaction_type (str): Тип транзакции, которую надо поместить в соответствующий интервал.
        value (tuple[datetime, Decimal]): Дата и сумма операции.

    Returns:
        dict[str, dict]: Обновленный transaction_groups с добавлением переданной транзакции в соответствующие
                         тип и интервал.
    """
    for day in transaction_groups[transaction_type].keys():
        if value[0].day <= day:
            transaction_groups[transaction_type][day] += float(value[1])
            break

    return transaction_groups


def aggregate_by_months(
    transaction_groups: dict[str, dict],
    transaction_type: str,
    value: tuple[datetime, Decimal]
) -> dict[str, dict]:
    """Функция определения, к какому месяцу относится транзакция (Распределение за квартал или год).
    см. шаблон для заполнения типов в intervals.py operations_intervals["K" или "G"] и periods_models["K или G"][axis]

    Args:
        transaction_groups (dict[str, dict]): Шаблон для формирования общих сумм доходов, расходов и задолженности
                                              в интервалах переданного периода, постепенно заполняющийся данными.
        transaction_type (str): Тип транзакции, которую надо поместить в соответствующий интервал.
        value (tuple[datetime, Decimal]): Дата и сумма операции.

    Returns:
        dict[str, dict]: Обновленный transaction_groups с добавлением переданной транзакции в соответствующие
                         тип и интервал.
    """
    for month in transaction_groups[transaction_type].keys():
        if value[0].month == month:
            transaction_groups[transaction_type][month] += float(value[1])
            break

    return transaction_groups


def aggregate_by_years(
    transaction_groups: dict[str, dict],
    transaction_type: str,
    value: tuple[datetime, Decimal]
) -> dict[str, dict]:
    """Функция определения, к какому году относится транзакция (Распределение за всё время).
    см. шаблон для заполнения типов в intervals.py operations_intervals["V"]  и periods_models["V"][axis]

    Args:
        transaction_groups (dict[str, dict]): Шаблон для формирования общих сумм доходов, расходов и задолженности
                                              в интервалах переданного периода, постепенно заполняющийся данными.
        transaction_type (str): Тип транзакции, которую надо поместить в соответствующий интервал.
        value (tuple[datetime, Decimal]): Дата и сумма операции.

    Returns:
        dict[str, dict]: Обновленный transaction_groups с добавлением переданной транзакции в соответствующие
                         тип и интервал.
    """
    year = value[0].year
    if str(year) not in transaction_groups[transaction_type]:
        for t_type in ["income", "expense", "debt"]:
            transaction_groups[t_type][str(year)] = 0.0

    transaction_groups[transaction_type][str(year)] += float(value[1])

    return transaction_groups


def round_money(transaction_groups: dict[str, dict]) -> dict[str, dict]:
    """Функция приведения сумм транзакций к общему формату с двумя знаками после запятой.

    Args:
        transaction_groups (dict[str, dict]): Транзакции распределённые по типам и интервалам.

    Returns:
        dict[str, dict]: Транзакции с отформатированными значениями сумм.
    """
    for intervals_amounts in transaction_groups.values():
        for interval, amount in intervals_amounts.items():
            intervals_amounts[interval] = round(amount, 2)

    return transaction_groups


def aggregate_transactions_by_interval(period: str, divided_transactions: dict[str, list]) -> dict[str, dict]:
    """Функция распределения транзакций на интервалы в зависимости от выбранного периода.

    Args:
        period (str): Период, транзакции которого надо распределить по интервалам (определяет шаблон интервалов).
        divided_transactions (dict[str, list]): Транзакции, разделённые на доходы, расходы и задолженность.

    Returns:
        dict[str, dict]: Транзакции распределённые по типам и интервалам.
    """
    transaction_groups = deepcopy(operations_intervals[period])

    for transaction_type, data in divided_transactions.items():
        for intervals_amounts in data:
            if period == "D":
                transaction_groups = aggregate_by_hours(transaction_groups, transaction_type, intervals_amounts)
            elif period == "N":
                transaction_groups = aggregate_by_days(transaction_groups, transaction_type, intervals_amounts)
            elif period == "M":
                transaction_groups = aggregate_by_date_range(transaction_groups, transaction_type, intervals_amounts)
            elif period in ["K", "G"]:
                transaction_groups = aggregate_by_months(transaction_groups, transaction_type, intervals_amounts)
            elif period == "V":
                transaction_groups = aggregate_by_years(transaction_groups, transaction_type, intervals_amounts)

    transaction_groups = round_money(transaction_groups)

    return transaction_groups


def build_period_stats(
    period_operations_intervals: dict[str, dict],
    totals: dict[str, float],
    account_id: int
) -> dict[str, list | float]:
    """Функция распределения отсортированных данных по транзакциям в шаблон для формирования графика.
    Объединяется с periods_models в generate_chart_data().

    Args:
        period_operations_intervals (dict[str, dict]): Транзакции распределённые по типам и интервалам.
        totals (dict[str, float]): Суммы доходов, расходов и задолженности за весь период.
        account_id (int): Текущий аккаунт.
    Returns:
        dict[str, list | float]: Шаблон для формирования графика, с распределёнными суммами транзакций.
    """
    period_stats = {
        "income_shape": [], "expense_shape": [], "debt_shape": [], "profit_shape": [], "profit_share": [],
        "income_max": None, "expense_max": None,
        "income_total": None, "expense_total": None, "debt": None,
    }
    total_balance = calc_balance(account_id)["total_balance"]

    for operation_type in period_operations_intervals.keys():
        period_stats[f"{operation_type}_shape"] = list(period_operations_intervals[operation_type].values())

    for income, expense in zip(period_stats["income_shape"], period_stats["expense_shape"]):
        profit = income - expense
        period_stats["profit_shape"].append(round(profit, 2))
        period_stats["profit_share"].append(round(profit / total_balance, 6))

    period_stats["income_max"] = round(totals["income"] * 1.2, 2)
    period_stats["expense_max"] = round(totals["expense"] * 1.2, 2)
    period_stats["income_total"] = totals["income"]
    period_stats["expense_total"] = totals["expense"]
    period_stats["debt"] = totals["debt"]

    return period_stats


def generate_chart_data(
    period: str,
    transactions: list[Row],
    account_id: int
) -> dict[str, str | int | float | list]:
    """Функция заполнения шаблона для составления графика показателей запрошенного периода.

    Args:
        period (str): Период, из транзакций которого надо сформировать график.
        transactions (list[Row]): Транзакции для формирования графика.
        account_id (int): Текущий аккаунт.

    Returns:
        dict[str, str | int | float | list]: Шаблона для составления графика.
    """
    divided_transactions = divide_transactions_by_type(transactions)
    totals = calculate_totals(divided_transactions)

    transaction_groups = aggregate_transactions_by_interval(period, divided_transactions)
    period_stats = build_period_stats(transaction_groups, totals, account_id)

    if period == "V":
        periods_models[period]["axis"] = [year for year in transaction_groups["income"].keys()]

    for key, value in period_stats.items():
        periods_models[period][key] = value

    return periods_models[period]


@transactions_bp.get("/api/transactions/chart")
def get_transactions_chart() -> Response:
    """Endpoint заполнения шаблона для составления графика показателей запрошенного периода.

    Returns:
        Response: Шаблон в формате JSON.
    """
    account_id = _current_account().id

    validated_data = validate_data(TransactionsQuery, request.args.to_dict())
    period = validated_data.period

    command = create_transactions_command()
    filtered_command = add_period_filter(command, period, account_id)
    transactions = db.session.execute(filtered_command).all()

    chart_data = generate_chart_data(period, transactions, account_id)

    return jsonify(chart_data)
