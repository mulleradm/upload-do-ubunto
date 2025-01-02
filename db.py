from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    attempt = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Safe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combination = db.Column(db.String(20), nullable=False)
    prize = db.Column(db.String(255), nullable=False)
    donor = db.Column(db.String(100), nullable=False)
    reset_time = db.Column(db.DateTime, nullable=False)