# activate_this.py
import os
import sys

activate_this = '/var/www/cofre-da-sorte/venv/bin/activate_this.py'

# Alterar o caminho do sistema para apontar para o ambiente virtual
sys.path.insert(0, '/var/www/cofre-da-sorte/venv/lib/python3.12/site-packages')

# Ativa o ambiente virtual
exec(open(activate_this).read(), {'__file__': activate_this})
