from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone  # Adicionado timedelta
import secrets

db = SQLAlchemy()

def generate_combination():
    """
    Gera uma combinação de 6 números aleatórios entre 1 e 60.
    Utiliza o módulo secrets para gerar números criptograficamente seguros.
    """
    return '-'.join(str(secrets.randbelow(60) + 1) for _ in range(6))

class Attempt(db.Model):
    """
    Modelo que representa uma tentativa de abrir o cofre.
    """
    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)  # Indexando username para buscas rápidas
    attempt = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Indexando timestamp para consultas baseadas em tempo

    def __repr__(self):
        return f'<Attempt {self.username} at {self.timestamp}: {self.attempt}>'

class Safe(db.Model):
    """
    Modelo que representa o cofre.
    """
    __tablename__ = 'safes'

    id = db.Column(db.Integer, primary_key=True)
    combination = db.Column(db.String(20), nullable=False, unique=True)  # Unicidade para garantir combinações únicas
    prize = db.Column(db.String(255), nullable=False)
    donor = db.Column(db.String(100), nullable=False)
    reset_time = db.Column(db.DateTime, nullable=False, index=True)  # Indexando reset_time para consultas rápidas
    winner = db.Column(db.String(100), nullable=True)  # Armazena o nome do vencedor, se houver

    def __repr__(self):
        return f'<Safe {self.id} - {self.combination}>'

    def is_active(self):
        """
        Verifica se o cofre está ativo.
        Um cofre está ativo se não tem um vencedor e o reset_time não foi atingido.
        """
        return not self.winner and datetime.now(timezone.utc) < self.reset_time

    @classmethod
    def get_active_safe(cls):
        """
        Retorna o cofre ativo, se existir.
        """
        return cls.query.filter(cls.winner == None, cls.reset_time > datetime.now(timezone.utc)).first()

    def reset(self, new_combination=None, new_prize=None, new_donor=None, reset_days=30):
        """
        Reseta o cofre com uma nova combinação e/ou outros detalhes.
        """
        if new_combination:
            self.combination = new_combination
        else:
            self.combination = generate_combination()
        
        if new_prize:
            self.prize = new_prize
        
        if new_donor:
            self.donor = new_donor
        
        self.reset_time = datetime.now(timezone.utc) + timedelta(days=reset_days)
        self.winner = None

        db.session.commit()

# Exemplo de como inicializar o banco de dados (normalmente feito em outro lugar)
# from your_application import app
# with app.app_context():
#     db.create_all()
