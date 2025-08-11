# Sistema de Gestão Integrado

## Visão Geral
Sistema completo para gestão de:
- 👥 Usuários (Admin/Comercial)
- 🏷️ Categorias de produtos
- 🛍️ Produtos com galeria de imagens
- 📊 Vendas com financiamento
- 📈 Dashboard analítico

## 🛠️ Instalação
```bash
# Clonar repositório
git clone https://github.com/nolram-mym/Gestaotest.git
cd Gestaotest

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
copiar .env.example para .env e configurar

# Iniciar aplicação
flask run
```

## 🔑 Funcionalidades Principais
### Módulo Comercial
- Gestão completa de clientes
- Controle de estoque inteligente
- Cálculo automático de custos
- Sistema de vendas com financiamento

### Painel Admin
- CRUD completo de usuários
- Controle de permissões
- Backup de dados
- Logs de atividades

## ⚙️ Configuração Avançada
```python
# Configurações personalizadas no config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
```

## 📦 Dependências Principais
- Flask + Extensões (SQLAlchemy, WTF, Login)
- Pandas para análise de dados
- Biblioteca de PDF e Excel
- Sistema de temas claro/escuro

## 🤝 Contribuição
1. Faça fork do projeto
2. Crie uma branch feature (`git checkout -b feature/novo-recurso`)
3. Commit suas mudanças (`git commit -m 'Adiciona novo recurso'`)
4. Push para a branch (`git push origin feature/novo-recurso`)
5. Abra um Pull Request

## 📄 Licença
MIT License - Consulte o arquivo LICENSE para detalhes