from app.extensions import db


class MinimumBalanceAccount(db.Model):
    __tablename__ = "minimum_balance_accounts"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    account_name = db.Column(db.Text, nullable=False)
    balance = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    minimum_balance = db.Column(db.Numeric(14, 2), nullable=False)
    deposit_date = db.Column(db.Date, nullable=False)
