from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For FontAwesome icons
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0

class Customer(models.Model):
    LOYALTY_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'), 
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    loyalty_tier = models.CharField(max_length=20, choices=LOYALTY_CHOICES, default='bronze')
    loyalty_points = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def discount_percentage(self):
        discounts = {'bronze': 0, 'silver': 5, 'gold': 10, 'platinum': 15}
        return discounts.get(self.loyalty_tier, 0)
    


from django.db import models
from django.contrib.auth.models import User
import json

class Payment(models.Model):
    """Model to track M-Pesa payments for POS sales"""
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    sale = models.ForeignKey(
        'Sale', 
        on_delete=models.CASCADE, 
        related_name='payments',
        help_text="Related sale transaction"
    )
    
    checkout_request_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="M-Pesa checkout request ID"
    )
    
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='PENDING',
        help_text="Payment status"
    )
    
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Customer phone number used for payment"
    )
    
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Payment amount"
    )
    
    mpesa_receipt = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="M-Pesa transaction receipt number"
    )
    
    transaction_date = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="M-Pesa transaction date"
    )
    
    raw_response = models.JSONField(
        blank=True, 
        null=True,
        help_text="Full M-Pesa API response"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When payment record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When payment record was last updated"
    )
    
    class Meta:
        db_table = 'pos_payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['status']),
            models.Index(fields=['sale']),
        ]
    
    def __str__(self):
        return f"Payment {self.checkout_request_id} - {self.status}"
    
    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'SUCCESS'
    
    @property
    def is_pending(self):
        """Check if payment is still pending"""
        return self.status == 'PENDING'
    
    @property
    def formatted_phone(self):
        """Return formatted phone number"""
        if self.phone_number:
            if self.phone_number.startswith('254'):
                return f"+{self.phone_number}"
            return self.phone_number
        return None
    
    def get_response_data(self):
        """Get parsed response data"""
        if self.raw_response:
            if isinstance(self.raw_response, str):
                try:
                    return json.loads(self.raw_response)
                except json.JSONDecodeError:
                    return {}
            return self.raw_response
        return {}

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
        ('credit', 'Credit'),
    ]
    
    sale_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    change_given = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Sale {self.sale_number}"
    
    def save(self, *args, **kwargs):
        if not self.sale_number:
            self.sale_number = f"S{timezone.now().strftime('%Y%m%d')}{Sale.objects.count() + 1:04d}"
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Discount(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.percentage}%"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to

class Inventory(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('sale', 'Sale'),
        ('return', 'Return'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Inventory Transactions"
        
    def __str__(self):
        return f"{self.product.name} - {self.transaction_type} - {self.quantity}"