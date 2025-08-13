from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pos_application.models import Category, Product, Customer, Discount
from decimal import Decimal
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Setup initial data for POS system'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up Dreams POS system...'))
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@dreams-pos.com',
                password='cp7kvt',
                first_name='System',
                last_name='Administrator'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (admin/admin123)'))
        
        # Create categories
        categories_data = [
            {'name': 'Mobiles', 'icon': 'mobile-alt', 'description': 'Smartphones and mobile devices'},
            {'name': 'Computers', 'icon': 'laptop', 'description': 'Laptops, desktops, and computers'},
            {'name': 'Watches', 'icon': 'clock', 'description': 'Smart watches and timepieces'},
            {'name': 'Shoes', 'icon': 'shoe-prints', 'description': 'Footwear and sneakers'},
            {'name': 'Headphones', 'icon': 'headphones', 'description': 'Audio devices and headphones'},
            {'name': 'Appliances', 'icon': 'blender', 'description': 'Home and kitchen appliances'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'✓ Created category: {category.name}')
        
        # Create sample products
        products_data = [
            {
                'name': 'iPhone 14 64GB',
                'category': 'Mobiles',
                'sku': 'IPH14-64',
                'price': Decimal('1580.00'),
                'cost_price': Decimal('1200.00'),
                'stock_quantity': 25,
                'description': 'Latest iPhone 14 with 64GB storage'
            },
            {
                'name': 'MacBook Pro',
                'category': 'Computers',
                'sku': 'MBP-13',
                'price': Decimal('1000.00'),
                'cost_price': Decimal('800.00'),
                'stock_quantity': 10,
                'description': '13-inch MacBook Pro'
            },
            {
                'name': 'Rolex Tribute V1',
                'category': 'Watches',
                'sku': 'RTW-V1',
                'price': Decimal('6800.00'),
                'cost_price': Decimal('5000.00'),
                'stock_quantity': 5,
                'description': 'Luxury tribute watch'
            },
            {
                'name': 'Red Nike Angelo',
                'category': 'Shoes',
                'sku': 'RNA-RED',
                'price': Decimal('199.00'),
                'cost_price': Decimal('120.00'),
                'stock_quantity': 50,
                'description': 'Nike Angelo sneakers in red'
            },
            {
                'name': 'Blue White OGR',
                'category': 'Shoes',
                'sku': 'BWO-001',
                'price': Decimal('356.90'),
                'cost_price': Decimal('250.00'),
                'stock_quantity': 30,
                'description': 'Blue and white casual shoes'
            },
            {
                'name': 'MacPad Slim 5 Gen 7',
                'category': 'Computers',
                'sku': 'MPS5G7',
                'price': Decimal('3569.00'),
                'cost_price': Decimal('2800.00'),
                'stock_quantity': 8,
                'description': 'Tablet device with advanced features'
            },
            {
                'name': 'SWAGME Headphones',
                'category': 'Headphones',
                'sku': 'SWG-HP1',
                'price': Decimal('656.70'),
                'cost_price': Decimal('400.00'),
                'stock_quantity': 20,
                'description': 'Premium wireless headphones'
            },
            {
                'name': 'HeadSet Slim 3',
                'category': 'Headphones',
                'sku': 'HSS3-001',
                'price': Decimal('3000.00'),
                'cost_price': Decimal('2200.00'),
                'stock_quantity': 15,
                'description': 'Professional gaming headset'
            },
        ]
        
        for prod_data in products_data:
            try:
                category = Category.objects.get(name=prod_data['category'])
                product, created = Product.objects.get_or_create(
                    sku=prod_data['sku'],
                    defaults={
                        'name': prod_data['name'],
                        'category': category,
                        'price': prod_data['price'],
                        'cost_price': prod_data['cost_price'],
                        'stock_quantity': prod_data['stock_quantity'],
                        'description': prod_data['description'],
                        'min_stock_level': 5,
                    }
                )
                if created:
                    self.stdout.write(f'✓ Created product: {product.name}')
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Category {prod_data["category"]} not found for {prod_data["name"]}')
                )
        
        # Create sample customers
        customers_data = [
            {
                'name': 'James Anderson',
                'email': 'james.anderson@email.com',
                'phone': '+254712345678',
                'loyalty_tier': 'bronze',
                'loyalty_points': 150,
                'total_spent': Decimal('2500.00')
            },
            {
                'name': 'Sarah Wilson',
                'email': 'sarah.wilson@email.com',
                'phone': '+254723456789',
                'loyalty_tier': 'silver',
                'loyalty_points': 500,
                'total_spent': Decimal('5000.00')
            },
            {
                'name': 'Michael Johnson',
                'email': 'michael.j@email.com',
                'phone': '+254734567890',
                'loyalty_tier': 'gold',
                'loyalty_points': 1200,
                'total_spent': Decimal('12000.00')
            },
        ]
        
        for cust_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=cust_data['email'],
                defaults=cust_data
            )
            if created:
                self.stdout.write(f'✓ Created customer: {customer.name}')
        
        # Create sample discounts
        discounts_data = [
            {
                'name': 'New Customer Discount',
                'description': 'Special discount for new customers',
                'percentage': Decimal('10.00'),
                'minimum_amount': Decimal('100.00'),
                'valid_from': datetime.now(),
                'valid_to': datetime.now() + timedelta(days=365),
            },
            {
                'name': 'Bulk Purchase Discount',
                'description': 'Discount for purchases over $500',
                'percentage': Decimal('5.00'),
                'minimum_amount': Decimal('500.00'),
                'valid_from': datetime.now(),
                'valid_to': datetime.now() + timedelta(days=365),
            },
            {
                'name': 'Loyalty Discount',
                'description': 'For loyal customers',
                'percentage': Decimal('15.00'),
                'minimum_amount': Decimal('200.00'),
                'valid_from': datetime.now(),
                'valid_to': datetime.now() + timedelta(days=365),
            },
        ]
        
        for disc_data in discounts_data:
            discount, created = Discount.objects.get_or_create(
                name=disc_data['name'],
                defaults=disc_data
            )
            if created:
                self.stdout.write(f'✓ Created discount: {discount.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Dreams POS system setup completed successfully!\n\n'
                'Next steps:\n'
                '1. Run: python manage.py runserver\n'
                '2. Visit: http://localhost:8000/pos/\n'
                '3. Admin login: admin/admin123\n'
                '4. Configure your store settings in Django admin\n'
            )
        )