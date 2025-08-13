# DREAM POS

A comprehensive Point of Sale (POS) system built with Django, designed for retail businesses to manage sales, inventory, customers, and daily operations efficiently.

## Features

### 🏪 Core POS Functionality
- **Real-time Sales Processing** - Fast and intuitive checkout interface
- **Product Management** - Complete catalog with categories, SKUs, and pricing
- **Inventory Tracking** - Real-time stock levels with low stock alerts
- **Customer Management** - Customer profiles with loyalty program integration
- **Multiple Payment Methods** - Cash, Card, Mobile Money, and Credit support

### 📊 Business Intelligence
- **Sales Dashboard** - Daily sales summaries and key metrics
- **Sales History** - Detailed transaction records with filtering
- **Inventory Reports** - Stock levels and movement tracking
- **Customer Analytics** - Purchase history and loyalty insights

### 💰 Financial Features
- **Flexible Discounts** - Percentage-based promotions with validity periods
- **Customer Loyalty Program** - 4-tier system (Bronze, Silver, Gold, Platinum)
- **Profit Margin Tracking** - Cost vs. selling price analysis
- **Tax Management** - Configurable tax calculations

### 🔐 Security & User Management
- **User Authentication** - Secure login with Django's auth system
- **Role-based Access** - Different permissions for cashiers and managers
- **Transaction Logging** - Complete audit trail for all operations

## Installation

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL/MySQL (recommended) or SQLite for development
- Pillow (for image handling)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/your-username/dream-pos.git
cd dream-pos
```

2. **Create virtual environment**
```bash
python -m venv dreampos_env
source dreampos_env/bin/activate  # On Windows: dreampos_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database settings**
Update `settings.py` with your database configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dreampos_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic
```

8. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access your DREAM POS system.

## Models Overview

### Product Management
- **Category** - Product categorization with icons
- **Product** - Complete product information including pricing, stock, and images
- **Inventory** - Transaction logging for stock movements

### Sales System
- **Sale** - Main sales transaction record
- **SaleItem** - Individual items within each sale
- **Discount** - Promotional discount management

### Customer Management
- **Customer** - Customer profiles with contact information
- **Loyalty Program** - Automatic tier assignment based on spending

## Usage Guide

### Making a Sale
1. Access the POS Terminal from the dashboard
2. Select products by category or search
3. Add items to cart with quantities
4. Apply discounts if applicable
5. Select customer (optional) for loyalty points
6. Choose payment method and process payment
7. Print receipt and complete transaction

### Managing Inventory
1. Navigate to Inventory Management
2. View current stock levels and low stock alerts
3. Add new products or update existing ones
4. Track inventory movements and adjustments
5. Generate inventory reports

### Customer Management
1. Add new customers with contact details
2. View purchase history and loyalty status
3. Track loyalty points and tier progression
4. Apply customer-specific discounts

### Sales Reporting
1. Access Sales History for detailed records
2. Filter by date ranges and customers
3. View individual sale details
4. Export reports for accounting

## API Endpoints

### Product Management
- `GET /api/products/category/<id>/` - Products by category
- `GET /api/products/search/?q=<query>` - Product search

### Sales Processing
- `POST /api/sales/process/` - Process new sale
- `GET /api/sales/history/` - Sales history
- `GET /api/sales/<id>/` - Sale details

## Configuration

### Settings
Key configuration options in `settings.py`:

```python
# Media files for product images
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Time zone
TIME_ZONE = 'Africa/Nairobi'  # Adjust to your location
```

### Loyalty Program
Configure loyalty tiers and discount percentages in the Customer model:
- Bronze: 0% discount
- Silver: 5% discount  
- Gold: 10% discount
- Platinum: 15% discount

## Customization

### Adding New Payment Methods
Update the `PAYMENT_METHODS` choices in the Sale model:
```python
PAYMENT_METHODS = [
    ('cash', 'Cash'),
    ('card', 'Card'),
    ('mobile', 'Mobile Money'),
    ('credit', 'Credit'),
    ('crypto', 'Cryptocurrency'),  # Add new methods
]
```

### Custom Discount Logic
Modify the discount calculation in `process_sale` view for complex discount rules.

### Reporting Extensions
Extend the dashboard with additional metrics by modifying the dashboard view and template.

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False` in settings
- [ ] Configure production database
- [ ] Set up static file serving (nginx/Apache)
- [ ] Configure media file storage
- [ ] Set up SSL certificates
- [ ] Configure backup procedures
- [ ] Set up monitoring and logging

### Recommended Stack
- **Web Server**: Nginx
- **Application Server**: Gunicorn
- **Database**: PostgreSQL
- **Caching**: Redis
- **Media Storage**: AWS S3 or local storage with backup

## Support

### Common Issues
1. **Low Stock Alerts** - Products show alerts when stock <= minimum level
2. **Sale Number Generation** - Automatic format: S{YYYYMMDD}{0001}
3. **Inventory Updates** - Stock automatically decreases on sales
4. **Customer Loyalty** - Points earned: 1 point per $10 spent

### Troubleshooting
- Check Django logs for error details
- Verify database connections
- Ensure media files permissions are correct
- Clear browser cache for UI issues

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Django Web Framework
- Icons powered by FontAwesome
- UI components and styling with modern CSS frameworks

---

**DREAM POS** - Making retail management a dream come true! 🚀