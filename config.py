# Sistema de Gestão - Configurações
# Este arquivo contém todas as configurações e inicializações necessárias
# para o funcionamento do sistema

from flask import Flask
from flask_sqlalchemy import SQLAlchemy      # ORM para banco de dados
from flask_login import LoginManager         # Gerenciamento de autenticação
from flask_bcrypt import Bcrypt              # Criptografia de senhas
from flask_mail import Mail                  # Envio de emails
from flask_wtf.csrf import CSRFProtect       # Proteção contra CSRF
from flask_migrate import Migrate            # Migrações do banco de dados
import os

# Criação da aplicação Flask
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vision_database_user:1bnnPrnMf4Vb4qTNAlVdIc0JdXtFBi9v@dpg-cvsgcl49c44c73a27cig-a.oregon-postgres.render.com/vision_database'

# Configurações básicas da aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Chave secreta para sessões
# Configuração do banco de dados com fallback para SQLite local
try:
    # Tenta usar o banco de dados de produção se a URL estiver configurada
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    else:
        # Se não houver URL de produção, usa SQLite local
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestao.db'
        print('INFO: Usando banco de dados SQLite local')
except Exception as e:
    # Em caso de erro de conexão, usa SQLite local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestao.db'
    print(f'AVISO: Erro ao conectar ao banco de dados de produção: {str(e)}')
    print('INFO: Usando banco de dados SQLite local como fallback')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False         # Desativa modificações do SQLAlchemy
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')  # Pasta para uploads

# Configurações do servidor de email (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'white.as.snow.ws@gmail.com'
app.config['MAIL_PASSWORD'] = 'khgb nwit vpjv hsoh'
# Configurar remetente padrão
default_sender = ('Sistema de Gestão', 'white.as.snow.ws@gmail.com')
app.config['MAIL_DEFAULT_SENDER'] = default_sender

# Configurar timeout do SMTP
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_TIMEOUT'] = 10
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Verificar se as configurações de email estão presentes
if not all([app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']]):
    print('AVISO: Variáveis de ambiente EMAIL_USER e EMAIL_PASS não configuradas.')
    print('As funcionalidades de email (como recuperação de senha) não estarão disponíveis.')
    app.config['MAIL_SUPPRESS_SEND'] = True  # Desativa o envio de emails
else:
    app.config['MAIL_SUPPRESS_SEND'] = False  # Ativa o envio de emails

# Inicialização das extensões Flask
db = SQLAlchemy(app)                # Banco de dados
bcrypt = Bcrypt(app)               # Criptografia
login_manager = LoginManager(app)   # Gerenciador de login
mail = Mail(app)                   # Serviço de email
csrf = CSRFProtect(app)            # Proteção CSRF
migrate = Migrate(app, db)         # Sistema de migrações

# Custom Jinja2 filters
def file_exists(url):
    if not url:
        return False
    file_path = os.path.join(os.path.dirname(__file__), url.lstrip('/'))
    return os.path.exists(file_path)

app.jinja_env.filters['exists'] = file_exists

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Criação da pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])