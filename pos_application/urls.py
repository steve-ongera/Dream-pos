from django.urls import path
from . import views


urlpatterns = [
    # Dashboard
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('terminal/', views.pos_terminal, name='terminal'),
    path('process-sale/', views.process_sale, name='process_sale'),

    # M-Pesa Integration  /mpesa-callback/
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
    path('pending-mpesa-sales/', views.get_pending_mpesa_sales, name='get_pending_mpesa_sales'),

    
    path('pos/products/category/<int:category_id>/', views.get_products_by_category, name='products_by_category'),
    path('products/search/', views.search_products, name='search_products'),
    path('sales/', views.sales_history, name='sales_history'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('inventory/', views.inventory_management, name='inventory'),
    # Customer URLs
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/ajax/', views.customers_ajax, name='customers_ajax'),
    path('customers/<int:customer_id>/detail/', views.customer_detail_ajax, name='customer_detail_ajax'),
    path('customers/create/', views.customer_create_ajax, name='customer_create_ajax'),
    path('customers/<int:customer_id>/update/', views.customer_update_ajax, name='customer_update_ajax'),
    path('customers/<int:customer_id>/delete/', views.customer_delete_ajax, name='customer_delete_ajax'),
    path('reports/', views.reports_view, name='reports_view'),
    path('reports/sales-data/', views.sales_data_ajax, name='sales_data_ajax'),
    path('reports/top-products/', views.top_products_ajax, name='top_products_ajax'),
    path('reports/daily-analysis/', views.daily_sales_analysis_ajax, name='daily_sales_analysis_ajax'),
    path('reports/sales-summary/', views.sales_summary_ajax, name='sales_summary_ajax'),
    path('settings/', views.settings_view, name='settings_view'),

    # AJAX endpoints
    path('update/', views.update_inventory, name='update_inventory'),
    path('export/', views.export_inventory, name='export_inventory'),
    path('add-product/', views.add_product, name='add_product'),
    path('product-history/<int:product_id>/', views.get_product_history, name='product_history'),
]