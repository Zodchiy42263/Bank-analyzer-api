from datetime import datetime, timedelta
from collections import defaultdict


def get_current_quarter() -> datetime:
    """Функция для получения, квартала в котором находится месяц.

    Returns:
        datetime: Дата первого месяца квартала.
    """

    for first_quarter_month in [10, 7, 4, 1]:
        if now.month >= first_quarter_month:
            start_of_quarter = (
                now.replace(month=first_quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            )
            return start_of_quarter


now = datetime.now()
start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
start_of_week = (now - timedelta(days=now.weekday())).replace(
    hour=0, minute=0, second=0, microsecond=0
)
start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
start_of_quarter = get_current_quarter()
start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

# Даты начала запрошенных периодов.
periods = {
    "D": start_of_day,
    "N": start_of_week,
    "M": start_of_month,
    "K": start_of_quarter,
    "G": start_of_year,
    "V": None
}

# Формат для формирования итоговых сумм за интервалы одного дня.
hours_intervals_amounts = {8: 0.0, 16: 0.0, 24: 0.0}
# Формат для формирования итоговых сумм дней недели.
days_intervals_amounts = {
    (start_of_week + timedelta(days=day)).day: 0.0
    for day in range(7)
}
# Формат для формирования итоговых сумм интервалов месяца.
weeks_intervals_amounts = {
    5: 0.0, 10: 0.0, 15: 0.0, 20: 0.0, 25: 0.0, 31: 0.0
}
# Формат для формирования итоговых сумм интервалов (месяцев) квартала.
quarters_intervals_amounts = {
    start_of_quarter.month: 0.0,
    start_of_quarter.replace(month=start_of_quarter.month + 1).month: 0.0,
    start_of_quarter.replace(month=start_of_quarter.month + 2).month: 0.0,
}
# Формат для формирования итоговых сумм интервалов (месяцев) года.
months_intervals_amounts = {
    start_of_year.month + month_index: 0.0
    for month_index in range(12)
}

periods_models = {
    "D": {
        "key": "D", "sort": 0, "short": "Д", "caption": "за сегодня",
        "date_prefix": "Сегодня, ",
        "axis": ["08:00", "16:00", "24:00"],
    },
    "N": {
        "key": "N", "sort": 1, "short": "Н", "caption": "за последнюю неделю",
        "date_prefix": "",
        "axis": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    },
    "M": {
        "key": "M", "sort": 2, "short": "М", "caption": "за последний месяц",
        "date_prefix": "",
        "axis": ["1-5", "6-10", "11-15", "16-20", "21-25", "26-31"],
    },
    "K": {
        "key": "K", "sort": 3, "short": "К", "caption": "за последний квартал",
        "date_prefix": "",
        "axis": ["Мес 1", "Мес 2", "Мес 3"]
    },
    "G": {
        "key": "G", "sort": 4, "short": "Г", "caption": "за последний год",
        "date_prefix": "",
        "axis": ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                 "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
    },
    "V": {
        "key": "V", "sort": 5, "short": "В", "caption": "за весь известный период",
        "date_prefix": "",
        "axis": []
    }
}

# Периоды с разделением на доходы, расходы и задолженность с шаблонами формирования сумм интервалов внутри.
# или
# Шаблон для формирования общих сумм доходов, расходов и задолженности в интервалах выбранного периода.
operations_intervals = {
    "D": {
        "income":
            hours_intervals_amounts.copy(),
        "expense":
            hours_intervals_amounts.copy(),
        "debt":
            hours_intervals_amounts.copy(),
    },
    "N": {
        "income":
            days_intervals_amounts.copy(),
        "expense":
            days_intervals_amounts.copy(),
        "debt":
            days_intervals_amounts.copy(),
    },
    "M": {
        "income":
            weeks_intervals_amounts.copy(),
        "expense":
            weeks_intervals_amounts.copy(),
        "debt":
            weeks_intervals_amounts.copy(),
    },
    "K": {
        "income":
            quarters_intervals_amounts.copy(),
        "expense":
            quarters_intervals_amounts.copy(),
        "debt":
            quarters_intervals_amounts.copy(),
    },
    "G": {
        "income":
            months_intervals_amounts.copy(),
        "expense":
            months_intervals_amounts.copy(),
        "debt":
            months_intervals_amounts.copy(),
    },
    "V": {
        "income":
            defaultdict(float),
        "expense":
            defaultdict(float),
        "debt":
            defaultdict(float),
    },
}
