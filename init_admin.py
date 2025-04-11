from config import app, db, bcrypt
from models import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

def init_admin():
    try:
        with app.app_context():
            # Verifica se o banco de dados está acessível
            try:
                db.session.execute(text('SELECT 1'))
            except SQLAlchemyError as e:
                print('Erro ao conectar ao banco de dados:', str(e))
                return

            # Verifica se já existe um administrador
            try:
                admin = User.query.filter_by(is_admin=True).first()
                if not admin:
                    # Cria o administrador padrão
                    hashed_password = bcrypt.generate_password_hash('admin123', rounds=12).decode('utf-8')
                    admin = User(
                        username='admin',
                        email='admin@sistema.com',
                        password=hashed_password,
                        is_admin=True
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print('Administrador padrão criado com sucesso!')
                    print('Email: admin@sistema.com')
                    print('Senha: admin123')
                else:
                    print('Já existe um administrador no sistema.')
            except SQLAlchemyError as e:
                db.session.rollback()
                print('Erro ao criar administrador:', str(e))
    except Exception as e:
        print('Erro inesperado:', str(e))

if __name__ == '__main__':
    init_admin()