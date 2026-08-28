from app.extensions import db


class SavingsAccount(db.Model):
    __tablename__ = "savings_accounts"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    account_id = db.Column(db.SmallInteger, db.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    account_name = db.Column(db.Text, nullable=False)
    balance = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
