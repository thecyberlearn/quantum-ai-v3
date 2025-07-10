# Agent Setup Checklist
## Steps to Complete After Running `create_agent` Command

This checklist covers the **5 essential steps** needed after running the automated `create_agent` command to make your agent fully functional.

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

## ✅ **Step 6: Verify Template Structure**

**Check that your agent's templates are in the correct location:**
```bash
# Your agent templates should be in:
agent_[name]/templates/detail.html

# Example for PDF Analyzer:
agent_pdf_analyzer/templates/detail.html
```

**If the template is missing or in wrong location, you'll get a `TemplateDoesNotExist` error.**

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

## 🐛 **Common Issues & Quick Fixes**

### **Issue 1: "No module named 'agent_pdf_analyzer'"**
**Fix:** Make sure you added the app to `INSTALLED_APPS` in settings.py

### **Issue 2: "TemplateDoesNotExist: detail.html"**
**Fix:** Ensure template is in correct location within the agent app:
```bash
# Template should be at:
agent_[name]/templates/detail.html

# NOT in the global templates folder
# Restart Django server after moving templates
```

### **Issue 3: "NoReverseMatch: Reverse for 'wallet' not found"**
**Fix:** Check template URLs use proper namespaces:
```html
<!-- Wrong -->
{% url 'wallet' %}

<!-- Correct -->
{% url 'core:wallet' %}
```

### **Issue 4: "Agent not found" in marketplace**
**Fix:** Verify BaseAgent was created with correct slug:
```bash
python manage.py shell -c "from agent_base.models import BaseAgent; print([a.slug for a in BaseAgent.objects.all()])"
```

### **Issue 4: Agent page shows 404**
**Fix:** Check URL registration order in `netcop_hub/urls.py` - agent URLs must come before core URLs.

### **Issue 5: API key errors**
**Fix:** Verify environment variable name matches processor:
```python
# In processor.py
api_key_env = 'DOCPARSER_API_KEY'  # Must match .env file
```

---

## 📝 **Quick Checklist Summary**

After running `create_agent`, complete these 5 steps:

- [ ] **Settings:** Add agent to `INSTALLED_APPS`
- [ ] **URLs:** Add URL pattern to `netcop_hub/urls.py`
- [ ] **Database:** Run `makemigrations` and `migrate`
- [ ] **Marketplace:** Create `BaseAgent` entry
- [ ] **Environment:** Add API keys to `.env`
- [ ] **Test:** Verify agent works end-to-end

**Total time:** ~5-10 minutes

---

## 🚀 **You're Done!**

Your agent should now be:
✅ **Visible** in the marketplace  
✅ **Accessible** via direct URL  
✅ **Functional** with authentication  
✅ **Processing** requests successfully  
✅ **Integrated** with wallet system  

**Next Steps:**
- Customize the agent's UI/templates
- Add more complex business logic
- Configure additional API integrations
- Monitor usage and performance