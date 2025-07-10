# Complete Manual Agent Creation Guide

This guide provides step-by-step instructions for manually creating AI agents in the NetCop Hub platform.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create Django App](#step-1-create-django-app)
4. [Step 2: Design Models](#step-2-design-models)
5. [Step 3: Create Processor](#step-3-create-processor)
6. [Step 4: Implement Views](#step-4-implement-views)
7. [Step 5: Configure URLs](#step-5-configure-urls)
8. [Step 6: Create Templates](#step-6-create-templates)
9. [Step 7: Integration](#step-7-integration)
10. [Step 8: Testing](#step-8-testing)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Customization](#advanced-customization)

## Overview

### Agent Types
- **API Agents**: Direct integration with external APIs (e.g., OpenWeather, Stripe)
- **Webhook Agents**: Integration with N8N workflows or custom webhooks

### Architecture
Each agent is a separate Django app that extends the base agent framework:
- `BaseAgent`: Marketplace catalog entry
- `BaseAgentRequest`/`BaseAgentResponse`: Request/response tracking
- `BaseAgentProcessor`: Processing logic (API or webhook)
- `BaseAgentView`: Form handling and authentication

## Prerequisites

1. Django project setup and running
2. Base agent framework installed (`agent_base` app)
3. Authentication system configured
4. Wallet system for payments

## Step 1: Create Django App

### 1.1 Create the App
```bash
python manage.py startapp agent_[name]
# Example: python manage.py startapp agent_pdf_analyzer
```

### 1.2 App Structure
```
agent_pdf_analyzer/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── processor.py
├── views.py
├── urls.py
├── migrations/
│   └── __init__.py
└── templates/
    └── agent_pdf_analyzer/
        └── detail.html
```

### 1.3 Configure Apps.py
```python
# agent_pdf_analyzer/apps.py
from django.apps import AppConfig

class AgentPdfAnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent_pdf_analyzer'
```

## Step 2: Design Models

### 2.1 Request Model
```python
# agent_pdf_analyzer/models.py
from django.db import models
from agent_base.models import BaseAgentRequest, BaseAgentResponse

class PdfAnalyzerRequest(BaseAgentRequest):
    """PDF Analyzer request tracking"""
    
    # Agent-specific fields
    pdf_file = models.FileField(upload_to='uploads/pdf/')
    analysis_type = models.CharField(
        max_length=50,
        choices=[
            ('summary', 'Document Summary'),
            ('extraction', 'Data Extraction'),
            ('sentiment', 'Sentiment Analysis'),
        ],
        default='summary'
    )
    language = models.CharField(max_length=10, default='en')
    
    class Meta:
        db_table = 'pdf_analyzer_requests'
        verbose_name = 'PDF Analyzer Request'
        verbose_name_plural = 'PDF Analyzer Requests'
```

### 2.2 Response Model
```python
class PdfAnalyzerResponse(BaseAgentResponse):
    """PDF Analyzer response storage"""
    
    request = models.OneToOneField(
        PdfAnalyzerRequest, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Response-specific fields
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'pdf_analyzer_responses'
        verbose_name = 'PDF Analyzer Response'
        verbose_name_plural = 'PDF Analyzer Responses'
```

## Step 3: Create Processor

Choose between API or Webhook processor based on your integration needs.

### 3.1 API Processor Example
```python
# agent_pdf_analyzer/processor.py
from agent_base.processors import StandardAPIProcessor
from django.utils import timezone
from .models import PdfAnalyzerRequest, PdfAnalyzerResponse
import json

class PdfAnalyzerProcessor(StandardAPIProcessor):
    """API processor for PDF Analyzer agent"""
    
    agent_slug = 'pdf-analyzer'
    api_base_url = 'https://api.docparser.com/v1/process'
    api_key_env = 'DOCPARSER_API_KEY'
    auth_method = 'bearer'
    
    def prepare_request_data(self, **kwargs):
        """Prepare API request data"""
        return {
            'file_url': kwargs.get('pdf_file_url'),
            'analysis_type': kwargs.get('analysis_type', 'summary'),
            'language': kwargs.get('language', 'en'),
        }
    
    def should_use_get(self, **kwargs):
        """Use POST for file uploads"""
        return False
    
    def process_response(self, response_data, request_obj):
        """Process the API response"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract response data
            extracted_text = response_data.get('extracted_text', '')
            summary = response_data.get('summary', '')
            key_points = response_data.get('key_points', [])
            sentiment_score = response_data.get('sentiment_score')
            confidence_score = response_data.get('confidence', 0.0)
            
            # Create response object
            response_obj = PdfAnalyzerResponse.objects.create(
                request=request_obj,
                success=response_data.get('success', True),
                processing_time=response_data.get('processing_time', 0),
                extracted_text=extracted_text,
                summary=summary,
                key_points=key_points,
                sentiment_score=sentiment_score,
                confidence_score=confidence_score,
            )
            
            # Update request as completed
            request_obj.status = 'completed'
            request_obj.processed_at = timezone.now()
            request_obj.save()
            
            return response_obj
            
        except Exception as e:
            # Handle error
            request_obj.status = 'failed'
            request_obj.save()
            
            # Create error response
            error_response = PdfAnalyzerResponse.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=response_data.get('processing_time', 0)
            )
            
            raise Exception(f"Failed to process PDF Analyzer response: {e}")
```

### 3.2 Webhook Processor Example
```python
# For N8N webhook integration
from agent_base.processors import StandardWebhookProcessor

class PdfAnalyzerProcessor(StandardWebhookProcessor):
    """Webhook processor for PDF Analyzer agent"""
    
    agent_slug = 'pdf-analyzer'
    webhook_url = settings.N8N_WEBHOOK_PDF_ANALYZER
    agent_id = '789'
    
    def prepare_message_text(self, **kwargs):
        """Prepare message for N8N webhook"""
        analysis_type = kwargs.get('analysis_type', 'summary')
        pdf_file = kwargs.get('pdf_file')
        
        return f"Analyze PDF file: {pdf_file.name}, Type: {analysis_type}"
    
    def process_response(self, response_data, request_obj):
        """Process webhook response"""
        # Similar to API processor but for webhook data format
        pass
```

## Step 4: Implement Views

### 4.1 Detail View
```python
# agent_pdf_analyzer/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from agent_base.models import BaseAgent
from .models import PdfAnalyzerRequest, PdfAnalyzerResponse
from .processor import PdfAnalyzerProcessor
import json

@login_required
def pdf_analyzer_detail(request):
    """Detail page for PDF Analyzer agent"""
    try:
        agent = BaseAgent.objects.get(slug='pdf-analyzer')
    except BaseAgent.DoesNotExist:
        messages.error(request, 'PDF Analyzer agent not found.')
        return redirect('core:homepage')
    
    # Get user's recent requests
    user_requests = PdfAnalyzerRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'agent': agent,
        'user_requests': user_requests
    }
    return render(request, 'agent_pdf_analyzer/detail.html', context)
```

### 4.2 Process View
```python
@method_decorator(csrf_exempt, name='dispatch')
class PdfAnalyzerProcessView(View):
    """Process PDF Analyzer requests"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            # Handle multipart form data for file uploads
            pdf_file = request.FILES.get('pdf_file')
            analysis_type = request.POST.get('analysis_type', 'summary')
            language = request.POST.get('language', 'en')
            
            if not pdf_file:
                return JsonResponse({'error': 'PDF file is required'}, status=400)
            
            # Get agent
            agent = BaseAgent.objects.get(slug='pdf-analyzer')
            
            # Check wallet balance
            if not request.user.has_sufficient_balance(agent.price):
                return JsonResponse({'error': 'Insufficient wallet balance'}, status=400)
            
            # Create request object
            agent_request = PdfAnalyzerRequest.objects.create(
                user=request.user,
                agent=agent,
                cost=agent.price,
                pdf_file=pdf_file,
                analysis_type=analysis_type,
                language=language,
            )
            
            # Deduct from wallet
            request.user.deduct_balance(
                agent.price, 
                f"PDF Analyzer request for {pdf_file.name}", 
                'pdf-analyzer'
            )
            
            # Process request
            processor = PdfAnalyzerProcessor()
            result = processor.process_request(
                request_obj=agent_request,
                user_id=request.user.id,
                pdf_file_url=agent_request.pdf_file.url,
                analysis_type=analysis_type,
                language=language,
            )
            
            return JsonResponse({
                'success': True,
                'request_id': str(agent_request.id),
                'message': 'PDF Analyzer request processed successfully'
            })
            
        except BaseAgent.DoesNotExist:
            return JsonResponse({'error': 'PDF Analyzer agent not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

### 4.3 Result View
```python
@login_required
def pdf_analyzer_result(request, request_id):
    """Get result for a specific request"""
    try:
        agent_request = PdfAnalyzerRequest.objects.get(
            id=request_id,
            user=request.user
        )
        
        if hasattr(agent_request, 'response'):
            response = agent_request.response
            return JsonResponse({
                'success': response.success,
                'status': agent_request.status,
                'extracted_text': response.extracted_text,
                'summary': response.summary,
                'key_points': response.key_points,
                'sentiment_score': response.sentiment_score,
                'confidence_score': response.confidence_score,
                'processing_time': float(response.processing_time) if response.processing_time else None,
                'error_message': response.error_message
            })
        else:
            return JsonResponse({
                'success': False,
                'status': agent_request.status,
                'message': 'Processing in progress...'
            })
            
    except PdfAnalyzerRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Step 5: Configure URLs

### 5.1 App URLs
```python
# agent_pdf_analyzer/urls.py
from django.urls import path
from . import views

app_name = 'pdf_analyzer'

urlpatterns = [
    path('', views.pdf_analyzer_detail, name='detail'),
    path('process/', views.PdfAnalyzerProcessView.as_view(), name='process'),
    path('result/<uuid:request_id>/', views.pdf_analyzer_result, name='result'),
]
```

### 5.2 Main URL Registration
```python
# netcop_hub/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('agents/weather-reporter/', include('weather_reporter.urls')),
    path('agents/pdf-analyzer/', include('agent_pdf_analyzer.urls')),  # Add this line
    path('', include('core.urls')),
]
```

## Step 6: Create Templates

### 6.1 Create Template Directory
```bash
mkdir -p agent_pdf_analyzer/templates/agent_pdf_analyzer/
```

### 6.2 Detail Template
```html
<!-- agent_pdf_analyzer/templates/agent_pdf_analyzer/detail.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Analyzer Agent - NetCop AI Hub</title>
    <style>
        /* Copy styles from weather reporter template and customize */
        /* Ensure responsive design and professional appearance */
    </style>
</head>
<body>
    <div style="min-height: 100vh; background: linear-gradient(135deg, #f6f8ff 0%, #e8f0fe 50%, #f0f7ff 100%); padding: 40px 0;">
        <!-- Navigation -->
        <nav style="background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px); padding: 16px 0; margin-bottom: 24px;">
            <div class="container">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <a href="{% url 'core:homepage' %}" style="font-size: 24px; font-weight: 700; color: #3b82f6; text-decoration: none;">
                        🚀 NetCop AI Hub
                    </a>
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <a href="{% url 'core:marketplace' %}" style="color: #374151; text-decoration: none;">Marketplace</a>
                        {% if user.is_authenticated %}
                            <a href="{% url 'core:wallet' %}" style="color: #374151; text-decoration: none;">Wallet</a>
                            <span style="color: #6b7280;">{{ user.wallet_balance|floatformat:2 }} AED</span>
                        {% else %}
                            <a href="{% url 'authentication:login' %}" style="color: #3b82f6; text-decoration: none;">Login</a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </nav>
        
        <div class="container">
            <!-- Page Title -->
            <div style="text-align: center; margin-bottom: 40px;">
                <h1 style="font-size: 36px; font-weight: 700; color: #1f2937; margin: 0 0 16px 0;">
                    📄 PDF Analyzer Agent
                </h1>
                <p style="font-size: 18px; color: #6b7280; margin: 0; max-width: 600px; margin: 0 auto;">
                    Extract text, generate summaries, and analyze sentiment from PDF documents using advanced AI.
                </p>
                <div style="background: rgba(59, 130, 246, 0.1); color: #1e40af; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-top: 12px; font-weight: 600;">
                    💰 Cost: {{ agent.price }} AED
                </div>
            </div>
            
            <!-- Messages -->
            {% if messages %}
                {% for message in messages %}
                    <div class="{% if message.tags == 'error' %}error-message{% else %}success-message{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
            
            <!-- Main Content -->
            <div class="grid" style="display: grid; grid-template-columns: 1fr 400px; gap: 24px; align-items: start;">
                <!-- PDF Upload Form -->
                <div>
                    <form method="POST" id="pdfForm" enctype="multipart/form-data">
                        {% csrf_token %}
                        
                        <!-- File Upload -->
                        <div class="card" style="background: rgba(255, 255, 255, 0.9); border-radius: 16px; padding: 24px; margin-bottom: 24px;">
                            <h3 style="font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 16px;">📁 Upload PDF Document</h3>
                            
                            <div class="form-group" style="margin-bottom: 20px;">
                                <input type="file" name="pdf_file" id="pdf_file" accept=".pdf" required 
                                       style="width: 100%; padding: 16px; border: 2px dashed #d1d5db; border-radius: 12px; background: #f9fafb;">
                                <div style="font-size: 14px; color: #6b7280; margin-top: 8px;">
                                    Supported: PDF files up to 10MB
                                </div>
                            </div>
                        </div>
                        
                        <!-- Analysis Options -->
                        <div class="card" style="background: rgba(255, 255, 255, 0.9); border-radius: 16px; padding: 24px; margin-bottom: 24px;">
                            <h3 style="font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 16px;">⚙️ Analysis Options</h3>
                            
                            <div class="form-group" style="margin-bottom: 20px;">
                                <label style="display: block; font-weight: 600; margin-bottom: 8px;">Analysis Type:</label>
                                <select name="analysis_type" style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px;">
                                    <option value="summary">Document Summary</option>
                                    <option value="extraction">Data Extraction</option>
                                    <option value="sentiment">Sentiment Analysis</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label style="display: block; font-weight: 600; margin-bottom: 8px;">Language:</label>
                                <select name="language" style="width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px;">
                                    <option value="en">English</option>
                                    <option value="ar">Arabic</option>
                                    <option value="fr">French</option>
                                    <option value="es">Spanish</option>
                                </select>
                            </div>
                        </div>
                    </form>
                </div>
                
                <!-- Sidebar -->
                <div>
                    <!-- Wallet Balance Card -->
                    <div class="card" style="background: rgba(255, 255, 255, 0.9); border-radius: 16px; padding: 24px; margin-bottom: 24px;">
                        <h3 style="font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 16px;">💳 Your Wallet</h3>
                        
                        <div style="margin-bottom: 20px;">
                            <div style="font-size: 28px; font-weight: 700; color: #1f2937;">
                                {% if user.is_authenticated %}
                                    {{ user.wallet_balance|floatformat:2 }} AED
                                {% else %}
                                    0.00 AED
                                {% endif %}
                            </div>
                            <div style="font-size: 16px; color: #6b7280;">Available Balance</div>
                        </div>
                        
                        {% if user.is_authenticated %}
                            {% if user.wallet_balance >= agent.price %}
                                <button type="submit" form="pdfForm" class="btn btn-primary" style="width: 100%; padding: 16px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer;">
                                    📄 Analyze PDF ({{ agent.price }} AED)
                                </button>
                            {% else %}
                                <div style="background: #fef2f2; border: 1px solid #fca5a5; color: #dc2626; padding: 12px; border-radius: 8px; text-align: center; margin-bottom: 12px;">
                                    Insufficient balance! You need {{ agent.price }} AED.
                                </div>
                                <a href="{% url 'core:wallet_topup' %}" style="display: block; width: 100%; padding: 16px; background: #10b981; color: white; text-decoration: none; border-radius: 12px; text-align: center; font-weight: 600;">
                                    💰 Top Up Wallet
                                </a>
                            {% endif %}
                        {% else %}
                            <a href="{% url 'authentication:login' %}" style="display: block; width: 100%; padding: 16px; background: #10b981; color: white; text-decoration: none; border-radius: 12px; text-align: center; font-weight: 600;">
                                🔑 Login to Continue
                            </a>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Add AJAX form submission similar to weather reporter
        document.getElementById('pdfForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate file upload
            const fileInput = document.getElementById('pdf_file');
            if (!fileInput.files[0]) {
                alert('Please select a PDF file');
                return;
            }
            
            // Create FormData for file upload
            const formData = new FormData(this);
            
            // Submit via AJAX
            fetch('{% url "pdf_analyzer:process" %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('PDF analysis started! Refreshing page...');
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while processing your request');
            });
        });
    </script>
</body>
</html>
```

## Step 7: Integration

### 7.1 Add to Django Settings
```python
# netcop_hub/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Core apps
    'core',
    'authentication',
    'wallet',
    'agent_base',
    
    # Agent apps
    'weather_reporter',
    'agent_pdf_analyzer',  # Add this line
]
```

### 7.2 Run Migrations
```bash
python manage.py makemigrations agent_pdf_analyzer
python manage.py migrate
```

### 7.3 Create BaseAgent Entry
```python
# In Django shell or management command
python manage.py shell

from agent_base.models import BaseAgent
from decimal import Decimal

BaseAgent.objects.create(
    name="PDF Analyzer",
    slug="pdf-analyzer",
    description="Extract text, generate summaries, and analyze sentiment from PDF documents",
    category="utilities",
    price=Decimal('5.00'),
    icon="📄",
    agent_type="api",
    rating=Decimal('4.5'),
    review_count=25,
    is_active=True
)
```

### 7.4 Environment Variables
```bash
# Add to .env file
DOCPARSER_API_KEY=your_api_key_here
```

### 7.5 Admin Configuration
```python
# agent_pdf_analyzer/admin.py
from django.contrib import admin
from .models import PdfAnalyzerRequest, PdfAnalyzerResponse

@admin.register(PdfAnalyzerRequest)
class PdfAnalyzerRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'analysis_type', 'created_at']
    list_filter = ['status', 'analysis_type', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'processed_at']

@admin.register(PdfAnalyzerResponse)
class PdfAnalyzerResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'success', 'confidence_score', 'created_at']
    list_filter = ['success', 'created_at']
    readonly_fields = ['id', 'created_at']
```

## Step 8: Testing

### 8.1 Test Checklist
- [ ] Agent appears in marketplace
- [ ] Agent detail page loads correctly
- [ ] Authentication required for access
- [ ] File upload works
- [ ] Form submission processes correctly
- [ ] Wallet balance is checked
- [ ] Payment is deducted
- [ ] Processing completes successfully
- [ ] Results are displayed
- [ ] Error handling works

### 8.2 Test Commands
```bash
# Test URL routing
python manage.py check

# Test database queries
python manage.py shell
>>> from agent_pdf_analyzer.models import *
>>> from agent_base.models import BaseAgent
>>> BaseAgent.objects.filter(slug='pdf-analyzer').exists()

# Test processor
>>> from agent_pdf_analyzer.processor import PdfAnalyzerProcessor
>>> processor = PdfAnalyzerProcessor()
>>> # Test with sample data
```

### 8.3 Browser Testing
1. Visit `/marketplace/` - verify agent appears
2. Click "Use Agent" - verify redirect to detail page
3. Try without login - verify authentication required
4. Upload test PDF file
5. Submit form and monitor processing
6. Check wallet balance deduction
7. Verify results display

## Troubleshooting

### Common Issues

#### 1. URL Namespace Errors
**Error**: `NoReverseMatch: Reverse for 'wallet' not found`
**Fix**: Use proper namespaces in templates:
```html
<!-- Wrong -->
{% url 'wallet' %}

<!-- Correct -->
{% url 'core:wallet' %}
```

#### 2. Template Not Found
**Error**: `TemplateDoesNotExist: detail.html`
**Fix**: Ensure template is in correct location within the agent app:
```bash
# Correct location:
agent_[name]/templates/agent_[name]/detail.html

# Example:
agent_pdf_analyzer/templates/agent_pdf_analyzer/detail.html

# NOT in global templates folder
# Restart Django server after moving templates
```

**Test template loading**:
```bash
python manage.py shell -c "
from django.template.loader import get_template
template = get_template('agent_pdf_analyzer/detail.html')
print('✅ Template found:', template.origin.name)
"
```

#### 3. Migration Issues
**Error**: Database migration fails
**Fix**: 
```bash
python manage.py makemigrations agent_[name] --empty
# Edit migration file if needed
python manage.py migrate
```

#### 4. Import Errors
**Error**: Module import fails
**Fix**: Check `INSTALLED_APPS` and Python path:
```python
# Ensure app is in INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'agent_pdf_analyzer',
]
```

#### 5. File Upload Issues
**Error**: File upload fails
**Fix**: Configure media settings:
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# urls.py (in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 6. API Integration Issues
**Error**: External API calls fail
**Fix**: Check API credentials and endpoints:
```python
# Test API connection
import requests
response = requests.get('https://api.example.com/test', headers={'Authorization': 'Bearer YOUR_KEY'})
print(response.status_code, response.text)
```

## Advanced Customization

### Custom Field Types
```python
# For complex data structures
class PdfAnalyzerRequest(BaseAgentRequest):
    # JSON field for complex configurations
    analysis_config = models.JSONField(default=dict, blank=True)
    
    # Custom validation
    def clean(self):
        super().clean()
        if self.pdf_file and self.pdf_file.size > 10 * 1024 * 1024:  # 10MB
            raise ValidationError('PDF file too large (max 10MB)')
```

### Custom Business Logic
```python
# Override processor methods for custom logic
class PdfAnalyzerProcessor(StandardAPIProcessor):
    
    def pre_process_request(self, request_obj, **kwargs):
        """Custom logic before API call"""
        # Validate file format
        # Compress large files
        # Extract metadata
        pass
    
    def post_process_response(self, response_obj, **kwargs):
        """Custom logic after API response"""
        # Generate additional insights
        # Send notifications
        # Update analytics
        pass
```

### Multiple API Integration
```python
class PdfAnalyzerProcessor(StandardAPIProcessor):
    
    def process_request(self, request_obj, **kwargs):
        """Custom multi-step processing"""
        # Step 1: Extract text
        text_response = self.call_text_extraction_api(**kwargs)
        
        # Step 2: Analyze sentiment
        sentiment_response = self.call_sentiment_api(text_response['text'])
        
        # Step 3: Generate summary
        summary_response = self.call_summary_api(text_response['text'])
        
        # Combine results
        combined_response = {
            'extracted_text': text_response['text'],
            'sentiment': sentiment_response['sentiment'],
            'summary': summary_response['summary'],
        }
        
        return self.process_response(combined_response, request_obj)
```

### Custom Template Components
```html
<!-- Reusable components -->
{% include 'components/file_upload.html' with accept='.pdf' max_size='10MB' %}
{% include 'components/progress_bar.html' with status=request.status %}
{% include 'components/result_display.html' with response=response %}
```

### Error Handling Patterns
```python
class PdfAnalyzerProcessor(StandardAPIProcessor):
    
    def handle_api_error(self, error, request_obj):
        """Custom error handling"""
        if 'rate_limit' in str(error).lower():
            # Retry after delay
            return self.retry_with_delay(request_obj, delay=60)
        elif 'invalid_file' in str(error).lower():
            # User error - don't retry
            return self.create_error_response(request_obj, "Invalid PDF file format")
        else:
            # Unknown error - log and notify
            self.log_error(error, request_obj)
            return super().handle_api_error(error, request_obj)
```

## Best Practices

1. **Security**: Always validate file uploads, sanitize inputs, check permissions
2. **Performance**: Implement caching, optimize database queries, handle large files efficiently
3. **User Experience**: Provide clear feedback, show progress indicators, handle errors gracefully
4. **Maintainability**: Use consistent naming, document complex logic, write tests
5. **Monitoring**: Log important events, track usage metrics, monitor error rates

## Summary

This guide covers the complete process of creating an AI agent manually in the NetCop Hub platform. Following these steps ensures your agent integrates properly with the authentication, payment, and processing systems while providing a professional user experience.

For automated agent creation, use the `create_agent` management command, but this manual approach gives you full control over customization and complex business logic.