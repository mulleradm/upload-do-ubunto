import random
import csv
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, send_file, abort
from flask_migrate import Migrate
from markupsafe import Markup
from flask_wtf import FlaskForm
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from db import db, Attempt, Safe
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length
import requests
from googleapiclient.discovery import build

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração básica do Flask
app = Flask(__name__)

# Configuração do Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cofre.db'  # Caminho para o banco de dados
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Usando a variável do .env
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração do Google reCAPTCHA
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')

# Iniciar banco de dados e migrações
db.init_app(app)
migrate = Migrate(app, db)

# Variável global para rastrear se o cofre foi configurado
safe_initialized = False

# Função para gerar a combinação de números
def generate_combination():
    return '-'.join(str(random.randint(1, 60)) for _ in range(6))

# Configuração de logs para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função que configura o cofre antes da primeira requisição
@app.before_request
def setup_safe():
    """Configura o cofre antes da primeira requisição."""
    global safe_initialized
    if not safe_initialized:
        try:
            # Tenta obter o primeiro registro do cofre
            safe = Safe.query.first()

            # Se não existir um cofre, cria um novo
            if not safe:
                safe = Safe(
                    combination=generate_combination(),
                    prize="Prêmio inicial",
                    donor="Doador inicial",
                    reset_time=datetime.now(timezone.utc) + timedelta(days=30)  # Certifique-se de usar datetime com fuso horário
                )
                db.session.add(safe)
                db.session.commit()
                logging.info("Cofre configurado com sucesso!")
        except Exception as e:
            # Caso ocorra algum erro, loga a mensagem de erro
            logging.error(f"Erro ao configurar o cofre: {e}")

        safe_initialized = True

# Função que verifica o token do reCAPTCHA usando a API do Google
def verify_recaptcha(token: str, recaptcha_action: str) -> bool:
    """Verifica o token do reCAPTCHA usando a API do Google."""
    
    # Configuração do cliente Google API
    service = build('recaptchaenterprise', 'v1', developerKey=os.getenv('RECAPTCHA_PRIVATE_KEY'))

    # Corpo da solicitação
    recaptcha_data = {
        "event": {
            "token": token,
            "expectedAction": recaptcha_action,
            "siteKey": os.getenv("RECAPTCHA_PUBLIC_KEY"),
        }
    }

    # Enviar solicitação para a API do Google
    url = f"https://recaptchaenterprise.googleapis.com/v1/projects/{os.getenv('GOOGLE_CLOUD_PROJECT_ID')}/assessments?key={os.getenv('RECAPTCHA_PRIVATE_KEY')}"
    response = requests.post(url, json=recaptcha_data)

    if response.status_code != 200:
        logging.error("Erro ao validar o reCAPTCHA")
        return False
    
    result = response.json()

    # Verifique a pontuação e se a ação corresponde
    if result.get("tokenProperties", {}).get("valid") and result["tokenProperties"].get("action") == recaptcha_action:
        logging.info(f"A pontuação de risco para este token é: {result['riskAnalysis']['score']}")
        return True
    else:
        logging.error("Falha na validação do reCAPTCHA.")
        return False

# Definição do formulário para tentar abrir o cofre
class AttemptForm(FlaskForm):
    username = StringField('Seu @ do Instagram', validators=[InputRequired(), Length(min=3)])
    recaptcha = StringField('reCAPTCHA', validators=[InputRequired()])
    submit = SubmitField('Tentar Abrir o Cofre')

# Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    safe = Safe.query.first()
    attempts = Attempt.query.all()

    # Verifica se o cofre já foi aberto (se há um vencedor)
    if safe.winner:
        flash("O cofre já foi aberto! Aguardando o próximo reset.", "info")
        return render_template("index.html", safe=safe, attempts=attempts)

    form = AttemptForm()

    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data.strip()
        numbers = request.form.get("numbers", "").strip()
        recaptcha_response = request.form.get('g-recaptcha-response')

        # Substitua pelas suas variáveis
        recaptcha_action = "LOGIN"  # Ação definida ao configurar o reCAPTCHA

        # Verifica o reCAPTCHA usando a função verify_recaptcha
        if not verify_recaptcha(recaptcha_response, recaptcha_action):
            flash('Falha na validação do reCAPTCHA. Tente novamente.', 'error')
            return redirect(url_for('index'))

        # Verifica se os campos foram preenchidos corretamente
        if not username:
            flash("Por favor, preencha o seu @ do Instagram.", "error")
        elif not numbers:
            flash("Por favor, selecione os números antes de tentar abrir o cofre.", "error")
        else:
            # 1) Checa se o nome de usuário começa com '@'
            if not username.startswith("@"):
                flash("O nome de usuário deve começar com '@'.", "error")
            else:
                # 2) Checa se há 6 números separados por vírgula
                parts = numbers.split(",")
                if len(parts) != 6:
                    flash("Por favor, selecione exatamente 6 números.", "error")
                else:
                    # -- NOVA LÓGICA: permitir 5 tentativas a cada 2 horas --
                    time_2_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
                    attempts_count = Attempt.query.filter(
                        Attempt.username == username,
                        Attempt.timestamp >= time_2_hours_ago
                    ).count()

                    # Se o usuário atingiu o limite de tentativas
                    if attempts_count >= 5:
                        flash("Você atingiu o limite de 5 tentativas a cada 2 horas. Tente novamente mais tarde.", "error")
                    else:
                        # Registrar a nova tentativa
                        new_attempt = Attempt(username=username, attempt=numbers)
                        db.session.add(new_attempt)

                        if numbers == safe.combination:
                            # Marca o vencedor no banco de dados
                            safe.winner = username
                            db.session.commit()
                            flash(f"Parabéns {username}, você acertou o cofre!", "success")
                        else:
                            flash("Você não acertou a senha do cofre. Tente novamente.", "error")

                        db.session.commit()

        # Após o POST, redireciona para a página principal (GET)
        return redirect(url_for('index'))  # Redireciona para a página inicial

    return render_template("index.html", safe=safe, attempts=attempts, form=form)

# Função para exportar auditoria
@app.route("/exportar_auditoria", methods=["GET"])
def exportar_auditoria():
    # Verifica se a aplicação está rodando em ambiente de desenvolvimento
    if os.environ.get("FLASK_ENV") != "development":
        abort(403)  # Se não estiver em desenvolvimento, retorna erro 403 (proibido)

    # Consultar todas as tentativas do banco de dados
    attempts = Attempt.query.all()

    # Criar o arquivo CSV
    filename = "tentativas.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Data/Hora", "Usuário", "Tentativa"])  # Cabeçalho do CSV

        # Adicionar as tentativas ao CSV
        for attempt in attempts:
            writer.writerow([attempt.timestamp.strftime('%d/%m/%Y %H:%M:%S'), attempt.username, attempt.attempt])

    # Enviar o arquivo CSV gerado para o usuário
    return send_file(filename, as_attachment=True)

# Função para resetar o cofre
@app.route("/reset")
def reset_safe():
    try:
        # Recupera o primeiro cofre, se existir
        safe = Safe.query.first()
        
        if safe:
            # Gera uma nova combinação
            safe.combination = generate_combination()
            
            # Atualiza o tempo de reset
            safe.reset_time = datetime.now(timezone.utc) + timedelta(days=30)
            
            # Limpa o vencedor para permitir novas tentativas
            safe.winner = None
            
            # Salva as alterações no banco de dados
            db.session.commit()

            # Feedback de sucesso para o usuário
            flash("Cofre resetado com sucesso!")
        else:
            flash("Cofre não encontrado.", "error")  # Caso não exista um cofre

    except Exception as e:
        # Registra erro e avisa o usuário
        db.session.rollback()  # Reverte qualquer alteração no banco em caso de erro
        flash(f"Erro ao resetar o cofre: {str(e)}", "error")
    
    # Redireciona para a página principal após o reset
    return redirect(url_for("index"))

# Rodar o aplicativo Flask
if __name__ == "__main__":
    app.run(debug=True)
