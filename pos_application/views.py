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


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import Extract
from django.utils import timezone
from datetime import datetime, timedelta
import json
from decimal import Decimal
from .models import Customer, Sale, SaleItem, Product, Category

# Customer Views
@login_required
def customers_list(request):
    """Display customers list page"""
    return render(request, 'customers.html')

@login_required
def customers_ajax(request):
    """AJAX endpoint for customer data"""
    if request.method == 'GET':
        customers = Customer.objects.all().order_by('-created_at')
        data = []
        for customer in customers:
            data.append({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'address': customer.address,
                'loyalty_tier': customer.get_loyalty_tier_display(),
                'loyalty_points': customer.loyalty_points,
                'total_spent': str(customer.total_spent),
                'discount_percentage': customer.discount_percentage,
                'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M')
            })
        return JsonResponse({'data': data})

@login_required
def customer_detail_ajax(request, customer_id):
    """Get single customer details"""
    try:
        customer = Customer.objects.get(id=customer_id)
        data = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'loyalty_tier': customer.loyalty_tier,
            'loyalty_points': customer.loyalty_points,
            'total_spent': str(customer.total_spent),
            'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M')
        }
        return JsonResponse({'success': True, 'data': data})
    except Customer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Customer not found'})

@csrf_exempt
@login_required
def customer_create_ajax(request):
    """Create new customer via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer = Customer.objects.create(
                name=data.get('name'),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                address=data.get('address', ''),
                loyalty_tier=data.get('loyalty_tier', 'bronze'),
                loyalty_points=int(data.get('loyalty_points', 0))
            )
            return JsonResponse({
                'success': True, 
                'message': 'Customer created successfully',
                'data': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'phone': customer.phone
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def customer_update_ajax(request, customer_id):
    """Update customer via AJAX"""
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=customer_id)
            data = json.loads(request.body)
            
            customer.name = data.get('name', customer.name)
            customer.email = data.get('email', customer.email)
            customer.phone = data.get('phone', customer.phone)
            customer.address = data.get('address', customer.address)
            customer.loyalty_tier = data.get('loyalty_tier', customer.loyalty_tier)
            customer.loyalty_points = int(data.get('loyalty_points', customer.loyalty_points))
            customer.save()
            
            return JsonResponse({'success': True, 'message': 'Customer updated successfully'})
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def customer_delete_ajax(request, customer_id):
    """Delete customer via AJAX"""
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=customer_id)
            customer.delete()
            return JsonResponse({'success': True, 'message': 'Customer deleted successfully'})
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Reports Views
@login_required
def reports_view(request):
    """Display reports dashboard"""
    return render(request, 'reports.html')

@login_required
def sales_data_ajax(request):
    """Get sales data for the past year"""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    
    # Monthly sales data
    monthly_sales = Sale.objects.filter(
        created_at__range=[start_date, end_date]
    ).extra(
        select={'month': "DATE_TRUNC('month', created_at)"}
    ).values('month').annotate(
        total_sales=Sum('final_amount'),
        total_orders=Count('id')
    ).order_by('month')
    
    # Format data for Chart.js
    months = []
    sales = []
    orders = []
    
    for item in monthly_sales:
        months.append(item['month'].strftime('%Y-%m'))
        sales.append(float(item['total_sales'] or 0))
        orders.append(item['total_orders'])
    
    return JsonResponse({
        'months': months,
        'sales': sales,
        'orders': orders
    })

@login_required
def top_products_ajax(request):
    """Get most sold products"""
    top_products = SaleItem.objects.values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_quantity')[:10]
    
    products = []
    quantities = []
    revenues = []
    
    for item in top_products:
        products.append(item['product__name'])
        quantities.append(item['total_quantity'])
        revenues.append(float(item['total_revenue']))
    
    return JsonResponse({
        'products': products,
        'quantities': quantities,
        'revenues': revenues
    })

@login_required
def daily_sales_analysis_ajax(request):
    """Analyze sales by day of week"""
    sales_by_day = Sale.objects.annotate(
        day_of_week=Extract('created_at', 'dow')
    ).values('day_of_week').annotate(
        total_sales=Sum('final_amount'),
        total_orders=Count('id'),
        avg_order_value=Sum('final_amount') / Count('id')
    ).order_by('day_of_week')
    
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_sales = [0] * 7
    day_orders = [0] * 7
    day_avg = [0] * 7
    
    for item in sales_by_day:
        day_index = item['day_of_week']
        day_sales[day_index] = float(item['total_sales'] or 0)
        day_orders[day_index] = item['total_orders']
        day_avg[day_index] = float(item['avg_order_value'] or 0)
    
    return JsonResponse({
        'days': days,
        'sales': day_sales,
        'orders': day_orders,
        'avg_values': day_avg
    })

@login_required
def sales_summary_ajax(request):
    """Get sales summary statistics"""
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Today's sales
    today_sales = Sale.objects.filter(
        created_at__date=today
    ).aggregate(
        total_sales=Sum('final_amount'),
        total_orders=Count('id')
    )
    
    # This month's sales
    this_month_sales = Sale.objects.filter(
        created_at__date__gte=this_month_start
    ).aggregate(
        total_sales=Sum('final_amount'),
        total_orders=Count('id')
    )
    
    # Last month's sales
    last_month_sales = Sale.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lt=this_month_start
    ).aggregate(
        total_sales=Sum('final_amount'),
        total_orders=Count('id')
    )
    
    # Top customer
    top_customer = Customer.objects.order_by('-total_spent').first()
    
    return JsonResponse({
        'today_sales': float(today_sales['total_sales'] or 0),
        'today_orders': today_sales['total_orders'] or 0,
        'month_sales': float(this_month_sales['total_sales'] or 0),
        'month_orders': this_month_sales['total_orders'] or 0,
        'last_month_sales': float(last_month_sales['total_sales'] or 0),
        'top_customer': top_customer.name if top_customer else 'No customers',
        'total_customers': Customer.objects.count(),
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(
            stock_quantity__lte=F('min_stock_level')
        ).count()
    })

# Settings Views
@login_required
def settings_view(request):
    """Display settings page"""
    return render(request, 'settings.html')