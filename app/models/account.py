from app.extensions import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.SmallInteger, db.Identity(start=0,  minvalue=0), primary_key=True)
    name = db.Column(db.String, nullable=False)
    initials = db.Column(db.String, nullable=False)
    # Коэффициент масштаба пользователя (как `mult` в моке).
    mult = db.Column(db.Numeric(6, 3), nullable=False, default=1)
