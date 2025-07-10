from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class BaseAgent(models.Model):
    """Base model for all agents - used for catalog and marketplace"""
    CATEGORIES = [
        ('analytics', 'Analytics'),
        ('utilities', 'Utilities'),
        ('content', 'Content'),
        ('marketing', 'Marketing'),
        ('customer-service', 'Customer Service'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    icon = models.CharField(max_length=100, default='🤖')
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('4.5'))
    review_count = models.IntegerField(default=0)
    agent_type = models.CharField(max_length=20, choices=[
        ('webhook', 'Webhook'),
        ('api', 'API'),
    ], default='webhook')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
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


class BaseAgentRequest(models.Model):
    """Base model for agent requests"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.ForeignKey(BaseAgent, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class BaseAgentResponse(models.Model):
    """Base model for agent responses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    processing_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True