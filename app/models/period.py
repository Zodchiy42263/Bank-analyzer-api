from app.extensions import db


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
