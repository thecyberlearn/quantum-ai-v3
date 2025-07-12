# Error Prevention Guide for Agent Creation

## 🎯 Based on 5 Whys Analyzer Debugging Experience

This guide documents all the common errors encountered during agent development and their proven solutions, based on extensive debugging work that led to the successful 5 Whys Analyzer implementation.

---

## 📋 Table of Contents

1. [Template Loading Errors](#template-loading-errors)
2. [URL Routing Issues](#url-routing-issues)
3. [Database Migration Conflicts](#database-migration-conflicts)
4. [Wallet Integration Problems](#wallet-integration-problems)
5. [Session Management Issues](#session-management-issues)
6. [Status Tracking Problems](#status-tracking-problems)
7. [Error Handling Failures](#error-handling-failures)
8. [Environment Variable Issues](#environment-variable-issues)
9. [N8N Webhook Problems](#n8n-webhook-problems)
10. [Performance and Index Issues](#performance-and-index-issues)

---

## 1. Template Loading Errors

### ❌ Common Error
```
TemplateDoesNotExist: detail.html
django.template.loader.TemplateDoesNotExist: detail.html
```

### 🔍 Root Cause Analysis
- Template in wrong directory structure
- Django server cache holding old template paths
- Missing app in INSTALLED_APPS
- Incorrect template naming convention

### ✅ 5 Whys Learned Solution

**Correct Template Structure:**
```bash
# ✅ Correct - 5 Whys pattern
agent_five_whys_analyzer/
└── templates/
    └── five_whys_analyzer/
        └── detail.html

# ❌ Wrong - causes TemplateDoesNotExist
agent_five_whys_analyzer/
└── templates/
    └── detail.html  # Missing app subdirectory
```

**Template Path Validation Script:**
```bash
# Test template loading before starting server
python manage.py shell -c "
from django.template.loader import get_template
try:
    template = get_template('five_whys_analyzer/detail.html')
    print('✅ Template found:', template.origin.name)
except Exception as e:
    print('❌ Template error:', e)
"
```

**Critical Fix Steps:**
1. Create proper directory structure
2. Move template to correct location
3. **RESTART Django server** (cache issue)
4. Verify template loading with shell command

### 🛡️ Prevention Strategy
```bash
# Template creation checklist
mkdir -p [agent_name]/templates/[agent_name]/
cp existing_working_template.html [agent_name]/templates/[agent_name]/detail.html
# Always restart server after template changes
```

---

## 2. URL Routing Issues

### ❌ Common Errors
```
NoReverseMatch: Reverse for 'wallet' not found
django.urls.exceptions.NoReverseMatch at /agents/five-whys-analyzer/
```

### 🔍 Root Cause Analysis
- Missing URL namespaces in templates
- Incorrect URL registration order
- Agent URLs placed after catch-all core URLs

### ✅ 5 Whys Learned Solution

**Correct URL Namespacing in Templates:**
```html
<!-- ❌ Wrong - causes NoReverseMatch -->
<a href="{% url 'wallet' %}">Wallet</a>
<a href="{% url 'homepage' %}">Home</a>

<!-- ✅ Correct - 5 Whys pattern -->
<a href="{% url 'core:wallet' %}">Wallet</a>
<a href="{% url 'core:homepage' %}">Home</a>
<a href="{% url 'authentication:login' %}">Login</a>
```

**Correct URL Registration Order:**
```python
# netcop_hub/urls.py - CRITICAL ORDER
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    
    # ✅ Agent URLs MUST come before core URLs
    path('agents/weather-reporter/', include('weather_reporter.urls')),
    path('agents/five-whys-analyzer/', include('five_whys_analyzer.urls')),
    
    # ❌ Core URLs with catch-all pattern must be LAST
    path('', include('core.urls')),  # This catches everything - put LAST
]
```

**URL Testing Commands:**
```bash
# Test URL resolution
python manage.py shell -c "
from django.urls import reverse
try:
    url = reverse('core:agent_detail', args=['five-whys-analyzer'])
    print('✅ URL resolved:', url)
except Exception as e:
    print('❌ URL error:', e)
"
```

### 🛡️ Prevention Strategy
- Always use namespaced URLs in templates
- Register agent URLs before core URLs
- Test URL resolution after each agent creation

---

## 3. Database Migration Conflicts

### ❌ Common Errors
```
django.db.utils.ProgrammingError: relation "five_whys_analyzer_requests" already exists
django.db.migrations.exceptions.InconsistentMigrationHistory
```

### 🔍 Root Cause Analysis
- Django migration state out of sync with actual database
- Manually created tables conflicting with migrations
- Migration dependencies missing or circular

### ✅ 5 Whys Learned Solution

**Manual Migration Sync Fix:**
```bash
# 1. Check current migration state
python manage.py showmigrations five_whys_analyzer

# 2. Create empty migration to sync state
python manage.py makemigrations five_whys_analyzer --empty --name fix_migration_sync

# 3. Edit the migration file to match current state
# migrations/000X_fix_migration_sync.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('five_whys_analyzer', '0001_initial'),
    ]
    operations = [
        # Empty operations - just sync Django state
    ]

# 4. Apply migration
python manage.py migrate five_whys_analyzer
```

**Conflict Resolution Pattern:**
```bash
# If migration conflicts persist
python manage.py migrate five_whys_analyzer --fake-initial
python manage.py migrate five_whys_analyzer
```

### 🛡️ Prevention Strategy
- Always run `makemigrations` immediately after model changes
- Test migrations on clean database before production
- Keep migration files in version control

---

## 4. Wallet Integration Problems

### ❌ Common Errors
```
AttributeError: 'User' object has no attribute 'deduct_balance'
decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
Wallet balance incorrectly deducted for failed requests
```

### 🔍 Root Cause Analysis
- Deducting balance before processing completion
- Incorrect decimal handling for currency
- Missing wallet methods in User model

### ✅ 5 Whys Learned Solution

**Delayed Deduction Pattern (Critical):**
```python
# ❌ Wrong - deduct before processing
def process_view(request):
    # Bad: deduct immediately
    request.user.deduct_balance(agent.price, description, agent_slug)
    result = process_request()  # What if this fails?
    return result

# ✅ Correct - 5 Whys pattern (deduct after success)
def process_report_response(self, response_data, request_obj):
    try:
        # Process first
        final_report = response_data.get('output', '')
        success = bool(final_report) and response_data.get('success', True)
        
        if success:
            # Save successful response
            response_obj.final_report = final_report
            response_obj.save()
            
            # ONLY deduct after confirmed success
            request_obj.user.deduct_balance(
                request_obj.cost,
                f"5 Whys Analysis Agent - Final Report",
                'five-whys-analyzer'
            )
            request_obj.status = 'completed'
        else:
            request_obj.status = 'failed'
            # No wallet deduction for failures
            
        request_obj.save()
        return response_obj
        
    except Exception as e:
        request_obj.status = 'failed'
        request_obj.save()
        # No wallet deduction for exceptions
        raise Exception(f"Failed to process: {e}")
```

**Decimal Handling:**
```python
# ✅ Correct decimal usage
from decimal import Decimal

# Always use Decimal for currency
agent.price = Decimal('8.00')
request_obj.cost = Decimal('8.00')

# Check balance properly
if request.user.wallet_balance >= agent.price:
    # Proceed
```

### 🛡️ Prevention Strategy
- Never deduct balance before processing completion
- Always use Decimal for currency calculations
- Implement balance checks before processing
- Test wallet integration with both success and failure scenarios

---

## 5. Session Management Issues

### ❌ Common Errors
```
KeyError: 'session_id'
Multiple chat sessions created for same user
Session state lost between requests
```

### 🔍 Root Cause Analysis
- Missing session ID handling
- No persistent session storage
- Poor session lifecycle management

### ✅ 5 Whys Learned Solution

**Session-Based Model Pattern:**
```python
# 5 Whys session management pattern
class AgentRequest(BaseAgentRequest):
    # Session management
    session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
    
    # Session state tracking
    chat_messages = models.JSONField(default=list)
    chat_active = models.BooleanField(default=True)
    report_generated = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'chat_active']),
        ]
```

**Session Retrieval Pattern:**
```python
# Safe session handling
def handle_chat_message(self, **kwargs):
    user = kwargs.get('user')
    session_id = kwargs.get('session_id', str(uuid.uuid4()))
    
    # Get or create session
    request_obj, created = AgentRequest.objects.get_or_create(
        user=user,
        session_id=session_id,
        chat_active=True,
        defaults={
            'agent': agent,
            'cost': 0,  # No cost for chat
            'status': 'pending'
        }
    )
    
    # Add message to history
    chat_messages = request_obj.chat_messages
    chat_messages.append({
        'role': 'user',
        'message': user_message,
        'timestamp': timezone.now().isoformat()
    })
    request_obj.chat_messages = chat_messages
    request_obj.save()
```

### 🛡️ Prevention Strategy
- Always use UUID for session IDs
- Index session_id field for performance
- Implement session cleanup for old sessions
- Test session persistence across requests

---

## 6. Status Tracking Problems

### ❌ Common Errors
```
Requests stuck in 'processing' status
Status not updated after completion
Inconsistent status across request lifecycle
```

### 🔍 Root Cause Analysis
- Missing status updates in error paths
- No status transitions defined
- Exception handling bypassing status updates

### ✅ 5 Whys Learned Solution

**Status Lifecycle Pattern:**
```python
# 5 Whys status tracking pattern
def process_response(self, response_data, request_obj):
    try:
        # Always update status to processing
        request_obj.status = 'processing'
        request_obj.save()
        
        # Process the request
        success = self.extract_and_validate_response(response_data)
        
        # Update status based on result
        if success:
            request_obj.status = 'completed'
            # Handle successful response
        else:
            request_obj.status = 'failed'
            # Handle failed response
            
    except Exception as e:
        # Always handle errors with status update
        request_obj.status = 'failed'
        request_obj.save()
        raise
    finally:
        # Always set processed timestamp
        request_obj.processed_at = timezone.now()
        request_obj.save()
```

**Status Validation:**
```python
# Status transition validation
VALID_STATUS_TRANSITIONS = {
    'pending': ['processing', 'failed'],
    'processing': ['completed', 'failed'],
    'completed': [],  # Terminal state
    'failed': [],     # Terminal state
}

def update_status(self, request_obj, new_status):
    current_status = request_obj.status
    if new_status not in VALID_STATUS_TRANSITIONS.get(current_status, []):
        raise ValueError(f"Invalid status transition: {current_status} -> {new_status}")
    request_obj.status = new_status
    request_obj.save()
```

### 🛡️ Prevention Strategy
- Define clear status lifecycle
- Always update status in exception handlers
- Use try-finally blocks for cleanup
- Monitor requests stuck in processing status

---

## 7. Error Handling Failures

### ❌ Common Errors
```
Unhandled exceptions breaking request flow
Users see raw Django error pages
No error logging for debugging
```

### 🔍 Root Cause Analysis
- Missing try-catch blocks
- No graceful error recovery
- Poor error messaging to users

### ✅ 5 Whys Learned Solution

**Comprehensive Error Handling Pattern:**
```python
# 5 Whys error handling pattern
def process_request(self, **kwargs):
    request_obj = None
    try:
        # Create request object
        request_obj = self.create_request_object(**kwargs)
        
        # Process the request
        response_data = self.make_api_call(**kwargs)
        
        # Handle response
        return self.process_response(response_data, request_obj)
        
    except ValidationError as e:
        # User input error - don't log as system error
        self.handle_user_error(request_obj, f"Invalid input: {e}")
        raise Exception(f"Please check your input: {e}")
        
    except requests.RequestException as e:
        # External API error - log and retry
        self.log_api_error(e, request_obj)
        self.handle_api_error(request_obj, "External service temporarily unavailable")
        raise Exception("Service temporarily unavailable. Please try again later.")
        
    except Exception as e:
        # Unknown error - log everything for debugging
        self.log_system_error(e, request_obj, **kwargs)
        self.handle_system_error(request_obj, "An unexpected error occurred")
        raise Exception("An unexpected error occurred. Please contact support.")

def handle_user_error(self, request_obj, message):
    if request_obj:
        request_obj.status = 'failed'
        request_obj.save()
    # Don't log user errors as system issues

def handle_api_error(self, request_obj, message):
    if request_obj:
        request_obj.status = 'failed'
        request_obj.save()
    # Log API errors for monitoring
    print(f"API Error: {message}")

def handle_system_error(self, request_obj, message):
    if request_obj:
        request_obj.status = 'failed'
        request_obj.save()
    # Log system errors with full context
    print(f"SYSTEM ERROR: {message}")

def log_system_error(self, error, request_obj, **kwargs):
    """Log system errors with full context for debugging"""
    error_context = {
        'error': str(error),
        'request_id': str(request_obj.id) if request_obj else 'None',
        'user_id': kwargs.get('user', {}).get('id', 'None'),
        'agent_slug': self.agent_slug,
        'kwargs': kwargs
    }
    print(f"SYSTEM ERROR CONTEXT: {error_context}")
```

**User-Friendly Error Messages:**
```python
# Map internal errors to user-friendly messages
ERROR_MESSAGES = {
    'insufficient_balance': "Insufficient wallet balance. Please top up your wallet.",
    'file_too_large': "File size exceeds limit. Please upload a smaller file.",
    'invalid_format': "Unsupported file format. Please upload a valid file.",
    'api_timeout': "Request timed out. Please try again.",
    'service_unavailable': "Service temporarily unavailable. Please try again later.",
    'unknown_error': "An unexpected error occurred. Please contact support."
}

def get_user_friendly_error(self, error_code):
    return ERROR_MESSAGES.get(error_code, ERROR_MESSAGES['unknown_error'])
```

### 🛡️ Prevention Strategy
- Wrap all external calls in try-catch blocks
- Provide user-friendly error messages
- Log errors with sufficient context for debugging
- Test error scenarios during development

---

## 8. Environment Variable Issues

### ❌ Common Errors
```
KeyError: 'N8N_WEBHOOK_5_WHYS'
API authentication failures
Webhook URLs not found
```

### 🔍 Root Cause Analysis
- Environment variables not loaded
- Variable name mismatches
- Missing .env file in production

### ✅ 5 Whys Learned Solution

**Environment Variable Pattern:**
```python
# Safe environment variable loading
import os
from django.conf import settings

class AgentProcessor:
    def __init__(self):
        # Safe environment variable access
        self.webhook_url = self.get_env_var('N8N_WEBHOOK_5_WHYS')
        self.api_key = self.get_env_var('EXTERNAL_API_KEY')
    
    def get_env_var(self, var_name, default=None):
        """Safely get environment variable with validation"""
        value = os.getenv(var_name, default)
        if not value and default is None:
            raise Exception(f"Required environment variable '{var_name}' not found")
        return value
    
    def validate_configuration(self):
        """Validate all required environment variables"""
        required_vars = [
            'N8N_WEBHOOK_5_WHYS',
            'DATABASE_URL',
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise Exception(f"Missing required environment variables: {missing_vars}")
```

**Environment Variable Validation Command:**
```bash
# Create validation script
python manage.py shell -c "
import os
required_vars = ['N8N_WEBHOOK_5_WHYS', 'OPENWEATHER_API_KEY', 'DATABASE_URL']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print('❌ Missing variables:', missing)
else:
    print('✅ All required variables present')
"
```

### 🛡️ Prevention Strategy
- Create environment variable validation script
- Use safe access patterns with defaults
- Document all required variables
- Test with missing variables to ensure graceful failure

---

## 9. N8N Webhook Problems

### ❌ Common Errors
```
Connection refused to N8N webhook
Webhook timeout errors
Invalid webhook response format
```

### 🔍 Root Cause Analysis
- N8N workflow not active
- Network connectivity issues
- Response format mismatches

### ✅ 5 Whys Learned Solution

**Webhook Validation Pattern:**
```python
# 5 Whys webhook handling pattern
class WebhookProcessor(StandardWebhookProcessor):
    def make_request(self, payload):
        """Make webhook request with comprehensive error handling"""
        try:
            # Validate webhook URL
            if not self.webhook_url:
                raise Exception("Webhook URL not configured")
            
            # Test connectivity first
            self.test_webhook_connectivity()
            
            # Make request with timeout
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30,  # 30 second timeout
                headers={'Content-Type': 'application/json'}
            )
            
            # Validate response
            if response.status_code != 200:
                raise Exception(f"Webhook returned status {response.status_code}: {response.text}")
            
            # Validate response format
            try:
                response_data = response.json()
            except ValueError:
                raise Exception("Webhook returned invalid JSON")
            
            return response_data
            
        except requests.ConnectionError:
            raise Exception("Cannot connect to N8N webhook. Check N8N service status.")
        except requests.Timeout:
            raise Exception("Webhook request timed out. Try again later.")
        except Exception as e:
            raise Exception(f"Webhook error: {e}")
    
    def test_webhook_connectivity(self):
        """Test webhook connectivity before making actual request"""
        try:
            test_response = requests.get(
                self.webhook_url.replace('/webhook/', '/ping/'),
                timeout=5
            )
            return True
        except:
            # Webhook connectivity test failed - continue anyway
            return False
```

**Webhook Response Validation:**
```python
def validate_webhook_response(self, response_data):
    """Validate webhook response format"""
    required_fields = ['output', 'success']
    
    if not isinstance(response_data, dict):
        raise Exception("Webhook response must be JSON object")
    
    missing_fields = [field for field in required_fields if field not in response_data]
    if missing_fields:
        raise Exception(f"Webhook response missing fields: {missing_fields}")
    
    return True
```

### 🛡️ Prevention Strategy
- Always test webhook connectivity
- Implement proper timeout handling
- Validate webhook response format
- Have fallback mechanisms for webhook failures

---

## 10. Performance and Index Issues

### ❌ Common Errors
```
Slow database queries
Missing indexes on frequently queried fields
Session lookup timeouts
```

### 🔍 Root Cause Analysis
- Missing database indexes
- Inefficient query patterns
- No query optimization

### ✅ 5 Whys Learned Solution

**Database Index Pattern:**
```python
# 5 Whys performance optimization
class AgentRequest(BaseAgentRequest):
    session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
    
    class Meta:
        indexes = [
            # Session-based queries
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'chat_active']),
            
            # Status and time-based queries
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'status']),
            
            # Agent-specific queries
            models.Index(fields=['agent', 'created_at']),
        ]
```

**Query Optimization Pattern:**
```python
# Efficient query patterns
def get_user_active_session(self, user, agent_slug):
    """Optimized session lookup"""
    return AgentRequest.objects.select_related('agent', 'user').filter(
        user=user,
        agent__slug=agent_slug,
        chat_active=True
    ).first()

def get_recent_requests(self, user, limit=10):
    """Optimized recent requests lookup"""
    return AgentRequest.objects.select_related('agent').filter(
        user=user
    ).order_by('-created_at')[:limit]
```

### 🛡️ Prevention Strategy
- Add indexes for all frequently queried fields
- Use select_related for foreign key queries
- Monitor slow queries in production
- Test with realistic data volumes

---

## 🛡️ Overall Prevention Strategy

### Pre-Development Checklist
- [ ] Study 5 Whys Analyzer patterns before starting
- [ ] Plan session management if needed
- [ ] Design delayed wallet deduction flow
- [ ] Plan comprehensive error handling

### During Development Checklist
- [ ] Use proper template directory structure
- [ ] Always use namespaced URLs
- [ ] Implement delayed wallet deduction
- [ ] Add comprehensive error handling
- [ ] Create proper database indexes

### Post-Development Checklist
- [ ] Test all error scenarios
- [ ] Validate template loading
- [ ] Test URL routing
- [ ] Verify wallet integration
- [ ] Test session management
- [ ] Validate environment variables

### Production Deployment Checklist
- [ ] Run migration validation
- [ ] Test webhook connectivity
- [ ] Verify environment variables
- [ ] Monitor error rates
- [ ] Check performance metrics

---

## 🎯 Key Takeaways from 5 Whys Debugging

1. **Template Organization is Critical**: Always use proper directory structure
2. **URL Namespaces Prevent Errors**: Always use namespaced URLs
3. **Delayed Wallet Deduction**: Never deduct before processing success
4. **Session Management**: Use UUID-based sessions for complex agents
5. **Status Tracking**: Implement proper lifecycle management
6. **Error Handling**: Wrap everything in try-catch blocks
7. **Environment Variables**: Validate all required variables
8. **Performance**: Add indexes for frequently queried fields

**Following these patterns from the 5 Whys success ensures error-free agent creation.**