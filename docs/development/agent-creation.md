# Agent Creation Guide using Template Prototype

This guide provides step-by-step instructions for creating new Django agents using the `agent_template_prototype.html` template system.

## Overview

The NetCop Hub uses a standardized template prototype (`agent_template_prototype.html`) that provides:
- Complete CSS framework with custom properties
- JavaScript utilities for common functions
- Consistent UI components (wallet card, processing status, quick access panel)
- Responsive design and accessibility features
- Toast notifications and status management

## Quick Start

### 1. Create Django Agent Structure

```bash
# Use the built-in Django command
python manage.py create_agent

# Or create manually:
mkdir your_agent_name
cd your_agent_name
touch __init__.py models.py views.py processor.py urls.py admin.py
mkdir templates
mkdir templates/your_agent_name
```

### 2. Required Files Checklist

- `__init__.py` - Empty Python package file
- `models.py` - Request model with base fields + agent-specific fields
- `processor.py` - Inherits from BaseAgentProcessor
- `views.py` - Detail view with form handling and status polling
- `urls.py` - URL patterns for detail and status endpoints
- `admin.py` - Django admin configuration
- `templates/your_agent_name/detail.html` - Converted template from prototype

## Template Conversion Process

### Step 1: Copy Base Structure from Prototype

Start with the `agent_template_prototype.html` and convert to Django template format:

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Your Agent Name - NetCop Hub{% endblock %}

{% block content %}
<div class="agent-container">
    <!-- Copy CSS from prototype within <style> tags -->
    <style>
        /* All CSS from agent_template_prototype.html lines 8-632 */
    </style>
    
    <!-- Copy HTML structure -->
    <!-- Agent Header -->
    <div class="agent-header">
        <div>
            <h1 class="agent-title">Your Agent Name</h1>
            <p class="agent-subtitle">Description of what your agent does</p>
        </div>
        <div class="header-controls">
            {% include 'components/wallet_card.html' %}
        </div>
    </div>
    
    <!-- Main agent content -->
    <!-- ... -->
</div>

<!-- Copy JavaScript from prototype -->
<script>
    /* All JavaScript from agent_template_prototype.html lines 808-967 */
</script>
{% endblock %}
```

### Step 2: Replace Placeholder Sections

Replace the placeholder sections with your agent-specific content:

**Agent Grid Section (lines 704-714 in prototype):**
```html
<div class="agent-grid">
    <div class="agent-widget widget-large">
        <div class="widget-header">
            <h3 class="widget-title">
                <span class="widget-icon">🎯</span>
                Your Agent Form
            </h3>
        </div>
        <div class="widget-content">
            {% if user.is_authenticated %}
                <form method="post" id="agentForm">
                    {% csrf_token %}
                    <!-- Your form fields here -->
                </form>
            {% else %}
                <p>Please <a href="{% url 'authentication:login' %}">login</a> to use this agent.</p>
            {% endif %}
        </div>
    </div>
    
    <!-- How It Works Widget (keep as-is from prototype) -->
    <div class="agent-widget widget-small">
        <!-- Copy from prototype lines 716-744 -->
    </div>
</div>
```

**Results Section (lines 763-774 in prototype):**
```html
<div class="agent-grid">
    <div class="agent-widget widget-wide" id="resultsSection" style="display: none;">
        <div class="widget-header">
            <h3 class="widget-title">
                <span class="widget-icon">📊</span>
                Results
            </h3>
        </div>
        <div class="widget-content">
            <div id="resultsContent">
                <!-- Agent-specific results display -->
            </div>
            <div style="display: flex; gap: var(--spacing-md); margin-top: var(--spacing-lg);">
                <button onclick="copyToClipboard(document.getElementById('resultsContent').textContent)">
                    📋 Copy Results
                </button>
                <button onclick="downloadAsFile(document.getElementById('resultsContent').textContent, 'agent_results.txt')">
                    💾 Download
                </button>
            </div>
        </div>
    </div>
</div>
```

## Django Implementation Patterns

### Models Structure

Follow this pattern for all agent models:

```python
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class YourAgentRequest(models.Model):
    """Your Agent request model"""
    
    # Base request fields (required for all agents)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=3.00)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Agent-specific fields
    your_field = models.CharField(max_length=200, help_text="Field description")
    # ... more fields
    
    # Result fields
    result_content = models.TextField(blank=True, help_text="Generated results")
    
    class Meta:
        verbose_name = "Your Agent Request"
        verbose_name_plural = "Your Agent Requests"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Your Agent - {self.your_field}"
```

### Views Pattern

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import YourAgentRequest
from .processor import YourAgentProcessor

@login_required
def your_agent_detail(request):
    if request.method == 'POST':
        # Form validation
        if not request.POST.get('required_field'):
            return JsonResponse({'error': 'Required field is missing'}, status=400)
        
        # Check wallet balance
        if request.user.wallet_balance < 3.00:
            return JsonResponse({'error': 'Insufficient balance'}, status=400)
        
        # Create request
        agent_request = YourAgentRequest.objects.create(
            user=request.user,
            your_field=request.POST.get('your_field'),
            # ... other fields
        )
        
        # Process with agent
        processor = YourAgentProcessor()
        processor.process_request(agent_request)
        
        return JsonResponse({'success': True, 'request_id': str(agent_request.id)})
    
    return render(request, 'your_agent/detail.html', {
        'agent_cost': 3.00
    })

@require_http_methods(["GET"])
def your_agent_status(request, request_id):
    try:
        agent_request = YourAgentRequest.objects.get(id=request_id, user=request.user)
        return JsonResponse({
            'status': agent_request.status,
            'result': agent_request.result_content if agent_request.status == 'completed' else None
        })
    except YourAgentRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found'}, status=404)
```

### Processor Pattern

```python
from agent_base.processors import BaseAgentProcessor

class YourAgentProcessor(BaseAgentProcessor):
    def get_cost(self):
        return 3.00
    
    def prepare_webhook_data(self, request_obj):
        return {
            'your_field': request_obj.your_field,
            # ... other fields
        }
    
    def process_webhook_response(self, request_obj, response_data):
        if response_data.get('success'):
            request_obj.result_content = response_data.get('result', '')
            request_obj.status = 'completed'
        else:
            request_obj.status = 'failed'
        
        request_obj.save()
```

## Form Integration with Template

### HTML Form Structure

```html
<form method="post" id="agentForm">
    {% csrf_token %}
    
    <div style="display: flex; flex-direction: column; gap: var(--spacing-md);">
        <div>
            <label for="your_field">Your Field:</label>
            <input type="text" id="your_field" name="your_field" required>
        </div>
        
        <!-- More form fields -->
        
        <button type="submit" 
                style="padding: var(--spacing-md); background: var(--primary); color: white; border: none; border-radius: var(--radius-md); cursor: pointer;">
            Process Request ({{ agent_cost }} AED)
        </button>
    </div>
</form>
```

### JavaScript Form Handling

Add this to your template's JavaScript section:

```javascript
// Form submission handling
document.getElementById('agentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    // Show processing status
    showProcessing();
    
    fetch('', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            pollStatus(data.request_id);
        } else {
            hideProcessing();
            showToast(data.error || 'Request failed', 'error');
        }
    })
    .catch(error => {
        hideProcessing();
        showToast('Network error occurred', 'error');
    });
});

// Status polling
function pollStatus(requestId) {
    const poll = setInterval(() => {
        fetch(`status/${requestId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    clearInterval(poll);
                    hideProcessing();
                    displayResults(data.result);
                } else if (data.status === 'failed') {
                    clearInterval(poll);
                    hideProcessing();
                    showToast('Processing failed', 'error');
                }
            });
    }, 2000);
}

// Display results
function displayResults(result) {
    document.getElementById('resultsContent').textContent = result;
    document.getElementById('resultsSection').style.display = 'block';
    showToast('Results ready!', 'success');
}
```

## Toast Messaging Standards

### Standardized Toast Messages

All agents must follow these standardized toast message patterns for consistency:

#### Success Messages
```javascript
// Agent completion - use specific agent action
AgentUtils.showToast('✅ Data analysis completed successfully!', 'success');
AgentUtils.showToast('✅ Weather report completed successfully!', 'success');
AgentUtils.showToast('✅ Email completed successfully!', 'success');
```

#### Clipboard Operations
```javascript
// Always use this exact message for clipboard operations
navigator.clipboard.writeText(text).then(() => {
    AgentUtils.showToast('📋 Copied to clipboard!', 'success');
}).catch(() => {
    AgentUtils.showToast('❌ Failed to copy to clipboard', 'error');
});
```

#### Error Messages
```javascript
// Use ❌ emoji prefix for all error messages
AgentUtils.showToast('❌ Network error occurred', 'error');
AgentUtils.showToast('❌ Insufficient wallet balance', 'error');
AgentUtils.showToast('❌ Processing failed', 'error');
```

#### No Toast Scenarios
Do NOT show toast messages for:
- **Download operations** - File download is confirmation enough
- **Reset operations** - Visual feedback is sufficient
- **Form validation** - Use inline error messages instead

### Toast Function Naming

Each agent should maintain its own utils object with a `showToast` method:

```javascript
// Data Analyzer
const DataAnalyzerUtils = {
    showToast(message, type = 'info') { /* standard implementation */ }
};

// Social Ads Generator  
const SocialAdsUtils = {
    showToast(message, type = 'info') { /* standard implementation */ }
};

// Weather Reporter
const WeatherUtils = {
    showToast(message, type = 'info') { /* standard implementation */ }
};
```

## Dynamic Pricing Implementation

### Template Variables

All pricing must use dynamic template variables instead of hardcoded values:

#### Button Text
```html
<!-- CORRECT -->
<button type="submit" class="btn btn-primary btn-full">
    🚀 Analyze Data ({{ agent.price }} AED)
</button>

<!-- INCORRECT -->  
<button type="submit" class="btn btn-primary btn-full">
    🚀 Analyze Data (5.00 AED)
</button>
```

#### Balance Validation  
```html
<!-- CORRECT -->
{% if user.wallet_balance >= agent.price %}
    <button>Process Request</button>
{% else %}
    <div class="alert alert-error">
        Insufficient balance! You need {{ agent.price }} AED.
    </div>
{% endif %}

<!-- INCORRECT -->
{% if user.wallet_balance >= 5.00 %}
```

#### JavaScript Price Checks
```javascript
// CORRECT - Use template variable
document.body.setAttribute('data-agent-price', '{{ agent.price }}');
const agentPrice = parseFloat(document.body.getAttribute('data-agent-price'));

if (walletBalance < agentPrice) {
    showToast('Insufficient wallet balance', 'error');
}

// INCORRECT - Hardcoded value
if (walletBalance < 5.00) {
```

### Agent Context Required

Ensure your view passes the agent context:

```python
# views.py
from agent_base.models import BaseAgent

def your_agent_detail(request):
    try:
        agent = BaseAgent.objects.get(slug='your-agent-slug')
    except BaseAgent.DoesNotExist:
        # Handle missing agent
        pass
        
    context = {
        'agent': agent,  # Required for {{ agent.price }}
        # other context...
    }
    return render(request, 'your_agent/detail.html', context)
```

## Best Practices for Agent Modifications

### Preserving Existing Functionality

When updating agents, follow these critical guidelines:

#### DO NOT Break Result Display Logic
```javascript
// CORRECT - Preserve agent-specific utils and function names
const DataAnalyzerUtils = {
    displayResults(result) { /* existing logic */ }
};

// INCORRECT - Don't change to generic names
const AgentUtils = {
    displayResults(result) { /* breaks existing calls */ }
};
```

#### Each Agent Has Unique Display Patterns
Different agents handle results differently:
- **Data Analyzer**: Formatted HTML output with sections
- **Weather Reporter**: Text-based reports with immediate API response
- **Social Ads**: Multiple ad variants with copy/download options
- **Email Writer**: Rich text formatting with email structure

**Never standardize result display logic across agents.**

#### Safe Modification Approach
1. **Test Before Changes**: Always verify current functionality works
2. **Isolated Updates**: Change only what's explicitly requested
3. **Preserve Names**: Keep existing function and object names
4. **Incremental Testing**: Test after each small change

### Common Pitfalls to Avoid

#### Over-Standardization
```javascript
// WRONG - Don't rename existing functions
// Before: DataAnalyzerUtils.displayResults()
// After: AgentUtils.displayResults() // BREAKS FUNCTIONALITY

// CORRECT - Keep existing structure, update content only
// Before: showToast('Data copied!', 'success');
// After: showToast('📋 Copied to clipboard!', 'success');
```

#### Breaking Function Calls
```javascript
// WRONG - Changing function names breaks templates
SocialAdsUtils.displayResults() → AgentUtils.displayResults()

// CORRECT - Preserve all function names and calling patterns
SocialAdsUtils.displayResults() → SocialAdsUtils.displayResults()
```

#### Git Recovery When Things Break
If agent functionality breaks:
```bash
# Check what changed
git status
git diff

# Reset to last working commit
git log --oneline -10
git reset --hard <commit-hash>

# Verify functionality restored
python manage.py runserver
# Test affected agents manually
```

## URL Configuration

### App URLs (`your_agent/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'your_agent'

urlpatterns = [
    path('', views.your_agent_detail, name='detail'),
    path('status/<uuid:request_id>/', views.your_agent_status, name='status'),
]
```

### Main URLs (add to `netcop_hub/urls.py`)

```python
path('agents/your-agent-slug/', include('your_agent.urls')),
```

### Settings (add to `INSTALLED_APPS`)

```python
INSTALLED_APPS = [
    # ... existing apps
    'your_agent',
]
```

## Database and Marketplace Integration

### 1. Create and Apply Migrations

```bash
python manage.py makemigrations your_agent
python manage.py migrate
```

### 2. Add to Marketplace Catalog

```bash
python manage.py shell
```

```python
from agent_base.models import BaseAgent

BaseAgent.objects.create(
    name="Your Agent Name",
    slug="your-agent-slug",
    description="Description of what your agent does...",
    category="content",  # or appropriate category
    price=3.00,
    icon="🎯",  # appropriate emoji
    agent_type="webhook"
)
```

## Common Components Reference

### Available CSS Components

- **Layout**: `.agent-container`, `.agent-header`, `.agent-grid`
- **Widgets**: `.agent-widget`, `.widget-header`, `.widget-title`, `.widget-content`
- **Sizes**: `.widget-large`, `.widget-small`, `.widget-wide`
- **Wallet**: `.wallet-card` (use `{% include 'components/wallet_card.html' %}`)
- **Status**: `.processing-status`, `.status-icon`, `.status-title`
- **Utilities**: `.info-list`, `.placeholder-section`

### Available JavaScript Functions

- `showToast(message, type)` - Display notifications
- `showProcessing()` / `hideProcessing()` - Processing status
- `copyToClipboard(text, message)` - Copy functionality
- `downloadAsFile(text, filename, message)` - Download functionality
- `toggleQuickAgents()` - Quick access panel
- `updateWalletBalance(balance)` - Update wallet display

## Testing and Verification

### 1. Django Check

```bash
python manage.py check
```

### 2. URL Resolution Test

```bash
python manage.py shell
```

```python
from django.urls import reverse
print(reverse('your_agent:detail'))
```

### 3. Agent Marketplace Test

Visit `/marketplace/` to verify your agent appears in the catalog.

## Best Practices

1. **Always inherit CSS and JavaScript** from the prototype - don't modify the template utilities
2. **Use consistent naming** - follow the existing patterns for models, views, and URLs
3. **Preserve accessibility** - keep ARIA attributes and keyboard navigation
4. **Test responsive design** - verify mobile functionality
5. **Follow security practices** - use CSRF tokens, validate inputs, check permissions
6. **Maintain consistent pricing** - use decimal values with 2 places
7. **Handle errors gracefully** - provide meaningful error messages via toast notifications
8. **Preserve existing functionality** - Never break result display logic when making updates
9. **Test after each change** - Verify functionality works before proceeding to next modification
10. **Use git for safety** - Commit working states and reset if changes break functionality

## Testing Procedures for Agent Modifications

### Pre-Modification Testing
```bash
# 1. Test current functionality
python manage.py runserver
# Visit agent page and test full workflow

# 2. Create git checkpoint
git add .
git commit -m "Working state before modifications"
```

### During Modification Testing
```bash
# Test after each significant change
python manage.py runserver
# Test the specific functionality you modified

# If something breaks:
git status
git diff
# Identify the breaking change and fix or revert
```

### Post-Modification Testing
```bash
# 1. Full agent workflow test
# - Form submission
# - Processing status display
# - Results display
# - Copy/download functionality

# 2. Cross-agent functionality test
# - Quick agents panel
# - Navigation between agents
# - Wallet balance updates

# 3. Browser console check
# - No JavaScript errors
# - No broken network requests
```

## Troubleshooting

### Common Issues

1. **CSS not loading**: Ensure all CSS from prototype is copied within `<style>` tags
2. **JavaScript errors**: Check that all utility functions are included
3. **Form submission fails**: Verify CSRF token and POST data validation
4. **Agent not in marketplace**: Check BaseAgent database entry and migrations
5. **Template not found**: Verify template directory structure matches app name

### Debug Commands

```bash
# Check database
python manage.py check_db

# Shell debugging
python manage.py shell

# View agent catalog
python manage.py shell
>>> from agent_base.models import BaseAgent
>>> BaseAgent.objects.all()
```

This guide ensures consistent, maintainable agent creation using the proven template prototype system.

## Recent Improvements (July 2025)

### ✅ Toast Messaging Standardization
All agents now use consistent toast messages:
- **Success**: `✅ [Action] completed successfully!`
- **Clipboard**: `📋 Copied to clipboard!`
- **Errors**: `❌ [Error description]`
- **Removed**: Download and reset toast notifications (visual feedback sufficient)

### ✅ Dynamic Pricing Implementation
All agents now use `{{ agent.price }}` template variables instead of hardcoded prices:
- Button text: `Process Request ({{ agent.price }} AED)`
- Balance validation: `{% if user.wallet_balance >= agent.price %}`
- JavaScript checks: `data-agent-price="{{ agent.price }}"`

### ✅ Enhanced Agent Template Architecture
- Improved component-based template structure
- Standardized CSS and JavaScript utilities
- Better security with XSS prevention
- Consistent wallet balance integration

These improvements ensure all agents maintain consistent user experience while syncing with Railway database pricing changes.