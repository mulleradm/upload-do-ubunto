import os
import sys

# Caminho para o ambiente virtual
activate_this = '/var/www/cofre-da-sorte/venv/bin/activate_this.py'

# Verifica se o arquivo de ativação do ambiente virtual existe
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})
else:
    sys.exit("O arquivo 'activate_this.py' não foi encontrado!")
