from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required
from models import Client, ClientImage, Sale
from config import db
from routes.auth import admin_required
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO



clients_bp = Blueprint('clients', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@clients_bp.route('/clients')
@login_required
def list_clients():
    clients = Client.query.all()
    return render_template('clients/list.html', clients=clients)

@clients_bp.route('/client/image/<int:image_id>')
def get_client_image(image_id):
    image = ClientImage.query.get_or_404(image_id)
    return send_file(
        BytesIO(image.image_data),
        mimetype=image.mime_type
    )

from forms import ClientForm

@clients_bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
def create_client():
    form = ClientForm()
    if request.method == 'POST' and form.validate_on_submit():
        full_name = form.full_name.data
        japan_address = form.japan_address.data
        japan_phone = form.japan_phone.data
        japan_id = form.japan_id.data
        email = form.email.data
        images = request.files.getlist('images[]')
        
        # Validação de dados únicos
        if Client.query.filter_by(japan_id=japan_id).first():
            flash('ID japonês já cadastrado.', 'danger')
            return redirect(url_for('clients.create_client'))
            
        if Client.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('clients.create_client'))
        
        client = Client(
            full_name=full_name,
            japan_address=japan_address,
            japan_phone=japan_phone,
            japan_id=japan_id,
            email=email
        )
        
        db.session.add(client)
        db.session.commit()
        
        # Processar até 5 imagens
        for i, image in enumerate(images[:5]):
            if image and allowed_file(image.filename):
                image_data = image.read()
                mime_type = image.content_type
                client_image = ClientImage(client_id=client.id, image_data=image_data, mime_type=mime_type)
                db.session.add(client_image)
        
        db.session.commit()
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('clients.list_clients'))
        
    return render_template('clients/create.html', form=form)

from forms import ClientForm

@clients_bp.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_client(id):
    client = Client.query.get_or_404(id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        # Validação de dados únicos
        if form.japan_id.data != client.japan_id and Client.query.filter_by(japan_id=form.japan_id.data).first():
            flash('ID japonês já cadastrado.', 'danger')
            return redirect(url_for('clients.edit_client', id=id))
            
        if form.email.data != client.email and Client.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('clients.edit_client', id=id))
            
        form.populate_obj(client)
        
        # Processar imagens
        images = request.files.getlist('images[]')
        if images and any(image.filename for image in images):
            # Adicionar novas imagens (até 5)
            existing_images_count = len(client.images)
            new_images_count = len([img for img in images if img.filename])
            
            if existing_images_count + new_images_count > 5:
                flash('Você pode ter no máximo 5 imagens por cliente.', 'danger')
                return redirect(url_for('clients.edit_client', id=id))
            
            for image in images:
                if image and allowed_file(image.filename):
                    image_data = image.read()
                    mime_type = image.content_type
                    client_image = ClientImage(client_id=client.id, image_data=image_data, mime_type=mime_type)
                    db.session.add(client_image)
        
        db.session.commit()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clients.list_clients'))
        
    return render_template('clients/edit.html', client=client, form=form)

@clients_bp.route('/clients/delete-image/<int:image_id>', methods=['POST'])
@login_required
@admin_required
def delete_client_image(image_id):
    client_image = ClientImage.query.get_or_404(image_id)
    
    try:
        # Remove o registro do banco de dados
        db.session.delete(client_image)
        db.session.commit()
        
        return {'success': True, 'message': 'Imagem excluída com sucesso'}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@clients_bp.route('/clients/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_client(id):
    client = Client.query.get_or_404(id)
    
    try:
        # Delete all associated sales records first
        Sale.query.filter_by(client_id=id).delete()
        
        db.session.delete(client)
        db.session.commit()
        flash('Cliente excluído com sucesso!', 'success')
        return redirect(url_for('clients.list_clients'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting client: {e}')
        flash('Erro ao excluir cliente. Por favor, tente novamente.', 'danger')
        return redirect(url_for('clients.list_clients'))