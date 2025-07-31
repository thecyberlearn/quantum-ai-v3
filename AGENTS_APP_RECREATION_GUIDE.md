# Django Agents App Recreation Guide

This guide provides complete instructions for recreating the agents app in another Django project.

## Overview

Create a Django app called `agents` with the following functionality:
- Agent marketplace with categories
- Agent execution system with n8n webhook integration
- User balance checking and fee deduction
- Complete REST API with pagination
- Admin interface for management

## Installation Steps

### 1. Create the App

```bash
python manage.py startapp agents
```

### 2. Install Dependencies

```bash
pip install requests djangorestframework
```

### 3. Add to INSTALLED_APPS

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'agents',
]
```

### 4. Add to URLs

In your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('api/agents/', include('agents.urls')),
]
```

## File Structure

```
agents/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── migrations/
│   └── __init__.py
└── management/
    └── commands/
        └── create_sample_agents.py
```

## Code Files

### agents/models.py

```python
from django.db import models
import uuid

class AgentCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    category = models.ForeignKey(AgentCategory, on_delete=models.CASCADE, related_name='agents')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    form_schema = models.JSONField(help_text="JSON schema for agent input form")
    webhook_url = models.URLField(help_text="n8n webhook URL for execution")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class AgentExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='executions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)  # Adjust to your user model
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2)
    webhook_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    execution_time = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.agent.name} - {self.user.email} - {self.status}"
```

### agents/admin.py

```python
from django.contrib import admin
from .models import AgentCategory, Agent, AgentExecution

@admin.register(AgentCategory)
class AgentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'user', 'status', 'fee_charged', 'created_at']
    list_filter = ['status', 'created_at', 'agent__category']
    search_fields = ['agent__name', 'user__email']
    readonly_fields = ['created_at', 'completed_at']
```

### agents/serializers.py

```python
from rest_framework import serializers
from .models import Agent, AgentCategory, AgentExecution

class AgentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCategory
        fields = ['id', 'name', 'slug', 'description', 'icon']

class AgentSerializer(serializers.ModelSerializer):
    category = AgentCategorySerializer(read_only=True)
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'slug', 'short_description', 'description',
            'category', 'price', 'form_schema', 'created_at'
        ]

class AgentExecutionSerializer(serializers.ModelSerializer):
    agent = AgentSerializer(read_only=True)
    
    class Meta:
        model = AgentExecution
        fields = [
            'id', 'agent', 'input_data', 'output_data', 'status',
            'fee_charged', 'error_message', 'execution_time',
            'created_at', 'completed_at'
        ]
```

### agents/views.py

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Agent, AgentExecution
from .serializers import AgentSerializer, AgentExecutionSerializer
import requests
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_list(request):
    """List all active agents with optional category filtering"""
    agents = Agent.objects.filter(is_active=True)
    
    category = request.GET.get('category')
    if category:
        agents = agents.filter(category__slug=category)
    
    search = request.GET.get('search')
    if search:
        agents = agents.filter(name__icontains=search)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(agents, request)
    serializer = AgentSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_detail(request, slug):
    """Get detailed agent information"""
    agent = get_object_or_404(Agent, slug=slug, is_active=True)
    serializer = AgentSerializer(agent)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_agent(request):
    """Execute an agent with provided input data"""
    agent_slug = request.data.get('agent_slug')
    input_data = request.data.get('input_data', {})
    
    if not agent_slug:
        return Response({'error': 'agent_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    agent = get_object_or_404(Agent, slug=agent_slug, is_active=True)
    
    # Check if user has sufficient balance (adjust based on your wallet system)
    if hasattr(request.user, 'wallet_balance') and request.user.wallet_balance < agent.price:
        return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create execution record
    execution = AgentExecution.objects.create(
        agent=agent,
        user=request.user,
        input_data=input_data,
        fee_charged=agent.price,
        status='pending'
    )
    
    try:
        # Deduct fee from user wallet (adjust based on your wallet system)
        if hasattr(request.user, 'deduct_balance'):
            request.user.deduct_balance(agent.price)
        
        # Call n8n webhook
        execution.status = 'running'
        execution.save()
        
        webhook_payload = {
            'execution_id': str(execution.id),
            'agent_slug': agent.slug,
            'user_id': str(request.user.id),
            'input_data': input_data
        }
        
        response = requests.post(
            agent.webhook_url,
            json=webhook_payload,
            timeout=30
        )
        
        execution.webhook_response = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'raw': response.text}
        
        if response.status_code == 200:
            execution.status = 'completed'
            execution.output_data = execution.webhook_response
        else:
            execution.status = 'failed'
            execution.error_message = f"Webhook returned {response.status_code}"
        
        execution.completed_at = timezone.now()
        execution.save()
        
        serializer = AgentExecutionSerializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except requests.RequestException as e:
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.completed_at = timezone.now()
        execution.save()
        
        return Response({
            'error': 'Failed to execute agent',
            'execution_id': str(execution.id)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_list(request):
    """List user's agent executions"""
    executions = AgentExecution.objects.filter(user=request.user)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(executions, request)
    serializer = AgentExecutionSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_detail(request, execution_id):
    """Get detailed execution information"""
    execution = get_object_or_404(AgentExecution, id=execution_id, user=request.user)
    serializer = AgentExecutionSerializer(execution)
    return Response(serializer.data)
```

### agents/urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('<slug:slug>/', views.agent_detail, name='agent_detail'),
    path('execute/', views.execute_agent, name='execute_agent'),
    path('executions/', views.execution_list, name='execution_list'),
    path('executions/<uuid:execution_id>/', views.execution_detail, name='execution_detail'),
]
```

### agents/management/commands/create_sample_agents.py

First create the directories:

```bash
mkdir -p agents/management/commands
touch agents/management/__init__.py
touch agents/management/commands/__init__.py
```

Then create the file:

```python
from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create sample agents for testing'

    def handle(self, *args, **options):
        # Create categories
        ai_category, _ = AgentCategory.objects.get_or_create(
            slug='ai-tools',
            defaults={
                'name': 'AI Tools',
                'description': 'AI-powered automation tools',
                'icon': '🤖'
            }
        )
        
        data_category, _ = AgentCategory.objects.get_or_create(
            slug='data-analysis',
            defaults={
                'name': 'Data Analysis',
                'description': 'Data processing and analysis tools',
                'icon': '📊'
            }
        )
        
        web_category, _ = AgentCategory.objects.get_or_create(
            slug='web-scraping',
            defaults={
                'name': 'Web Scraping',
                'description': 'Web data extraction tools',
                'icon': '🕷️'
            }
        )
        
        # Create sample agents
        Agent.objects.get_or_create(
            slug='pdf-analyzer',
            defaults={
                'name': 'PDF Content Analyzer',
                'short_description': 'Extract and analyze content from PDF documents',
                'description': 'This agent processes PDF files and extracts meaningful insights including summaries, keywords, and sentiment analysis. Perfect for document processing workflows.',
                'category': ai_category,
                'price': 5.00,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'pdf_url',
                            'type': 'url',
                            'label': 'PDF URL',
                            'placeholder': 'https://example.com/document.pdf',
                            'required': True
                        },
                        {
                            'name': 'analysis_type',
                            'type': 'select',
                            'label': 'Analysis Type',
                            'options': [
                                {'value': 'summary', 'label': 'Summary'},
                                {'value': 'keywords', 'label': 'Keywords'},
                                {'value': 'sentiment', 'label': 'Sentiment Analysis'}
                            ],
                            'required': True
                        }
                    ]
                },
                'webhook_url': 'https://your-n8n-instance.com/webhook/pdf-analyzer'
            }
        )
        
        Agent.objects.get_or_create(
            slug='website-scraper',
            defaults={
                'name': 'Website Data Scraper',
                'short_description': 'Extract structured data from any website',
                'description': 'Advanced web scraping agent that can extract specific data from websites using CSS selectors or XPath. Handles JavaScript-rendered content and returns clean, structured data.',
                'category': web_category,
                'price': 3.00,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'website_url',
                            'type': 'url',
                            'label': 'Website URL',
                            'placeholder': 'https://example.com',
                            'required': True
                        },
                        {
                            'name': 'selectors',
                            'type': 'textarea',
                            'label': 'CSS Selectors (one per line)',
                            'placeholder': 'h1.title\n.price\n.description',
                            'required': True
                        },
                        {
                            'name': 'wait_for_js',
                            'type': 'checkbox',
                            'label': 'Wait for JavaScript to load',
                            'required': False
                        }
                    ]
                },
                'webhook_url': 'https://your-n8n-instance.com/webhook/website-scraper'
            }
        )
        
        Agent.objects.get_or_create(
            slug='data-analyzer',
            defaults={
                'name': 'CSV Data Analyzer',
                'short_description': 'Analyze and visualize CSV data with insights',
                'description': 'Upload CSV files and get comprehensive data analysis including statistics, trends, and visualizations. Perfect for business intelligence and data exploration.',
                'category': data_category,
                'price': 4.50,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'csv_url',
                            'type': 'url',
                            'label': 'CSV File URL',
                            'placeholder': 'https://example.com/data.csv',
                            'required': True
                        },
                        {
                            'name': 'analysis_columns',
                            'type': 'text',
                            'label': 'Columns to Analyze (comma-separated)',
                            'placeholder': 'sales,revenue,date',
                            'required': False
                        },
                        {
                            'name': 'chart_type',
                            'type': 'select',
                            'label': 'Chart Type',
                            'options': [
                                {'value': 'line', 'label': 'Line Chart'},
                                {'value': 'bar', 'label': 'Bar Chart'},
                                {'value': 'pie', 'label': 'Pie Chart'},
                                {'value': 'scatter', 'label': 'Scatter Plot'}
                            ],
                            'required': False
                        }
                    ]
                },
                'webhook_url': 'https://your-n8n-instance.com/webhook/data-analyzer'
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Sample agents created successfully'))
        self.stdout.write(f'Created categories: {AgentCategory.objects.count()}')
        self.stdout.write(f'Created agents: {Agent.objects.count()}')
```

### agents/apps.py

```python
from django.apps import AppConfig

class AgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agents'
    verbose_name = 'Agents'
```

## Setup Instructions

### 1. Run Migrations

```bash
python manage.py makemigrations agents
python manage.py migrate
```

### 2. Create Sample Data

```bash
python manage.py create_sample_agents
```

### 3. Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 4. Test the API

Start the server and test these endpoints:

- `GET /api/agents/` - List all agents
- `GET /api/agents/pdf-analyzer/` - Agent details
- `POST /api/agents/execute/` - Execute an agent
- `GET /api/agents/executions/` - List executions

## API Usage Examples

### List Agents

```bash
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/agents/
```

### Execute Agent

```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_slug": "pdf-analyzer",
    "input_data": {
      "pdf_url": "https://example.com/document.pdf",
      "analysis_type": "summary"
    }
  }' \
  http://localhost:8000/api/agents/execute/
```

## Customization Notes

### User Model Integration

Update the `AgentExecution` model to reference your custom user model:

```python
# If your user model is in a different app
user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
```

### Wallet Integration

The code assumes your user model has these methods:
- `wallet_balance` property
- `deduct_balance(amount)` method

Adjust the wallet checking logic in `execute_agent` view as needed.

### n8n Webhook Format

The webhook payload sent to n8n includes:
- `execution_id`: UUID of the execution
- `agent_slug`: Identifier for the agent
- `user_id`: User who triggered the execution  
- `input_data`: Form data submitted by user

## Features Included

✅ **Agent Categories** - Organize agents by type  
✅ **Agent Management** - Full CRUD via Django admin  
✅ **Execution System** - Track agent runs with status  
✅ **Webhook Integration** - Connect to n8n workflows  
✅ **User Balance Checking** - Wallet integration ready  
✅ **REST API** - Complete API endpoints  
✅ **Pagination** - Built-in pagination for lists  
✅ **Error Handling** - Comprehensive error management  
✅ **Sample Data** - Management command for test data  
✅ **Form Schema** - Dynamic form generation support  
✅ **Admin Interface** - Django admin integration  
✅ **UUID Primary Keys** - Better security and uniqueness  

## Production Considerations

1. **Environment Variables**: Store webhook URLs and API keys in environment variables
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Caching**: Cache agent lists and categories for better performance
4. **Background Tasks**: Use Celery for long-running agent executions
5. **Logging**: Add comprehensive logging for debugging
6. **Monitoring**: Monitor webhook success rates and execution times
7. **Security**: Validate webhook responses and sanitize input data

This guide provides a complete, production-ready agents marketplace that can be easily integrated into any Django project.