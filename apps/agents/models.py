
# Create your models here.
from django.db import models
from decimal import Decimal

class Agent(models.Model):
    CATEGORIES = [
        ('analytics', 'Analytics'),
        ('utilities', 'Utilities'),
        ('content', 'Content'),
        ('marketing', 'Marketing'),
        ('customer-service', 'Customer Service'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    icon = models.CharField(max_length=10, default='🤖')
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('4.5'))
    review_count = models.IntegerField(default=0)
    n8n_webhook_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def price_display(self):
        return f"{self.price} AED"
    
    def get_gradient_class(self):
        gradient_map = {
            'analytics': 'from-indigo-500 to-purple-600',
            'utilities': 'from-sky-400 to-blue-500',
            'content': 'from-purple-500 to-indigo-600',
            'marketing': 'from-pink-500 to-rose-600',
            'customer-service': 'from-blue-500 to-blue-600',
        }
        return gradient_map.get(self.category, 'from-gray-500 to-gray-600')