import sys
import os

# Caminho para o projeto
sys.path.insert(0, '/var/www/cofre-da-sorte')

# Caminho para o ambiente virtual
activate_this = '/var/www/cofre-da-sorte/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

from app import app as application
