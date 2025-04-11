# Sistema de Gestão - Modelos de Dados
# Este arquivo define a estrutura do banco de dados através dos modelos SQLAlchemy

from datetime import datetime
from flask_login import UserMixin
from config import db, login_manager

# Função necessária para o Flask-Login carregar o usuário da sessão
@login_manager.user_loader
def load_user(user_id):
    """Carrega um usuário pelo ID para o Flask-Login"""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Modelo para usuários do sistema
    
    Armazena informações de autenticação e perfil dos usuários,
    incluindo administradores e usuários comuns.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Nome de usuário único
    email = db.Column(db.String(120), unique=True, nullable=False)   # Email único
    password = db.Column(db.String(128), nullable=False)             # Senha criptografada
    is_admin = db.Column(db.Boolean, default=False)                 # Flag de administrador
    created_at = db.Column(db.DateTime, default=datetime.utcnow)    # Data de criação
    deleted_at = db.Column(db.DateTime, nullable=True)              # Data de exclusão (soft delete)
    
    @property
    def is_deleted(self):
        """Verifica se o usuário está marcado como excluído"""
        return self.deleted_at is not None
    
    def soft_delete(self):
        """Marca o usuário como excluído sem removê-lo do banco de dados"""
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        """Restaura um usuário previamente marcado como excluído"""
        self.deleted_at = None
        db.session.commit()
    
    @classmethod
    def get_active_users(cls):
        """Retorna apenas usuários não excluídos"""
        return cls.query.filter_by(deleted_at=None)

class ProductImage(db.Model):
    """Modelo para imagens de produtos
    
    Permite armazenar múltiplas imagens para cada produto,
    mantendo o conteúdo binário da imagem e metadados.
    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Relacionamento com Produto
    image_data = db.Column(db.LargeBinary, nullable=False)                         # Conteúdo binário da imagem
    mime_type = db.Column(db.String(128), nullable=False)                          # Tipo MIME da imagem
    created_at = db.Column(db.DateTime, default=datetime.utcnow)                   # Data de upload

class Category(db.Model):
    """Modelo para categorias de produtos
    
    Permite organizar produtos em categorias específicas
    para melhor organização e filtragem.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # Nome da categoria
    description = db.Column(db.Text)                            # Descrição da categoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com produtos
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    """Modelo para produtos
    
    Gerencia o catálogo de produtos com informações detalhadas,
    incluindo preços, estoque e custos associados.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)      # Nome do produto
    description = db.Column(db.Text)                     # Descrição detalhada
    price = db.Column(db.Float, nullable=False)          # Preço de venda
    stock = db.Column(db.Integer, default=0)            # Quantidade em estoque
    is_active = db.Column(db.Boolean, default=True)     # Status de ativação
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Data de criação
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última atualização
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)  # Data de entrada no estoque
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))  # Relacionamento com categoria
    # Custos associados ao produto
    custo1 = db.Column(db.Float, nullable=True, default=0.0)  # Custo principal
    custo2 = db.Column(db.Float, nullable=True, default=0.0)  # Custo adicional 1
    custo3 = db.Column(db.Float, nullable=True, default=0.0)  # Custo adicional 2
    custo4 = db.Column(db.Float, nullable=True, default=0.0)  # Custo adicional 3
    custo5 = db.Column(db.Float, nullable=True, default=0.0)  # Custo adicional 4
    
    # Relacionamento com as imagens do produto
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def update_status(self):
        """Atualiza o status do produto baseado no estoque"""
        self.is_active = self.stock > 0
        
    def total_custos(self):
        """Calcula o custo total do produto somando todos os custos"""
        return self.custo1 + self.custo2 + self.custo3 + self.custo4 + self.custo5

class ClientImage(db.Model):
    """Modelo para imagens de clientes
    
    Armazena documentos e imagens relacionadas aos clientes,
    como documentos de identificação e comprovantes.
    """
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)  # Relacionamento com Cliente
    image_data = db.Column(db.LargeBinary, nullable=False)                       # Conteúdo binário da imagem
    mime_type = db.Column(db.String(128), nullable=False)                        # Tipo MIME da imagem
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Client(db.Model):
    """Modelo para clientes
    
    Armazena informações dos clientes, incluindo dados de contato
    e documentação no Japão.
    """
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)     # Nome completo do cliente
    japan_address = db.Column(db.String(200))               # Endereço no Japão
    japan_phone = db.Column(db.String(20))                 # Telefone no Japão
    japan_id = db.Column(db.String(50), unique=True)       # Documento de identificação japonês
    email = db.Column(db.String(120), unique=True)         # Email para contato
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Data de cadastro
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última atualização
    
    # Relacionamento com as imagens/documentos do cliente
    images = db.relationship('ClientImage', backref='client', lazy=True, cascade='all, delete-orphan')

class Sale(db.Model):
    """Modelo para vendas
    
    Registra as transações de venda, incluindo informações do cliente,
    produto, vendedor e condições de pagamento.
    """
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)   # Cliente que realizou a compra
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) # Produto vendido
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)    # Vendedor responsável (pode ser nulo após exclusão do vendedor)
    quantity = db.Column(db.Integer, nullable=False)                               # Quantidade vendida
    original_price = db.Column(db.Float, nullable=False)                           # Preço original do produto
    discount_percentage = db.Column(db.Float, default=0)                          # Percentual de desconto aplicado
    total_price = db.Column(db.Float, nullable=False)                           # Preço final após desconto
    status = db.Column(db.String(20), default='negotiating')                   # Estado da venda: negociando, pendente, concluída, cancelada
    stock_updated = db.Column(db.Boolean, default=False)                       # Indica se o estoque foi atualizado após a venda
    notes = db.Column(db.Text)                                                # Observações e anotações da venda
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)               # Data da venda
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Última atualização
    
    # Campos relacionados ao financiamento da venda
    is_financed = db.Column(db.Boolean, default=False)                      # Indica se a venda tem financiamento
    financing_years = db.Column(db.Integer)                                # Prazo do financiamento (1 a 10 anos)
    interest_rate = db.Column(db.Float)                                   # Taxa de juros anual do financiamento
    monthly_payment = db.Column(db.Float)                                 # Valor da parcela mensal
    total_amount = db.Column(db.Float)                                    # Valor total a ser pago com juros
    total_financed = db.Column(db.Float)                                  # Valor total financiado
    
    # Relacionamentos
    client = db.relationship('Client', backref=db.backref('sales', lazy=True))  # Cliente que realizou a compra
    product = db.relationship('Product', backref=db.backref('sales', lazy=True))  # Produto vendido
    seller = db.relationship('User', backref=db.backref('sales', lazy=True))  # Vendedor responsável

    def get_total_value(self):
        """Retorna o valor total da venda considerando financiamento"""
        total = self.total_financed if self.is_financed else self.total_price
        return round(total) if total is not None else 0