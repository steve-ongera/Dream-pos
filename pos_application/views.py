from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal
import json
from datetime import datetime, timedelta
from django.db import models
from .models import Product, Category, Sale, SaleItem, Customer, Discount, Inventory

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
import json

@csrf_protect
def login_view(request):
    """
    Handle user login with professional form
    """
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect to your main dashboard
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'auth/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Handle remember me functionality
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect to next page or dashboard
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Your account has been deactivated. Please contact administrator.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'auth/login.html')

@login_required
def logout_view(request):
    """
    Handle user logout
    """
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'You have been logged out successfully. See you soon!')
    return redirect('login')



@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get today's sales summary
    today = timezone.now().date()
    today_sales = Sale.objects.filter(created_at__date=today)
    
    # Calculate statistics
    total_sales_today = today_sales.aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    
    total_transactions = today_sales.count()
    
    # Get recent sales
    recent_sales = Sale.objects.select_related('customer', 'cashier').order_by('-created_at')[:5]
    
    # Get low stock products
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=models.F('min_stock_level'),
        is_active=True
    )[:5]
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    # Get featured/recent products
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
    context = {
        'total_sales_today': total_sales_today,
        'total_transactions': total_transactions,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'categories': categories,
        'products': products,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def pos_terminal(request):
    """POS Terminal for making sales"""
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    customers = Customer.objects.all()
    discounts = Discount.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
        'products': products,
        'customers': customers,
        'discounts': discounts,
    }
    
    return render(request, 'terminal.html', context)

@login_required
def get_products_by_category(request, category_id):
    """AJAX view to get products by category"""
    products = Product.objects.filter(
        category_id=category_id, 
        is_active=True,
        stock_quantity__gt=0
    )
    
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'stock': product.stock_quantity,
            'image': product.image.url if product.image else None,
        })
    
    return JsonResponse({'products': products_data})

@login_required
def search_products(request):
    """AJAX view to search products"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(sku__icontains=query),
        is_active=True,
        stock_quantity__gt=0
    )[:10]
    
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.price),
            'stock': product.stock_quantity,
            'category': product.category.name,
        })
    
    return JsonResponse({'products': products_data})

@login_required
def process_sale(request):
    """Process a sale transaction"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract data
            cart_items = data.get('items', [])
            customer_id = data.get('customer_id')
            payment_method = data.get('payment_method', 'cash')
            amount_paid = Decimal(str(data.get('amount_paid', 0)))
            discount_id = data.get('discount_id')
            
            if not cart_items:
                return JsonResponse({'success': False, 'error': 'No items in cart'})
            
            # Calculate totals
            total_amount = Decimal('0.00')
            sale_items = []
            
            for item in cart_items:
                product = get_object_or_404(Product, id=item['product_id'])
                quantity = int(item['quantity'])
                unit_price = product.price
                
                # Check stock
                if product.stock_quantity < quantity:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Insufficient stock for {product.name}'
                    })
                
                item_total = unit_price * quantity
                total_amount += item_total
                
                sale_items.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': item_total,
                })
            
            # Apply discount
            discount_amount = Decimal('0.00')
            if discount_id:
                discount = get_object_or_404(Discount, id=discount_id)
                if discount.is_valid and total_amount >= discount.minimum_amount:
                    discount_amount = (total_amount * discount.percentage) / 100
            
            # Calculate final amount
            tax_amount = Decimal('0.00')  # Add tax calculation if needed
            final_amount = total_amount - discount_amount + tax_amount
            
            # Calculate change
            change_given = amount_paid - final_amount if amount_paid >= final_amount else Decimal('0.00')
            
            # Create sale
            sale = Sale.objects.create(
                customer_id=customer_id if customer_id else None,
                cashier=request.user,
                total_amount=total_amount,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                final_amount=final_amount,
                payment_method=payment_method,
                amount_paid=amount_paid,
                change_given=change_given,
            )
            
            # Create sale items and update inventory
            for item_data in sale_items:
                SaleItem.objects.create(
                    sale=sale,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                )
                
                # Update product stock
                product = item_data['product']
                product.stock_quantity -= item_data['quantity']
                product.save()
                
                # Create inventory transaction
                Inventory.objects.create(
                    product=product,
                    transaction_type='sale',
                    quantity=-item_data['quantity'],
                    notes=f'Sale {sale.sale_number}',
                    user=request.user,
                )
            
            # Update customer loyalty points if applicable
            if customer_id:
                customer = Customer.objects.get(id=customer_id)
                points_earned = int(final_amount / 10)  # 1 point per $10
                customer.loyalty_points += points_earned
                customer.total_spent += final_amount
                customer.save()
            
            return JsonResponse({
                'success': True,
                'sale_id': sale.id,
                'sale_number': sale.sale_number,
                'total': float(final_amount),
                'change': float(change_given),
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def sales_history(request):
    """View sales history"""
    sales = Sale.objects.select_related('customer', 'cashier').order_by('-created_at')
    
    # Filter by date range if provided
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        sales = sales.filter(created_at__date__gte=date_from)
    if date_to:
        sales = sales.filter(created_at__date__lte=date_to)
    
    context = {
        'sales': sales,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'sales_history.html', context)

@login_required
def sale_detail(request, sale_id):
    """View sale details"""
    sale = get_object_or_404(Sale, id=sale_id)
    sale_items = sale.items.select_related('product')
    
    context = {
        'sale': sale,
        'sale_items': sale_items,
    }
    
    return render(request, 'sale_detail.html', context)

@login_required
def inventory_management(request):
    """Inventory management view"""
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query)
        )
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    
    return render(request, 'inventory.html', context)