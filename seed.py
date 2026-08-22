"""
Создаёт таблицы и наполняет БД данными, повторяющими моки фронтенда.
Запуск:  python seed.py
"""

from app import Period, User, app, db

USERS = [
    {"name": "Иван Соколов", "initials": "ИС", "balance": 482340.00, "mult": 1.00},
    {"name": "Анна Смирнова", "initials": "АС", "balance": 219870.00, "mult": 0.45},
    {"name": "Дмитрий Волков", "initials": "ДВ", "balance": 1054200.00, "mult": 2.15},
    {"name": "Мария Петрова", "initials": "МП", "balance": 76540.00, "mult": 0.16},
]

PERIODS = [
    {
        "key": "D", "sort": 0, "short": "Д", "caption": "за сегодня",
        "date_prefix": "Сегодня, ",
        "axis": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "income_shape": [0.32, 0.55, 0.38, 0.72, 0.9, 0.61],
        "expense_shape": [0.48, 0.4, 0.58, 0.44, 0.62, 0.5],
        "debt_shape": [0.55, 0.5, 0.58, 0.6, 0.62, 0.65],
        "income_total": 6420.35, "expense_total": 4380.90, "debt": 4200.00,
    },
    {
        "key": "N", "sort": 1, "short": "Н", "caption": "за последнюю неделю",
        "date_prefix": "",
        "axis": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "income_shape": [0.35, 0.5, 0.42, 0.68, 0.6, 0.82, 0.55],
        "expense_shape": [0.45, 0.42, 0.5, 0.48, 0.55, 0.6, 0.5],
        "debt_shape": [0.45, 0.5, 0.48, 0.55, 0.58, 0.6, 0.63],
        "income_max": 9200, "expense_max": 6800,
        "income_total": 41250.60, "expense_total": 29870.25, "debt": 4350.00,
    },
    {
        "key": "M", "sort": 2, "short": "М", "caption": "за последний месяц",
        "date_prefix": "",
        "axis": ["1-5", "6-10", "11-15", "16-20", "21-25", "26-30"],
        "income_shape": [0.4, 0.62, 0.5, 0.78, 0.68, 0.9],
        "expense_shape": [0.5, 0.48, 0.58, 0.52, 0.6, 0.55],
        "debt_shape": [0.4, 0.45, 0.5, 0.55, 0.6, 0.65],
        "income_max": 42000, "expense_max": 33000,
        "income_total": 178450.90, "expense_total": 129680.45, "debt": 15200.00,
    },
    {
        "key": "K", "sort": 3, "short": "К", "caption": "за последний квартал",
        "date_prefix": "",
        "axis": ["Мес 1", "Мес 2", "Мес 3"],
        "income_shape": [0.55, 0.78, 0.92],
        "expense_shape": [0.6, 0.65, 0.72],
        "debt_shape": [0.5, 0.6, 0.7],
        "income_max": 125000, "expense_max": 98000,
        "income_total": 536200.75, "expense_total": 389450.30, "debt": 42500.00,
    },
    {
        "key": "G", "sort": 4, "short": "Г", "caption": "за последний год",
        "date_prefix": "",
        "axis": ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                 "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
        "income_shape": [0.3, 0.35, 0.42, 0.5, 0.48, 0.58,
                         0.62, 0.7, 0.66, 0.78, 0.85, 0.95],
        "expense_shape": [0.4, 0.42, 0.45, 0.48, 0.5, 0.52,
                          0.55, 0.58, 0.56, 0.62, 0.65, 0.7],
        "debt_shape": [0.3, 0.32, 0.35, 0.38, 0.4, 0.45,
                       0.5, 0.55, 0.58, 0.62, 0.66, 0.7],
        "income_max": 420000, "expense_max": 330000,
        "income_total": 2104500.60, "expense_total": 1587300.20, "debt": 210000.00,
    },
    {
        "key": "V", "sort": 5, "short": "В", "caption": "за весь известный период",
        "date_prefix": "",
        "axis": ["2021", "2022", "2023", "2024", "2025", "2026"],
        "income_shape": [0.25, 0.38, 0.5, 0.62, 0.78, 0.95],
        "expense_shape": [0.3, 0.4, 0.48, 0.55, 0.62, 0.72],
        "debt_shape": [0.2, 0.32, 0.45, 0.55, 0.65, 0.75],
        "income_max": 980000, "expense_max": 760000,
        "income_total": 8452300.40, "expense_total": 6218750.85, "debt": 210000.00,
    },
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()
        # id задаём явно (0..3) — фронт нумерует пользователей с нуля,
        # иначе PostgreSQL начнёт с 1 и user=0 вернёт 404.
        db.session.add_all(User(id=i, **u) for i, u in enumerate(USERS))
        db.session.add_all(Period(**p) for p in PERIODS)
        db.session.commit()
        print(f"OK: {len(USERS)} пользователей, {len(PERIODS)} периодов.")


if __name__ == "__main__":
    seed()
