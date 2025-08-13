from django.urls import path
from . import views


urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('terminal/', views.pos_terminal, name='terminal'),
    path('process-sale/', views.process_sale, name='process_sale'),
    path('products/category/<int:category_id>/', views.get_products_by_category, name='products_by_category'),
    path('products/search/', views.search_products, name='search_products'),
    path('sales/', views.sales_history, name='sales_history'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('inventory/', views.inventory_management, name='inventory'),
]