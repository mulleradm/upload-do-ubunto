import sys
import os

# Caminho para o projeto
sys.path.insert(0, '/var/www/cofre-da-sorte')

# Caminho para o ambiente virtual
sys.path.insert(0, '/var/www/cofre-da-sorte/venv/lib/python3.12/site-packages')

from app import app as application
