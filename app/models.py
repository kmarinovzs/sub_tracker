from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    hash = db.Column(db.Text, nullable=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    amount = db.Column(db.Integer)
    billing_cycle = db.Column(db.String(10))
    next_due_date = db.Column(db.DateTime)
    