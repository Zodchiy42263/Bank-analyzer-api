from app.extensions import db


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    contract_number = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    term = db.Column(db.SmallInteger, nullable=False)
    overpayment = db.Column(db.Numeric(14, 2), nullable=False)
