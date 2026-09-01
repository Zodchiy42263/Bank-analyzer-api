from app.extensions import db


class Deposit(db.Model):
    __tablename__ = "deposits"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    account_id = db.Column(db.SmallInteger, db.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    deposit_name = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(14,2), nullable=False)
    balance = db.synonym("amount")
    term = db.Column(db.SmallInteger, nullable=False)
    interest_rate = db.Column(db.Numeric(5,2), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    capitalization = db.Column(db.Boolean, nullable=False)
