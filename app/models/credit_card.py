from app.extensions import db


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
