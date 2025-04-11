from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from config import db, bcrypt, mail, app
from models import User
from flask_mail import Message
from functools import wraps
from forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm
import os
from itsdangerous import URLSafeTimedSerializer

auth_bp = Blueprint('auth', __name__)

def get_reset_token(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='reset-password-salt')

def verify_reset_token(token, expiration=1800):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='reset-password-salt', max_age=expiration)
    except:
        return None
    return User.get_active_users().filter_by(email=email).first()

def send_reset_email(user):
    try:
        token = get_reset_token(user)
        msg = Message('Solicitação de Redefinição de Senha',
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[user.email])
        msg.body = f'''Para redefinir sua senha, visite o seguinte link:
{url_for('auth.reset_token', token=token, _external=True)}

Se você não fez esta solicitação, simplesmente ignore este email e nenhuma alteração será feita.
'''
        print(f'Tentando enviar email para: {user.email}')
        mail.send(msg)
        print(f'Email enviado com sucesso para: {user.email}')
        return True
    except Exception as e:
        print(f'Erro ao enviar email: {str(e)}')
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acesso negado. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.get_active_users().filter_by(email=form.email.data).first()
            
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login falhou. Por favor, verifique email e senha.', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Erro no campo {field}: {error}', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar a senha do administrador
        admin = User.get_active_users().filter_by(is_admin=True).first()
        if not admin or not bcrypt.check_password_hash(admin.password, form.admin_password.data):
            flash('Senha do administrador incorreta.', 'danger')
            return redirect(url_for('auth.register'))

        if User.get_active_users().filter_by(username=form.username.data).first():
            flash('Username já existe.', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.get_active_users().filter_by(email=form.email.data).first():
            flash('Email já está registrado.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(form.password.data, rounds=12).decode('utf-8')
        
        # Criar usuário normal
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password, is_admin=False)
        db.session.add(user)
        db.session.commit()
        
        flash('Sua conta foi criada! Você já pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema com sucesso!', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.get_active_users().filter_by(email=form.email.data).first()
        if user:
            if send_reset_email(user):
                flash('Um email foi enviado com instruções para redefinir sua senha. Por favor, verifique também sua pasta de spam.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('Ocorreu um erro ao enviar o email. Por favor, tente novamente mais tarde.', 'danger')
        else:
            flash('Não existe conta com esse email.', 'danger')
    return render_template('auth/reset_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = verify_reset_token(token)
    if user is None:
        flash('Token inválido ou expirado', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data, rounds=12).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Sua senha foi atualizada! Você já pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', form=form)