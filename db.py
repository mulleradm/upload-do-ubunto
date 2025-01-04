from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import secrets

db = SQLAlchemy()

def generate_combination():
    # Gera uma combinação de 6 números aleatórios entre 1 e 60
    return '-'.join(str(secrets.randbelow(60) + 1) for _ in range(6))

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)  # Indexando username
    attempt = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Indexando timestamp

class Safe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    combination = db.Column(db.String(20), nullable=False)
    prize = db.Column(db.String(255), nullable=False)
    donor = db.Column(db.String(100), nullable=False)
    reset_time = db.Column(db.DateTime, nullable=False, index=True)  # Indexando reset_time
    winner = db.Column(db.String(100), nullable=True)  # Adicionando a coluna winner para armazenar o nome do vencedor

    def __repr__(self):
        return f'<Safe {self.id} - {self.combination}>'
