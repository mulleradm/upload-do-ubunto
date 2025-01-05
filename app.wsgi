import sys
import os

# Adiciona o caminho do projeto para o sys.path
sys.path.insert(0, '/var/www/cofre-da-sorte')

# Ativa o ambiente virtual, se necessário
activate_this = '/var/www/cofre-da-sorte/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Agora importa o app
from app import app as application
