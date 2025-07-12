# Agent Setup Checklist - Error-Free Creation Guide
## Steps to Complete After Running `create_agent` Command

This checklist covers the **6 essential steps** needed after running the automated `create_agent` command to make your agent fully functional. **Updated with debugging insights from the successful 5 Whys Agent implementation.**

**✅ The automated system now generates all code files including models, views, processors, and admin interface!**

---

## 🚀 **Success Patterns from 5 Whys Agent**

The 5 Whys Analyzer represents the most robust agent implementation with these key features:
- **Dual-mode processing**: Free chat interactions + paid report generation
- **Session-based architecture**: UUID tracking with persistent chat history
- **Delayed wallet deduction**: Only charge after successful processing
- **Comprehensive error handling**: Graceful failure recovery
- **Smart status tracking**: Proper request lifecycle management

**Apply these patterns to achieve error-free agent creation.**

---

## Example Command
```bash
python manage.py create_agent "PDF Analyzer" "pdf-analyzer" api \
  --category utilities --price 5.0 \
  --api-base-url "https://api.docparser.com/v1/process" \
  --api-key-env "DOCPARSER_API_KEY" --auth-method bearer
```

After running this command, follow these steps:

---

## ✅ **Step 1: Add to Django Settings**

**File:** `netcop_hub/settings.py`

**Add your new agent to INSTALLED_APPS:**
```python
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
    'agent_pdf_analyzer',  # ← ADD THIS LINE
]
```

---

## ✅ **Step 2: Register URL Routing**

**File:** `netcop_hub/urls.py`

**Add URL pattern for your agent:**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('agents/weather-reporter/', include('weather_reporter.urls')),
    path('agents/pdf-analyzer/', include('agent_pdf_analyzer.urls')),  # ← ADD THIS LINE
    path('', include('core.urls')),
]
```

**⚠️ Important:** Add agent URLs **before** the core URLs (the line with `path('', include('core.urls'))`).

---

## ✅ **Step 3: Run Database Migrations**

**Terminal Commands:**
```bash
# Create migrations for your new agent
python manage.py makemigrations agent_pdf_analyzer

# Apply migrations to database
python manage.py migrate
```

**Expected Output:**
```
Migrations for 'agent_pdf_analyzer':
  agent_pdf_analyzer/migrations/0001_initial.py
    - Create model PdfAnalyzerRequest
    - Create model PdfAnalyzerResponse

Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying agent_pdf_analyzer.0001_initial... OK
```

---

## ✅ **Step 4: Create Marketplace Entry**

**Method A: Django Shell (Recommended)**
```bash
python manage.py shell
```

```python
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
    review_count=0,
    is_active=True
)

# Verify it was created
print("Agent created:", BaseAgent.objects.filter(slug='pdf-analyzer').exists())
```

**Method B: Admin Interface**
1. Go to `http://localhost:8000/admin/`
2. Login with superuser account
3. Click "Base agents" under "AGENT_BASE"
4. Click "Add Base Agent"
5. Fill in the form with agent details
6. Save

---

## ✅ **Step 5: Add Environment Variables**

**File:** `.env`

**Add API credentials for your agent:**
```bash
# Existing variables...
OPENWEATHER_API_KEY=15befe6bac7b1cd0268900fb97d31482

# Add your new agent's API key
DOCPARSER_API_KEY=your_actual_api_key_here
```

**For webhook agents, add webhook URLs:**
```bash
# For webhook-based agents
N8N_WEBHOOK_PDF_ANALYZER=https://your-n8n-instance.com/webhook/pdf-analyzer
```

---

## ✅ **Step 6: Create Agent Template**

**The automated system creates the code structure, but you need to create the template:**

```bash
# Create the template directory and file:
mkdir -p [agent_name]/templates/
```

**Copy and customize from the weather reporter template:**
```bash
# Copy the weather reporter template as a starting point:
cp weather_reporter/templates/detail.html [agent_name]/templates/detail.html

# Then customize the template for your specific agent
```

**Template location should be:**
```bash
# Your agent templates should be in:
agent_[name]/templates/agent_[name]/detail.html

# Example for PDF Analyzer:
agent_pdf_analyzer/templates/agent_pdf_analyzer/detail.html

# Example for Data Analyzer:
data_analyzer/templates/data_analyzer/detail.html
```

---

## 🧪 **Step 7: Test Your Agent**

### **7.1 Check Django Configuration**
```bash
python manage.py check
```
**Expected:** `System check identified no issues (0 silenced).`

### **7.2 Test Template Loading**
```bash
python manage.py shell -c "
from django.template.loader import get_template
try:
    template = get_template('detail.html')
    print('✅ Template found successfully')
except Exception as e:
    print('❌ Template error:', e)
"
```
**Expected:** `✅ Template found successfully`

### **7.3 Test URL Routing**
```bash
python manage.py shell -c "from django.urls import reverse; print('Agent URL:', reverse('core:agent_detail', args=['pdf-analyzer']))"
```
**Expected:** `Agent URL: /agents/pdf-analyzer/`

### **7.4 Test in Browser**
1. **Start server:** `python manage.py runserver`
2. **Visit marketplace:** `http://localhost:8000/marketplace/`
3. **Verify agent appears** in the list
4. **Click "Use Agent"** button
5. **Verify agent page loads** correctly (should redirect to login if not authenticated)
6. **Test authentication flow** (login → redirect back to agent page)

### **7.5 Test Complete Flow**
1. **Login** with test user
2. **Add wallet balance** (if needed)
3. **Submit agent form** with test data
4. **Verify request processes** successfully
5. **Check wallet deduction** occurred
6. **Verify results display** correctly

---

## 🐛 **Common Issues & Quick Fixes** *(Learned from 5 Whys Debugging)*

### **Issue 1: "No module named 'agent_pdf_analyzer'"**
**Root Cause:** App not added to Django settings
**Fix:** Make sure you added the app to `INSTALLED_APPS` in settings.py
**Prevention:** Use the automated validation script (coming soon)

### **Issue 2: "TemplateDoesNotExist: detail.html"**
**Root Cause:** Template in wrong location or server cache
**Fix:** Ensure template is in correct location within the agent app:
```bash
# Template should be at:
agent_[name]/templates/agent_[name]/detail.html

# NOT just:
agent_[name]/templates/detail.html

# CRITICAL: Restart Django server after moving templates
```
**5 Whys Learning:** Template organization is crucial for reliability

### **Issue 3: "NoReverseMatch: Reverse for 'wallet' not found"**
**Root Cause:** Missing URL namespaces in templates
**Fix:** Check template URLs use proper namespaces:
```html
<!-- Wrong -->
{% url 'wallet' %}

<!-- Correct -->
{% url 'core:wallet' %}
```
**5 Whys Learning:** Always use namespaced URLs for reliability

### **Issue 4: "Agent not found" in marketplace**
**Root Cause:** BaseAgent entry missing or wrong slug
**Fix:** Verify BaseAgent was created with correct slug:
```bash
python manage.py shell -c "from agent_base.models import BaseAgent; print([a.slug for a in BaseAgent.objects.all()])"
```

### **Issue 5: Agent page shows 404**
**Root Cause:** URL registration order is wrong
**Fix:** Check URL registration order in `netcop_hub/urls.py` - agent URLs must come before core URLs.
**5 Whys Learning:** URL order matters for Django routing

### **Issue 6: API key errors**
**Root Cause:** Environment variable name mismatch
**Fix:** Verify environment variable name matches processor:
```python
# In processor.py
api_key_env = 'DOCPARSER_API_KEY'  # Must match .env file
```

### **Issue 7: Wallet deduction errors (5 Whys Pattern)**
**Root Cause:** Deducting balance before processing success
**Fix:** Follow the 5 Whys pattern - only deduct after successful processing:
```python
# ❌ Wrong - deduct before processing
user.deduct_balance(cost, description, agent_slug)
response = process_request()

# ✅ Correct - deduct after success (5 Whys pattern)
response = process_request()
if response.success:
    user.deduct_balance(cost, description, agent_slug)
```

### **Issue 8: Migration conflicts**
**Root Cause:** Django migrations out of sync with database
**Fix:** Create empty migration to sync state:
```bash
# Create manual sync migration
python manage.py makemigrations [agent_name] --empty
# Edit migration to match your needs
python manage.py migrate
```
**5 Whys Learning:** Migration conflicts are common - be prepared to sync manually

### **Issue 9: Session management errors (Advanced Agents)**
**Root Cause:** No persistent session tracking
**Fix:** Implement session-based architecture like 5 Whys:
```python
# Add to your models
session_id = models.CharField(max_length=100, default=uuid.uuid4, db_index=True)
chat_messages = models.JSONField(default=list)
```

### **Issue 10: Status tracking problems**
**Root Cause:** Inconsistent request status management
**Fix:** Use proper status lifecycle like 5 Whys:
```python
# Status flow: pending → processing → completed/failed
request_obj.status = 'processing'
request_obj.save()
# ... do processing ...
request_obj.status = 'completed' if success else 'failed'
request_obj.save()
```

---

## 📝 **Quick Checklist Summary** *(Error-Free Process)*

After running `create_agent`, complete these **7 critical steps** (updated with 5 Whys learnings):

- [ ] **Settings:** Add agent to `INSTALLED_APPS` in `netcop_hub/settings.py`
- [ ] **URLs:** Add URL pattern to `netcop_hub/urls.py` **BEFORE core URLs**
- [ ] **Database:** Run `makemigrations` and `migrate` (watch for conflicts)
- [ ] **Marketplace:** Verify `BaseAgent` entry created correctly
- [ ] **Environment:** Add API keys/webhook URLs to `.env`
- [ ] **Template:** Create `agent_[name]/templates/agent_[name]/detail.html`
- [ ] **Validation:** Run complete test flow including wallet integration

**5 Whys Bonus Validations:**
- [ ] **Template Loading:** Restart Django server after template creation
- [ ] **URL Namespaces:** Use `{% url 'core:wallet' %}` not `{% url 'wallet' %}`
- [ ] **Error Handling:** Implement try-catch blocks in processor
- [ ] **Wallet Logic:** Only deduct balance after successful processing
- [ ] **Status Tracking:** Use pending → processing → completed/failed flow

**Total time:** ~15-20 minutes (includes validation steps)

---

## 🚀 **You're Done!** *(Error-Free Agent)*

Your agent should now be:
✅ **Visible** in the marketplace  
✅ **Accessible** via direct URL  
✅ **Functional** with authentication  
✅ **Processing** requests successfully  
✅ **Integrated** with wallet system  
✅ **Error-resistant** with proper handling
✅ **Session-aware** (if applicable)
✅ **Status-tracked** throughout lifecycle

**Success Validation** (5 Whys Standard):
- Agent processes test request without errors
- Wallet deduction only happens after successful processing  
- Templates load correctly with namespaced URLs
- Error states are handled gracefully
- Status updates correctly throughout request lifecycle

**Next Steps:**
- Consider implementing dual-mode processing (free chat + paid reports)
- Add session management for complex interactions
- Enhance error handling with comprehensive try-catch blocks
- Monitor usage patterns and optimize based on 5 Whys learnings
- Document any new patterns for future agents

**🎯 Remember:** Follow the 5 Whys Agent patterns for maximum reliability!