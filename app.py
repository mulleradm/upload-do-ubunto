import random
from flask import Flask, render_template, request, redirect, url_for, flash  # type: ignore
from flask_migrate import Migrate  # type: ignore
from datetime import datetime, timedelta, timezone
from db import db, Attempt, Safe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cofre.db'
app.config['SECRET_KEY'] = 'sua-chave-secreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Variável global para rastrear se o cofre foi configurado
safe_initialized = False

def generate_combination():
    return '-'.join(str(random.randint(1, 60)) for _ in range(6))

@app.before_request
def setup_safe():
    """Configura o cofre antes da primeira requisição."""
    global safe_initialized
    if not safe_initialized:
        safe = Safe.query.first()
        if not safe:
            safe = Safe(
                combination=generate_combination(),
                prize="Prêmio inicial",
                donor="Doador inicial",
                reset_time=(datetime.now(timezone.utc) + timedelta(days=30))  # Certifique-se de usar timezone-aware datetime
            )
            db.session.add(safe)
            db.session.commit()
        safe_initialized = True

@app.route("/", methods=["GET", "POST"])
def index():
    safe = Safe.query.first()
    attempts = Attempt.query.all()
    message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        numbers = request.form.get("numbers", "").strip()

        # Verifica se os campos foram preenchidos
        if not username or not numbers:
            message = "Por favor, preencha todos os campos corretamente."
        else:
            # 1) Checa se o nome de usuário começa com '@'
            if not username.startswith("@"):
                message = "O nome de usuário deve começar com '@'."
            else:
                # 2) Checa se há 6 dígitos separados por vírgula
                parts = numbers.split(",")
                if len(parts) != 6:
                    message = "Por favor, selecione exatamente 6 números."
                else:
                    # -- NOVA LÓGICA: permitir 5 tentativas a cada 2 horas --
                    time_2_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
                    attempts_count = Attempt.query.filter(
                        Attempt.username == username,
                        Attempt.timestamp >= time_2_hours_ago
                    ).count()

                    if attempts_count >= 5:
                        message = (
                            "Você atingiu o limite de 5 tentativas a cada 2 horas. "
                            "Tente novamente mais tarde."
                        )
                    else:
                        # Registrar a nova tentativa
                        new_attempt = Attempt(username=username, attempt=numbers)
                        db.session.add(new_attempt)

                        if numbers == safe.combination:
                            message = f"Parabéns {username}, você acertou o cofre!"
                        else:
                            message = "Você não acertou a senha do cofre tente novamente."

                        db.session.commit()

    return render_template(
        "index.html",
        safe=safe,
        attempts=attempts,
        message=message,
    )

@app.route("/reset")
def reset_safe():
    safe = Safe.query.first()
    safe.combination = generate_combination()
    safe.reset_time = datetime.now(timezone.utc) + timedelta(days=7)  # Use timezone-aware datetime
    db.session.query(Attempt).delete()  # Remove todas as tentativas
    db.session.commit()
    flash("Cofre resetado com sucesso!")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
