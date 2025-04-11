from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required
from models import Product, ProductImage, Category
from config import db
from routes.auth import admin_required
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO

products_bp = Blueprint('products', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        try:
            db.session.commit()
            flash('Categoria criada com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Erro ao criar categoria. Por favor, tente novamente.', 'danger')
        return redirect(url_for('products.manage_categories'))
    
    categories = Category.query.all()
    return render_template('products/categories.html', categories=categories, form=form)

@products_bp.route('/products')
@login_required
def list_products():
    view_type = request.args.get('view', 'list')
    category_id = request.args.get('category')
    
    if category_id:
        products = Product.query.filter_by(category_id=category_id).all()
    else:
        products = Product.query.all()
    categories = Category.query.all()
    if view_type == 'gallery':
        return render_template('products/gallery.html', products=products, categories=categories)
    return render_template('products/list.html', products=products, categories=categories)

@products_bp.route('/products/gallery')
@login_required
def gallery_products():
    products = Product.query.all()
    # Obtém apenas as categorias que têm produtos
    categories = Category.query.join(Product).distinct().all()
    return render_template('products/gallery.html', products=products, categories=categories)

@products_bp.route('/product/image/<int:image_id>')
def get_product_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    return send_file(
        BytesIO(image.image_data),
        mimetype=image.mime_type
    )

from wtforms import StringField, FloatField, IntegerField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, NumberRange

from wtforms_sqlalchemy.fields import QuerySelectField

def get_categories():
    return Category.query.all()

class ProductForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Descrição', validators=[Length(max=500)])
    category = QuerySelectField('Categoria', query_factory=get_categories, get_label='name', allow_blank=True, blank_text='Selecione uma categoria...')
    price = FloatField('Preço', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Estoque', validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Ativo')
    data_entrada = DateField('Data de Entrada', validators=[DataRequired()])
    custo1 = FloatField('Custo 1', validators=[NumberRange(min=0)])
    custo2 = FloatField('Custo 2', validators=[NumberRange(min=0)])
    custo3 = FloatField('Custo 3', validators=[NumberRange(min=0)])
    custo4 = FloatField('Custo 4', validators=[NumberRange(min=0)])
    custo5 = FloatField('Custo 5', validators=[NumberRange(min=0)])
    submit = SubmitField('Salvar Produto')

class CategoryForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=50)])
    description = StringField('Descrição', validators=[Length(max=200)])
    submit = SubmitField('Salvar Categoria')

@products_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_product():
    form = ProductForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        price = form.price.data
        stock = form.stock.data
        images = request.files.getlist('images[]')
        
        # condiçao de quantidade de imagens que podem ser enviadas por produto
        if len(images) > 5:
            flash('Você pode enviar no máximo 5 imagens por produto.', 'danger')
            return redirect(url_for('products.create_product'))
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            data_entrada=form.data_entrada.data,
            custo1=form.custo1.data,
            custo2=form.custo2.data,
            custo3=form.custo3.data,
            custo4=form.custo4.data,
            custo5=form.custo5.data,
            category=form.category.data
        )
        product.update_status()
        db.session.add(product)
        
        for image in images:
            if image and allowed_file(image.filename):
                image_data = image.read()
                mime_type = image.content_type
                product_image = ProductImage(product=product, image_data=image_data, mime_type=mime_type)
                db.session.add(product_image)
        
        try:
            db.session.commit()
            flash('Produto criado com sucesso!', 'success')
            return redirect(url_for('products.list_products'))
        except:
            db.session.rollback()
            flash('Erro ao criar produto. Por favor, tente novamente.', 'danger')
            return redirect(url_for('products.create_product'))
        
    return render_template('products/create.html', form=form)

@products_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.data_entrada = form.data_entrada.data
        product.custo1 = form.custo1.data
        product.custo2 = form.custo2.data
        product.custo3 = form.custo3.data
        product.custo4 = form.custo4.data
        product.custo5 = form.custo5.data
        product.is_active = form.is_active.data
        product.category = form.category.data
        product.update_status()
        
        images = request.files.getlist('images[]')
        if images and any(image.filename for image in images):
            existing_images_count = len(product.images)
            new_images_count = len([img for img in images if img.filename])
            
            if existing_images_count + new_images_count > 5:
                flash('Você pode ter no máximo 5 imagens por produto.', 'danger')
                return redirect(url_for('products.edit_product', id=id))
            
            for image in images:
                if image and allowed_file(image.filename):
                    image_data = image.read()
                    mime_type = image.content_type
                    product_image = ProductImage(product=product, image_data=image_data, mime_type=mime_type)
                    db.session.add(product_image)
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('products.list_products'))
        
    return render_template('products/edit.html', product=product, form=form)

@products_bp.route('/products/delete_image/<int:image_id>', methods=['POST'])
@login_required
@admin_required
def delete_product_image(image_id):
    product_image = ProductImage.query.get_or_404(image_id)
    
    try:
        db.session.delete(product_image)
        db.session.commit()
        return {'success': True}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@products_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    if product.sales:
        flash('Não é possível excluir o produto pois existem vendas associadas a ele.', 'danger')
        return redirect(url_for('products.list_products'))
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Produto excluído com sucesso!', 'success')
        return redirect(url_for('products.list_products'))
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir produto. Verifique se não existem dependências.', 'danger')
        return redirect(url_for('products.list_products'))