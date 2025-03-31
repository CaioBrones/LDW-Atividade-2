from flask import Flask, render_template
from controllers import routes
import requests

# Criando a instância do Flask na variável app
app = Flask(__name__, template_folder='views')
routes.init_app(app)

# Iniciar o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
