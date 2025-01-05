import sys
import os

# Caminho para o projeto
sys.path.insert(0, '/var/www/cofre-da-sorte')

# Caminho para o ambiente virtual
venv_path = '/var/www/cofre-da-sorte/venv/lib/python3.12/site-packages'
sys.path.insert(0, venv_path)

from app import app as application
