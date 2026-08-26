"""
Bank Analyzer — референс-бэкенд под фронтенд Bank-analyzer-ui.

Отдельный сервис/репозиторий. Отдаёт данные в ТОЧНО такой форме, какую ждут
компоненты фронта (см. README → «Контракт»). Схема PostgreSQL повторяет структуру
моков фронтенда, поэтому графики работают без единой правки в UI.

Эндпоинты:
    GET /api/accounts
    GET /api/overview?user=<id>&period=<D|N|M|K|G|V>
    GET /api/health
"""

import os

from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/bank",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ── Модели ────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.SmallInteger, db.Identity(start=0,  minvalue=0), primary_key=True)
    name = db.Column(db.String, nullable=False)
    initials = db.Column(db.String, nullable=False)
    balance = db.Column(db.Numeric(14, 2), nullable=False)
    # Коэффициент масштаба пользователя (как `mult` в моке).
    mult = db.Column(db.Numeric(6, 3), nullable=False, default=1)


class Bank(db.Model):
    __tablename__ = "banks"

    id = db.Column(db.SmallInteger, db.Identity(start=0,  minvalue=0), primary_key=True)
    name = db.Column(db.String, nullable=False)


class DebitCard(db.Model):
    __tablename__ = "debit_cards"

    id = db.Column(db.SmallInteger, db.Identity(start=0,  minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    account_name = db.Column(db.Text, nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    balance_rub = db.Column(db.Numeric(14,2), nullable=False)
    balance_usd = db.Column(db.Numeric(14,2), nullable=False)
    balance_eur = db.Column(db.Numeric(14,2), nullable=False)
    cashback = db.Column(db.Numeric(14,2), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    record_date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "account_number ~ '^[0-9]{20}$'",
            name="check_account_format"
        ),
    )


class Deposit(db.Model):
    __tablename__ = "deposits"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    deposit_name = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(14,2), nullable=False)
    term = db.Column(db.SmallInteger, nullable=False)
    interest_rate = db.Column(db.Numeric(5,2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    capitalization = db.Column(db.Boolean, nullable=False)


class SavingsAccount(db.Model):
    __tablename__ = "savings_accounts"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    account_name = db.Column(db.Text, nullable=False)
    balance = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)


class MinBalanceAccount(db.Model):
    __tablename__ = "minimum_balance_accounts"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    account_name = db.Column(db.Text, nullable=False)
    balance = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    minimum_balance = db.Column(db.Numeric(14, 2), nullable=False)
    deposit_date = db.Column(db.Date, nullable=False)


class CreditCard(db.Model):
    __tablename__ = "credit_cards"

    id = db.Column(db.SmallInteger, db.Identity(start=0,  minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    account_name = db.Column(db.Text, nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    balance_rub = db.Column(db.Numeric(14,2), nullable=False)
    balance_usd = db.Column(db.Numeric(14,2), nullable=False)
    balance_eur = db.Column(db.Numeric(14,2), nullable=False)
    credit_limit = db.Column(db.Numeric(14,2), nullable=False)
    debt = db.Column(db.Numeric(14,2), nullable=False)
    nearest_debt_date = db.Column(db.Date, nullable=False)
    last_debt_date = db.Column(db.Date, nullable=False)
    cashback = db.Column(db.Numeric(14,2), nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)
    record_date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            "account_number ~ '^[0-9]{20}$'",
            name="check_account_format"
        ),
    )


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    contract_number = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    term = db.Column(db.SmallInteger, nullable=False)
    overpayment = db.Column(db.Numeric(14, 2), nullable=False)


class Period(db.Model):
    __tablename__ = "periods"

    key = db.Column(db.String(1), primary_key=True)  # D N M K G V
    sort = db.Column(db.Integer, nullable=False, default=0)
    short = db.Column(db.String(2), nullable=False)
    caption = db.Column(db.String, nullable=False)
    date_prefix = db.Column(db.String, nullable=False, default="")
    axis = db.Column(db.JSON, nullable=False)
    income_shape = db.Column(db.JSON, nullable=False)
    expense_shape = db.Column(db.JSON, nullable=False)
    debt_shape = db.Column(db.JSON, nullable=False)
    income_max = db.Column(db.Numeric(14, 2), nullable=False)
    expense_max = db.Column(db.Numeric(14, 2), nullable=False)
    income_total = db.Column(db.Numeric(14, 2), nullable=False)
    expense_total = db.Column(db.Numeric(14, 2), nullable=False)
    debt = db.Column(db.Numeric(14, 2), nullable=False)


# Разбивка активов: доля от баланса + цвет (как в моке фронтенда).
ASSET_BREAKDOWN = [
    ("Вклады", 0.45, "hsl(150, 30%, 46%)"),
    ("Дебетовые счета", 0.25, "hsl(95, 26%, 52%)"),
    ("Инвестиции", 0.30, "hsl(210, 35%, 55%)"),
]


# ── Эндпоинты ───────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/accounts")
def accounts():
    users = User.query.order_by(User.id).all()
    return jsonify(
        [
            {
                "id": u.id,
                "name": u.name,
                "initials": u.initials,
                "balance": float(u.balance),
            }
            for u in users
        ]
    )

@app.get("/api/overview")
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


if __name__ == "__main__":
    # Flask dev-сервер слушает 5000 — совпадает с proxy.target во фронте.
    app.run(host="0.0.0.0", port=5000, debug=True)
