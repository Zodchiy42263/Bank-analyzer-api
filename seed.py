"""
Создаёт таблицы и наполняет БД данными, повторяющими моки фронтенда.
Запуск:  python seed.py
"""
import time
import subprocess

from run import create_app
from app.extensions import db
from app.models.account import Account
from app.models.bank import Bank
from app.models.debit_card import DebitCard
from app.models.deposit import Deposit
from app.models.saving_account import SavingsAccount
from app.models.minimum_balance_account import MinimumBalanceAccount
from app.models.credit_card import CreditCard
from app.models.loan import Loan
from app.models.transaction import Transaction
from app.models.period import Period
from app.constants.transactions import TRANSACTION_TYPES

ACCOUNTS = [
    {"account_name": "Симанин Антон", "initials": "СА", "mult": 1.00},
    {"account_name": "Симанина Анастасия", "initials": "СА", "mult": 1.00},
]

BANKS = [
    {"bank_name": "Озон"},
    {"bank_name": "Яндекс"},
    {"bank_name": "Сбер"},
    {"bank_name": "Альфа"},
    {"bank_name": "ВТБ"},
    {"bank_name": "Т-Банк"},
]

DEBIT_CARDS = [
    {
        "account_id": 0,
        "bank_id": 0,
        "account_name": "Повседневный",
        "account_number": "40817810300006667778",
        "balance_rub": 185450.50,
        "balance_usd": 2318.13,
        "balance_eur": 1994.09,
        "cashback": 8.50,
        "expiration_date": "2027-03-15 00:00:00",
        "record_date": "2026-08-20",
    },
    {
        "account_id": 0,
        "bank_id": 1,
        "account_name": "Зарплатный",
        "account_number": "40817810300007778889",
        "balance_rub": 324800.00,
        "balance_usd": 4060.00,
        "balance_eur": 3492.47,
        "cashback": 11.20,
        "expiration_date": "2028-01-10 00:00:00",
        "record_date": "2026-08-21",
    },
    {
        "account_id": 1,
        "bank_id": 2,
        "account_name": "Покупки",
        "account_number": "40817810300008889990",
        "balance_rub": 72850.75,
        "balance_usd": 910.63,
        "balance_eur": 783.34,
        "cashback": 6.75,
        "expiration_date": "2027-09-25 00:00:00",
        "record_date": "2026-08-22",
    },
    {
        "account_id": 1,
        "bank_id": 3,
        "account_name": "Путешествия",
        "account_number": "40817810300009990001",
        "balance_rub": 156300.00,
        "balance_usd": 1953.75,
        "balance_eur": 1680.65,
        "cashback": 14.30,
        "expiration_date": "2029-05-30 00:00:00",
        "record_date": "2026-08-23",
    },
]

DEPOSITS = [
    {
        "account_id": 0,
        "bank_id": 0,
        "deposit_name": "Надёжный доход",
        "amount": 500000.00,
        "term": 12,
        "interest_rate": 15.50,
        "start_date": "2026-02-15 00:00:00",
        "end_date": "2027-02-15 00:00:00",
        "capitalization": True,
    },
    {
        "account_id": 0,
        "bank_id": 1,
        "deposit_name": "Короткий срок",
        "amount": 250000.00,
        "term": 6,
        "interest_rate": 14.75,
        "start_date": "2026-06-10 00:00:00",
        "end_date": "2026-12-10 00:00:00",
        "capitalization": False,
    },
    {
        "account_id": 1,
        "bank_id": 3,
        "deposit_name": "Семейный капитал",
        "amount": 800000.00,
        "term": 24,
        "interest_rate": 13.25,
        "start_date": "2026-01-20 00:00:00",
        "end_date": "2028-01-20 00:00:00",
        "capitalization": True,
    },
    {
        "account_id": 1,
        "bank_id": 5,
        "deposit_name": "Накопительный вклад",
        "amount": 350000.00,
        "term": 3,
        "interest_rate": 16.00,
        "start_date": "2026-08-05 00:00:00",
        "end_date": "2026-11-05 00:00:00",
        "capitalization": False,
    },
]

SAVINGS_ACCOUNTS = [
    {
        "account_id": 0,
        "bank_id": 1,
        "account_name": "Накопительный счёт",
        "balance": 350000.00,
        "interest_rate": 12.50,
    },
    {
        "account_id": 1,
        "bank_id": 1,
        "account_name": "Накопления Плюс",
        "balance": 780000.00,
        "interest_rate": 13.00,
    },
    {
        "account_id": 1,
        "bank_id": 2,
        "account_name": "Доходный счёт",
        "balance": 125000.00,
        "interest_rate": 10.50,
    },
    {
        "account_id": 0,
        "bank_id": 3,
        "account_name": "Финансовая подушка",
        "balance": 920000.00,
        "interest_rate": 11.75,
    },
]

MIN_BALANCE_ACCOUNTS = [
    {
        "account_id": 1,
        "bank_id": 0,
        "account_name": "Стабильный доход",
        "balance": 600000.00,
        "interest_rate": 14.00,
        "minimum_balance": 100000.00,
        "deposit_date": "2026-01-20 00:00:00",
    },
    {
        "account_id": 1,
        "bank_id": 2,
        "account_name": "Накопительный максимум",
        "balance": 950000.00,
        "interest_rate": 15.25,
        "minimum_balance": 200000.00,
        "deposit_date": "2025-11-10 00:00:00",
    },
    {
        "account_id": 0,
        "bank_id": 4,
        "account_name": "Резервный капитал",
        "balance": 420000.00,
        "interest_rate": 12.75,
        "minimum_balance": 50000.00,
        "deposit_date": "2026-03-05 00:00:00",
    },
    {
        "account_id": 0,
        "bank_id": 1,
        "account_name": "Финансовый резерв",
        "balance": 1500000.00,
        "interest_rate": 13.50,
        "minimum_balance": 300000.00,
        "deposit_date": "2024-09-18 00:00:00",
    },
]

CREDIT_CARDS = [
    {
        "account_id": 0,
        "bank_id": 0,
        "account_name": "Основная кредитная",
        "account_number": "40817810300012223334",
        "balance_rub": 125000.00,
        "balance_usd": 1562.50,
        "balance_eur": 1344.09,
        "credit_limit": 209750.00,
        "debt": 84750.00,
        "nearest_debt_date": "2026-09-15 00:00:00",
        "last_debt_date": "2026-10-06 00:00:00",
        "cashback": 7.50,
        "expiration_date": "2029-04-30 00:00:00",
        "record_date": "2026-08-25 00:00:00",
    },
    {
        "account_id": 0,
        "bank_id": 1,
        "account_name": "Кредитная для покупок",
        "account_number": "40817810300023334455",
        "balance_rub": 48300.00,
        "balance_usd": 603.75,
        "balance_eur": 519.35,
        "credit_limit": 81080.50,
        "debt": 32780.50,
        "nearest_debt_date": "2026-09-10 00:00:00",
        "last_debt_date": "2026-09-30 00:00:00",
        "cashback": 5.00,
        "expiration_date": "2028-11-20 00:00:00",
        "record_date": "2026-08-25 00:00:00",
    },
    {
        "account_id": 1,
        "bank_id": 3,
        "account_name": "Кредитная для путешествий",
        "account_number": "40817810300034445566",
        "balance_rub": 210000.00,
        "balance_usd": 2625.00,
        "balance_eur": 2258.06,
        "credit_limit": 406450.00,
        "debt": 196450.00,
        "nearest_debt_date": "2026-09-20 00:00:00",
        "last_debt_date": "2026-10-12 00:00:00",
        "cashback": 10.00,
        "expiration_date": "2030-02-28 00:00:00",
        "record_date": "2026-08-25 00:00:00",
    },
    {
        "account_id": 1,
        "bank_id": 5,
        "account_name": "Резервная кредитная",
        "account_number": "40817810300045556677",
        "balance_rub": 76500.00,
        "balance_usd": 956.25,
        "balance_eur": 822.58,
        "credit_limit": 118600.00,
        "debt": 42100.00,
        "nearest_debt_date": "2026-09-05 00:00:00",
        "last_debt_date": "2026-09-26 00:00:00",
        "cashback": 3.50,
        "expiration_date": "2027-12-15 00:00:00",
        "record_date": "2026-08-25 00:00:00",
    },
]

LOANS = [
    {
        "account_id": 0,
        "bank_id": 4,
        "contract_number": "LN-2026-0001",
        "amount": 3000000.00,
        "interest_rate": 19.00,
        "term": 180,
        "overpayment": 6080000.00,
    },
    {
        "account_id": 1,
        "bank_id": 1,
        "contract_number": "LN-2025-0042",
        "amount": 1500000.00,
        "interest_rate": 17.50,
        "term": 120,
        "overpayment": 1660000.00,
    },
    {
        "account_id": 0,
        "bank_id": 3,
        "contract_number": "LN-2026-0018",
        "amount": 800000.00,
        "interest_rate": 21.00,
        "term": 60,
        "overpayment": 510000.00,
    },
    {
        "account_id": 1,
        "bank_id": 0,
        "contract_number": "LN-2024-0137",
        "amount": 4500000.00,
        "interest_rate": 16.90,
        "term": 240,
        "overpayment": 9150000.00,
    },
]

PERIODS = [
    {
        "key": "D", "sort": 0, "short": "Д", "caption": "за сегодня",
        "date_prefix": "Сегодня, ",
        "axis": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
        "income_shape": [0.32, 0.55, 0.38, 0.72, 0.9, 0.61],
        "expense_shape": [0.48, 0.4, 0.58, 0.44, 0.62, 0.5],
        "debt_shape": [0.55, 0.5, 0.58, 0.6, 0.62, 0.65],
        "income_max": 7000.00, "expense_max": 5000.00,
        "income_total": 6420.35, "expense_total": 4380.90, "debt": 4200.00,
    },
    {
        "key": "N", "sort": 1, "short": "Н", "caption": "за последнюю неделю",
        "date_prefix": "",
        "axis": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "income_shape": [0.35, 0.5, 0.42, 0.68, 0.6, 0.82, 0.55],
        "expense_shape": [0.45, 0.42, 0.5, 0.48, 0.55, 0.6, 0.5],
        "debt_shape": [0.45, 0.5, 0.48, 0.55, 0.58, 0.6, 0.63],
        "income_max": 9300, "expense_max": 6800,
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

TRANSACTIONS = [
    {
        "account_id": 0,
        "bank_id": 0,
        "record_date": "2014-09-02 02:30:00",
        "amount": 1050.00,
        "type": TRANSACTION_TYPES["income"][3]
    },
    {
        "account_id": 0,
        "bank_id": 0,
        "record_date": "2017-12-31 23:30:00",
        "amount": 4650.00,
        "type": TRANSACTION_TYPES["income"][3]
    },
    {
        "account_id": 0,
        "bank_id": 0,
        "record_date": "2021-02-01 14:07:00",
        "amount": 1250.00,
        "type": TRANSACTION_TYPES["income"][3]
    },
    {
        "account_id": 0,
        "bank_id": 0,
        "record_date": "2026-09-02 02:30:00",
        "amount": 3050.00,
        "type": TRANSACTION_TYPES["income"][3]
    },
    {
        "account_id": 0,
        "bank_id": 4,
        "record_date": "2026-09-02 11:05:43",
        "amount": 626.23,
        "type": TRANSACTION_TYPES["income"][0]
    },
    {
        "account_id": 0,
        "bank_id": 2,
        "record_date": "2026-09-02 17:53:46",
        "amount": 700.60,
        "type": TRANSACTION_TYPES["income"][4]
    },
    {
        "account_id": 0,
        "bank_id": 0,
        "record_date": "2026-09-02 23:06:54",
        "amount": 7000.10,
        "type": TRANSACTION_TYPES["income"][1]
    },
    {
        "account_id": 0,
        "bank_id": 4,
        "record_date": "2026-09-02 04:06:54",
        "amount": 15000.00,
        "type": TRANSACTION_TYPES["income"][6]
    },
    {
        "account_id": 0,
        "bank_id": 3,
        "record_date": "2026-09-02 06:40:14",
        "amount": 1724.50,
        "type": TRANSACTION_TYPES["expense"][1]
    },
    {
        "account_id": 0,
        "bank_id": 2,
        "record_date": "2026-09-02 14:36:04",
        "amount": 368.50,
        "type": TRANSACTION_TYPES["expense"][0]
    },

    {
        "account_id": 0,
        "bank_id": 5,
        "record_date": "2026-09-02 21:29:42",
        "amount": 456.17,
        "type": TRANSACTION_TYPES["expense"][1]
    },
    {
        "account_id": 0,
        "bank_id": 3,
        "record_date": "2026-09-03 02:30:00",
        "amount": 1450.00,
        "type": TRANSACTION_TYPES["income"][0]
    },
    {
        "account_id": 0,
        "bank_id": 5,
        "record_date": "2026-09-03 11:05:43",
        "amount": 516.23,
        "type": TRANSACTION_TYPES["income"][4]
    },
    {
        "account_id": 0,
        "bank_id": 2,
        "record_date": "2026-09-03 17:53:46",
        "amount": 700.60,
        "type": TRANSACTION_TYPES["income"][3]
    },
    {
        "account_id": 0,
        "bank_id": 0,
        "record_date": "2026-09-03 23:06:54",
        "amount": 7000.00,
        "type": TRANSACTION_TYPES["income"][1]
    },
    {
        "account_id": 0,
        "bank_id": 4,
        "record_date": "2026-09-03 03:15:54",
        "amount": 100000.00,
        "type": TRANSACTION_TYPES["income"][6]
    },
    {
        "account_id": 0,
        "bank_id": 1,
        "record_date": "2026-09-03 05:55:04",
        "amount": 450.00,
        "type": TRANSACTION_TYPES["expense"][1]
    },
    {
        "account_id": 0,
        "bank_id": 4,
        "record_date": "2026-09-03 12:30:04",
        "amount": 259.00,
        "type": TRANSACTION_TYPES["expense"][0]
    },
    {
        "account_id": 0,
        "bank_id": 4,
        "record_date": "2026-09-04 02:29:42",
        "amount": 1470.17,
        "type": TRANSACTION_TYPES["expense"][0]
    },
    {
        "account_id": 0,
        "bank_id": 1,
        "record_date": "2026-09-05 07:29:42",
        "amount": 175.17,
        "type": TRANSACTION_TYPES["expense"][1]
    },
    {
        "account_id": 0,
        "bank_id": 3,
        "record_date": "2026-09-05 07:29:42",
        "amount": 325.47,
        "type": TRANSACTION_TYPES["income"][4]
    },
]


app = create_app()

def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add_all(Account(**account) for account in ACCOUNTS)
        db.session.flush()

        db.session.add_all(Bank(**bank) for bank in BANKS)
        db.session.flush()

        db.session.add_all(DebitCard(**d_card) for d_card in DEBIT_CARDS)

        db.session.add_all(Deposit(**deposit) for deposit in DEPOSITS)

        db.session.add_all(SavingsAccount(**saving_account) for saving_account in SAVINGS_ACCOUNTS)

        db.session.add_all(
            MinimumBalanceAccount(**minimum_balance_account) for minimum_balance_account in MIN_BALANCE_ACCOUNTS
        )

        db.session.add_all(CreditCard(**c_card) for c_card in CREDIT_CARDS)

        db.session.add_all(Loan(**loan) for loan in LOANS)

        db.session.add_all(Period(**period) for period in PERIODS)

        db.session.add_all(Transaction(**transaction) for transaction in TRANSACTIONS)

        db.session.commit()
        print(f"OK: {len(ACCOUNTS)} пользователей, {len(PERIODS)} периодов.")


if __name__ == "__main__":
    subprocess.run("docker start bank-pg")
    time.sleep(2)
    seed()
