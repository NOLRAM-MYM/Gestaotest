from flask import Blueprint, render_template
from flask_login import login_required
from models import Sale, Product, Client
from config import db
from sqlalchemy import func, case
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    from flask import request
    
    # Obter parâmetros do filtro
    period = request.args.get('period', 'monthly')
    date_str = request.args.get('date')
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date = datetime.utcnow()
    
    # Definir período de filtro
    if period == 'daily':
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif period == 'weekly':
        start_date = date - timedelta(days=date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
    elif period == 'yearly':
        start_date = date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date.replace(year=start_date.year + 1)
    else:  # monthly
        start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
    
    # Vendas por período
    sales = Sale.query\
        .filter(Sale.sale_date >= start_date)\
        .filter(Sale.sale_date < end_date)\
        .filter(Sale.status == 'completed')\
        .all()
    
    # Agrupar vendas por data e calcular total
    sales_by_date_dict = {}
    for sale in sales:
        date = sale.sale_date.date()
        if date not in sales_by_date_dict:
            sales_by_date_dict[date] = 0
        total = sale.total_amount if sale.is_financed else sale.total_price
        if total is not None:
            sales_by_date_dict[date] += round(total)
        else:
            sales_by_date_dict[date] += 0
    
    sales_by_date = [{'date': date.strftime('%Y-%m-%d'), 'total': total} for date, total in sales_by_date_dict.items()]
    
    # Produtos mais vendidos
    product_sales = {}
    for sale in Sale.query.filter_by(status='completed').all():
        if sale.product.name not in product_sales:
            product_sales[sale.product.name] = {'quantity': 0, 'revenue': 0}
        product_sales[sale.product.name]['quantity'] += sale.quantity
        total = sale.total_amount if sale.is_financed else sale.total_price
        if total is not None:
            product_sales[sale.product.name]['revenue'] += round(total)
        else:
            product_sales[sale.product.name]['revenue'] += 0
    
    # Ordenar por quantidade vendida
    top_products = sorted(
        [{'name': name, 'total_quantity': data['quantity'], 'total_revenue': data['revenue']}
         for name, data in product_sales.items()],
        key=lambda x: x['total_quantity'],
        reverse=True
    )[:5]
    
    # Estoque atual
    low_stock_products = Product.query\
        .filter(Product.stock < 10)\
        .order_by(Product.stock.asc())\
        .all()
    
    # Clientes mais ativos
    client_sales = {}
    for sale in Sale.query.filter_by(status='completed').all():
        if sale.client.full_name not in client_sales:
            client_sales[sale.client.full_name] = {'purchases': 0, 'spent': 0}
        client_sales[sale.client.full_name]['purchases'] += 1
        total = sale.total_amount if sale.is_financed else sale.total_price
        if total is not None:
            client_sales[sale.client.full_name]['spent'] += round(total)
        else:
            client_sales[sale.client.full_name]['spent'] += 0
    
    # Ordenar por valor total gasto
    top_clients = sorted(
        [{'full_name': name, 'total_purchases': data['purchases'], 'total_spent': data['spent']}
         for name, data in client_sales.items()],
        key=lambda x: x['total_spent'],
        reverse=True
    )[:5]
    
    # Estatísticas gerais
    completed_sales = Sale.query.filter_by(status='completed').all()
    total_sales = len(completed_sales)
    total_revenue = round(sum(sale.get_total_value() for sale in completed_sales))
    total_clients = Client.query.count()
    total_products = Product.query.count()
    
    # Cálculo dos custos totais e lucro
    vendas_completas = Sale.query.filter_by(status='completed').all()
    total_custos = 0
    for venda in vendas_completas:
        custo_produto = venda.product.total_custos()
        total_custos += custo_produto * venda.quantity
    
    # Cálculo do lucro (receita - custos)
    lucro_total = round(total_revenue - total_custos)
    
    return render_template('dashboard/index.html',
                         sales_by_date=sales_by_date,
                         top_products=top_products,
                         low_stock_products=low_stock_products,
                         top_clients=top_clients,
                         total_sales=total_sales,
                         total_revenue=total_revenue,
                         total_clients=total_clients,
                         total_products=total_products,
                         total_custos=total_custos,
                         lucro_total=lucro_total)