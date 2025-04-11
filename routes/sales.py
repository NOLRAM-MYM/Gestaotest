from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Sale, Product, Client, User
from config import db
from forms import SaleForm
from datetime import datetime
from routes.auth import admin_required
import math

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales')
@login_required
def list_sales():
    # Usando LEFT JOIN para incluir vendas mesmo quando o vendedor foi excluído
    sales = Sale.query.join(Client).join(Product).outerjoin(User, Sale.seller_id == User.id).order_by(Sale.sale_date.desc(), Sale.id.desc()).all()
    return render_template('sales/list.html', sales=sales)

@sales_bp.route('/sales/new', methods=['GET', 'POST'])
@login_required
def create_sale():
    product_id = request.args.get('product_id', type=int)
    form = SaleForm()
    
    if product_id:
        form.product_id.data = product_id
    
    # Populate select fields
    form.product_id.choices = [(p.id, f"{p.name} - ¥{p.price}") 
                              for p in Product.query.filter_by(is_active=True).all()]
    form.client_id.choices = [(c.id, c.full_name) 
                             for c in Client.query.all()]
    
    if form.validate_on_submit():
        product = Product.query.get_or_404(form.product_id.data)
        
        if product.stock < form.quantity.data:
            flash('Quantidade indisponível em estoque.', 'danger')
            return redirect(url_for('sales.create_sale'))
        
        original_price = round(product.price * form.quantity.data)
        discount = round((form.discount_percentage.data / 100) * original_price)
        total_price = round(original_price - discount)
        
        # Cálculo do financiamento
        is_financed = form.is_financed.data
        total_financed = round(total_price)
        monthly_payment = round(total_price)
        
        if is_financed:
            years = form.financing_years.data
            if years <= 0:
                flash('O período de financiamento deve ser maior que zero.', 'danger')
                return redirect(url_for('sales.create_sale'))
                
            annual_rate = form.interest_rate.data
            if annual_rate <= 0:
                flash('A taxa de juros deve ser maior que zero.', 'danger')
                return redirect(url_for('sales.create_sale'))
                
            annual_rate = annual_rate / 100
            monthly_rate = annual_rate / 12
            num_payments = years * 12
            
            monthly_payment = total_price * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            total_financed = monthly_payment * num_payments
        
        sale = Sale(
            product_id=form.product_id.data,
            client_id=form.client_id.data,
            seller_id=current_user.id,
            quantity=form.quantity.data,
            original_price=original_price,
            discount_percentage=form.discount_percentage.data,
            total_price=total_price,
            notes=form.notes.data,
            status='pending',
            stock_updated=False,
            sale_date=form.sale_date.data,
            is_financed=is_financed,
            financing_years=form.financing_years.data if is_financed else None,
            interest_rate=form.interest_rate.data if is_financed else None,
            total_financed=total_financed if is_financed else None,
            monthly_payment=monthly_payment if is_financed else None
        )
        
        try:
            # Não atualiza o estoque imediatamente para vendas pendentes
            db.session.add(sale)
            db.session.commit()
            flash('Venda registrada com sucesso!', 'success')
            return redirect(url_for('sales.list_sales'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar venda. Por favor, tente novamente.', 'danger')
            return redirect(url_for('sales.create_sale'))
    
    return render_template('sales/create.html', form=form)

@sales_bp.route('/sales/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sale(id):
    sale = Sale.query.get_or_404(id)
    
    # Validação de permissões e estado da venda
    if not current_user.is_admin and sale.seller_id != current_user.id:
        flash('Você não tem permissão para editar esta venda.', 'danger')
        return redirect(url_for('sales.list_sales'))
    
    if sale.status == 'completed':
        flash('Não é possível editar uma venda finalizada.', 'warning')
        return redirect(url_for('sales.list_sales'))
    
    form = SaleForm(obj=sale)
    form.product_id.choices = [(p.id, f"{p.name} - ¥{p.price}") for p in Product.query.filter_by(is_active=True).all()]
    form.client_id.choices = [(c.id, c.full_name) for c in Client.query.all()]
    
    # Preencher campos de financiamento existentes
    if request.method == 'GET' and sale.is_financed:
        form.financing_years.data = sale.financing_years
        form.interest_rate.data = sale.interest_rate
    
    if form.validate_on_submit():
        try:
            # Validar e atualizar estoque
            if not _validate_and_update_stock(sale, form):
                return redirect(url_for('sales.edit_sale', id=id))
            
            # Calcular valores da venda
            product = Product.query.get_or_404(form.product_id.data)
            sale_values = _calculate_sale_values(product, form)
            
            # Atualizar dados básicos
            _update_basic_sale_data(sale, form, sale_values)
            
            # Atualizar dados de financiamento
            if not _update_financing_data(sale, form, sale_values['total_price']):
                return redirect(url_for('sales.edit_sale', id=id))
            
            # Garantir que as alterações sejam salvas
            db.session.add(sale)
            db.session.commit()
            flash('Venda atualizada com sucesso!', 'success')
            return redirect(url_for('sales.list_sales'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar venda: {str(e)}")
            flash('Erro ao atualizar venda. Por favor, tente novamente.', 'danger')
            return redirect(url_for('sales.edit_sale', id=id))
    
    return render_template('sales/edit.html', form=form, sale=sale)

def _validate_and_update_stock(sale, form):
    product = Product.query.get_or_404(form.product_id.data)
    quantity_difference = form.quantity.data - sale.quantity
    
    # Verificar disponibilidade de estoque
    if (product.id != sale.product_id and product.stock < form.quantity.data) or \
       (product.id == sale.product_id and quantity_difference > product.stock):
        flash(f'Quantidade indisponível em estoque. Estoque atual: {product.stock}', 'danger')
        return False
    
    # Atualizar estoque
    if product.id != sale.product_id:
        old_product = Product.query.get(sale.product_id)
        old_product.stock += sale.quantity
        old_product.update_status()
        product.stock -= form.quantity.data
    else:
        product.stock -= quantity_difference
    product.update_status()
    return True

def _calculate_sale_values(product, form):
    original_price = round(product.price * form.quantity.data)
    total_price = round(original_price * (1 - form.discount_percentage.data / 100))
    return {'original_price': original_price, 'total_price': total_price}

def _update_basic_sale_data(sale, form, values):
    sale.product_id = form.product_id.data
    sale.client_id = form.client_id.data
    sale.quantity = form.quantity.data
    sale.original_price = values['original_price']
    sale.discount_percentage = form.discount_percentage.data
    sale.total_price = values['total_price']
    sale.notes = form.notes.data
    sale.sale_date = form.sale_date.data
    sale.updated_at = datetime.utcnow()

def _update_financing_data(sale, form, total_price):
    sale.is_financed = form.is_financed.data
    if not sale.is_financed:
        sale.financing_years = None
        sale.interest_rate = None
        sale.monthly_payment = total_price
        sale.total_financed = total_price
        sale.total_amount = total_price  # Garantir que o total_amount seja atualizado
        return True
    
    if form.financing_years.data <= 0 or form.interest_rate.data <= 0:
        flash('Período de financiamento e taxa de juros devem ser maiores que zero.', 'danger')
        return False
    
    monthly_rate = (form.interest_rate.data / 100) / 12
    num_payments = form.financing_years.data * 12
    
    if monthly_rate > 0:
        monthly_payment = round(total_price * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1))
        total_financed = round(monthly_payment * num_payments)
    else:
        monthly_payment = round(total_price / num_payments)
        total_financed = round(total_price)
    
    sale.financing_years = form.financing_years.data
    sale.interest_rate = form.interest_rate.data
    sale.monthly_payment = monthly_payment
    sale.total_financed = total_financed
    sale.total_amount = total_financed  # Atualizar o total_amount com o valor financiado
    return True

@sales_bp.route('/sales/<int:id>/complete',  methods=['GET', 'POST'])
@login_required
def complete_sale(id):
    sale = Sale.query.get_or_404(id)
    
    if sale.status not in ['negotiating', 'pending']:
        flash('Esta venda já foi finalizada ou cancelada.', 'warning')
        return redirect(url_for('sales.list_sales'))
    
    try:
        # Atualiza o estoque do produto
        product = Product.query.get(sale.product_id)
        if not product:
            flash('Produto não encontrado. Não é possível finalizar a venda.', 'danger')
            return redirect(url_for('sales.list_sales'))
            
        product.stock -= sale.quantity
        product.update_status()
        
        sale.status = 'completed'
        sale.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Venda finalizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f'Erro ao finalizar venda: {str(e)}')
        flash('Erro ao finalizar venda. Por favor, tente novamente.', 'danger')
    
    return redirect(url_for('sales.list_sales'))

@sales_bp.route('/sales/<int:id>/cancel',  methods=['GET', 'POST'])
@login_required
def cancel_sale(id):
    sale = Sale.query.get_or_404(id)
    
    if sale.status == 'cancelled':
        flash('Esta venda já foi cancelada.', 'warning')
        return redirect(url_for('sales.list_sales'))
    
    product = Product.query.get(sale.product_id)
    if not product:
        flash('Produto não encontrado. Não é possível cancelar a venda.', 'danger')
        return redirect(url_for('sales.list_sales'))
    
    try:
        # Só restaura o estoque se a venda estava completa
        if sale.status == 'completed':
            product.stock += sale.quantity
            product.update_status()
        
        sale.status = 'cancelled'
        sale.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Venda cancelada com sucesso!', 'success')
        return redirect(url_for('sales.list_sales'))
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao cancelar venda. Por favor, tente novamente.', 'danger')
        print(f'Erro ao cancelar venda: {str(e)}')
        return redirect(url_for('sales.list_sales'))
