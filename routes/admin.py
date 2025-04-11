from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, db
from routes.auth import admin_required
from config import bcrypt
from forms import AdminForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admins')
@login_required
@admin_required
def list_admins():
    admins = User.get_active_users().filter_by(is_admin=True).all()
    form = AdminForm()
    return render_template('admin/list.html', admins=admins, form=form)

@admin_bp.route('/admins/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    form = AdminForm()
    if form.validate_on_submit():
        if User.get_active_users().filter_by(username=form.username.data).first():
            flash('Username já existe.', 'danger')
            return redirect(url_for('admin.create_admin'))
            
        if User.get_active_users().filter_by(email=form.email.data).first():
            flash('Email já está registrado.', 'danger')
            return redirect(url_for('admin.create_admin'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data, rounds=12).decode('utf-8')
        new_admin = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password, is_admin=True)
        
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Administrador criado com sucesso!', 'success')
            return redirect(url_for('admin.list_admins'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar administrador. Por favor, tente novamente.', 'danger')
            return redirect(url_for('admin.create_admin'))
    
    return render_template('admin/create.html', form=form)

@admin_bp.route('/admins/delete/<int:admin_id>', methods=['POST'])
@login_required
@admin_required
def delete_admin(admin_id):
    admin = User.get_active_users().filter_by(id=admin_id, is_admin=True).first_or_404()

    if admin.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('admin.list_admins'))

    try:
        # Marcar o administrador como excluído (soft delete)
        admin.soft_delete()
        flash('Administrador excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir administrador. Por favor, tente novamente.', 'danger')

    return redirect(url_for('admin.list_admins'))

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.get_active_users().all()  # Apenas usuários não excluídos
    form = AdminForm()
    return render_template('admin/users.html', users=users, form=form)

@admin_bp.route('/users/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Você não pode alterar seu próprio status de administrador.', 'danger')
        return redirect(url_for('admin.list_users'))

    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'removido do' if not user.is_admin else 'adicionado ao'
        flash(f'Usuário {status} grupo de administradores com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao alterar status do usuário. Por favor, tente novamente.', 'danger')

    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('admin.list_users'))

    try:
        # Excluir o usuário permanentemente
        # As vendas associadas permanecerão no banco com seller_id nulo
        db.session.delete(user)
        db.session.commit()
        flash('Usuário excluído permanentemente com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir usuário. Por favor, tente novamente.', 'danger')

    return redirect(url_for('admin.list_users'))