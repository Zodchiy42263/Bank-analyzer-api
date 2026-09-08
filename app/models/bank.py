from app.extensions import db


class Bank(db.Model):
    __tablename__ = "banks"

    id = db.Column(db.SmallInteger, db.Identity(start=0,  minvalue=0), primary_key=True)
    bank_name = db.Column(db.String, nullable=False)
