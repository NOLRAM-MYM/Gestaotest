# Sistema de Gestão - Aplicação Principal
# Este arquivo é o ponto de entrada da aplicação Flask e configura todos os componentes necessários

from flask import render_template
from config import app, db

# Importação dos blueprints (módulos da aplicação)
# Cada blueprint representa uma área funcional específica do sistema
from routes.auth import auth_bp        # Autenticação e gerenciamento de usuários
from routes.products import products_bp # Gerenciamento de produtos
from routes.clients import clients_bp   # Gerenciamento de clientes
from routes.dashboard import dashboard_bp # Painel de controle e métricas
from routes.admin import admin_bp      # Funcionalidades administrativas
from routes.sales import sales_bp      # Gerenciamento de vendas

# Registro dos blueprints na aplicação
# Cada blueprint é registrado para habilitar suas rotas e funcionalidades
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(sales_bp)

# Rota principal da aplicação
@app.route('/')
def index():
    """Renderiza a página inicial do sistema"""
    return render_template('index.html')

# Inicialização da aplicação
if __name__ == '__main__':
    # Cria todas as tabelas do banco de dados definidas nos modelos
    with app.app_context():
        db.create_all()
    # Inicia o servidor de desenvolvimento
    app.run(debug=True)