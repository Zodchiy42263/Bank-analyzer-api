from app.extensions import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.SmallInteger, db.Identity(start=0, minvalue=0), primary_key=True)
    user_id = db.Column(db.SmallInteger, db.ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    bank_id = db.Column(db.SmallInteger, db.ForeignKey("banks.id", ondelete="RESTRICT"), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(14,2), nullable=False)
    transaction_type = db.Column(db.String, nullable=False)
