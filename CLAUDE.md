# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quantum Tasks AI is a Django-based AI agent marketplace platform. Users can access AI agent services through a web interface, with execution handled via two distinct systems: N8N webhook integrations and direct form access integrations.

**Key Architecture:**
- **Django Framework**: Main web application using Django 5.2.4
- **Agent System**: Database-driven agents app with dual integration systems:
  - **Webhook Agents**: N8N integrations for complex processing
  - **Direct Access Agents**: Form-based integrations (JotForm, etc.)
- **Authentication**: Custom user model with email verification
- **Payments**: Stripe integration with wallet system (supports free agents)
- **Database**: SQLite for development, PostgreSQL for production (Railway)
- **Static Files**: WhiteNoise for production static file serving

## Development Commands

### Environment Setup
```bash
# Use virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt          # Production
pip install -r requirements-dev.txt     # Development

# Start development server
./run_dev.sh                            # Recommended - includes migration checks
# OR
python manage.py runserver              # Direct Django server
```

### Database Operations
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Database shell
python manage.py dbshell

# Check database configuration
python manage.py check_db
```

### Testing
```bash
# Run Django tests
python manage.py test

# Run pytest (if configured)
pytest

# Run specific app tests
python manage.py test authentication
python manage.py test agents
python manage.py test wallet

# Custom test scripts
python tests/simple_test.py
python tests/check_agents.py
```

### Code Quality (Development Dependencies)
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8

# Type checking (if available)
mypy .
```

### Production Commands
```bash
# Collect static files
python manage.py collectstatic --noinput

# Production server (via Gunicorn)
gunicorn netcop_hub.wsgi:application
```

## Core Architecture

### Apps Structure
- **authentication/**: Custom user model, email verification, password reset
- **core/**: Homepage, error handlers, utility functions
- **agents/**: Database-driven agent system (marketplace, execution, models, REST API)
- **wallet/**: Stripe payments, wallet management, transactions

### Agent System (agents app)
**Key Files:**
- `agents/models.py`: Agent, AgentCategory, AgentExecution, ChatSession models
- `agents/views.py`: Dual integration systems and web interface views
- `agents/templates/agents/`: Dynamic agent templates and marketplace
- `agents/management/commands/`: Agent creation and management commands
- `templates/career_navigator.html`: Direct access form template

**Dual Integration Systems:**

**System 1: Webhook Agents (N8N Integration)**
1. User browses marketplace (`/agents/`)
2. Clicks "Try Now" → Agent detail page (`/agents/{slug}/`)
3. Fills dynamic form → Form submission calls `/agents/api/execute/`
4. N8N webhook processes request and returns response
5. Results displayed with file upload support

**System 2: Direct Access Agents (Form Integration)**
1. User browses marketplace (`/agents/`)
2. Clicks special "Try Now" button → Direct access (`/agents/{slug}/access/`)
3. Payment processed → Redirect to form page (`/agents/{slug}/`)
4. Form displays embedded interface (JotForm, etc.)
5. User interacts directly with external form system

### Database Models
**User Management:**
- `authentication.User`: Custom user model with email verification
- `authentication.PasswordResetToken`: Password reset tokens
- `authentication.EmailVerificationToken`: Email verification tokens

**Agents:**
- `agents.Agent`: Agent definitions with JSON form schemas and pricing
- `agents.AgentCategory`: Agent categories with icons and descriptions
- `agents.AgentExecution`: Execution history and results tracking

**Payments:**
- `wallet.Wallet`: User wallet with balance tracking
- `wallet.WalletTransaction`: Transaction history and Stripe integration

### Settings Configuration
**Environment Variables (Required for Production):**
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: SMTP credentials
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`: Stripe API keys
- `DATABASE_URL`: PostgreSQL connection string (Railway)

**Current Agents:**
The platform supports both webhook-based agents (N8N integration) and direct access agents (embedded forms):

**Webhook Agents (N8N Integration):**
1. **Social Ads Generator** (social-ads-generator) - 6.00 AED
   - Creates compelling social media advertisements
   - Form fields: description, social_platform, include_emoji, language
   - Webhook: N8N endpoint for social media ad generation

2. **Job Posting Generator** (job-posting-generator) - 10.00 AED  
   - Creates professional job postings
   - Form fields: job_title, company_name, job_description, seniority_level, contract_type, location, language
   - Webhook: N8N endpoint for job posting generation

3. **PDF Summarizer** (pdf-summarizer) - 8.00 AED
   - Analyzes and summarizes PDF documents with file upload
   - Form fields: pdf_file (file upload with drag-and-drop), summary_type
   - Webhook: N8N endpoint for PDF processing with multipart file support

4. **5 Whys Analyzer** (5-whys-analyzer) - 15.00 AED
   - Interactive chat-based root cause analysis using 5 Whys methodology
   - Chat interface with real-time N8N webhook integration
   - Session timeout: 2 hours

**Direct Access Agents (Embedded Forms):**
5. **CyberSec Career Navigator** (cybersec-career-navigator) - 0.00 AED
   - JotForm-based career guidance consultation
   - Embedded white-label interface with Quantum Tasks header
   - Session duration: 2 hours
   - Direct access URL: `/agents/career-navigator/`

6. **AI Brand Strategist** (ai-brand-strategist) - 0.00 AED
   - JotForm-based brand strategy consultation
   - Embedded white-label interface with Quantum Tasks header
   - Session duration: 2 hours
   - Direct access URL: `/agents/ai-brand-strategist/`

### URL Structure
```
/                       # Homepage (core app)
/digital-branding/      # Digital branding services page
/auth/                  # Authentication (login, register, etc.)
/agents/                # Agent marketplace (agents app)
/agents/{slug}/         # Individual agent pages (webhook agents)
/agents/career-navigator/       # Career navigator form page
/agents/career-navigator/access/ # Career navigator payment processing
/agents/ai-brand-strategist/    # AI Brand Strategist form page
/agents/ai-brand-strategist/access/ # AI Brand Strategist payment processing
/wallet/                # Wallet management
/admin/                 # Django admin
```

### Key Components
**Agent Configuration (Database-driven):**
- All agent metadata stored in database (pricing, descriptions, webhooks)
- JSON form schemas for dynamic form generation
- Easy to add new agents via management commands or admin interface

**Templates:**
- `templates/base.html`: Main layout with navigation
- `templates/components/`: Reusable UI components
- `agents/templates/agents/`: Dynamic agent forms and marketplace pages

## Adding New Agents

**⚡ RECOMMENDED APPROACH:** Use JSON configuration + `populate_agents` command for error-free, Railway-ready agent creation.

### **🏷️ Choose Existing Category First**

**IMPORTANT:** Always use existing categories before creating new ones to avoid category proliferation.

**Available Categories:**
- 🧠 **`analysis`** - Problem-solving, SWOT analysis, strategic analysis tools
- 🎓 **`career-education`** - Career guidance, educational resources, professional development
- 📄 **`document-processing`** - PDF analysis, file processing, document tools
- 💼 **`human-resources`** - Job postings, HR automation, talent management
- 📢 **`marketing`** - Social ads, branding, content marketing, advertising
- 💼 **`consulting`** - Business consultation, strategy services, expert advice

**Only create new categories when absolutely necessary and logically distinct.**

---

### **🚀 Agent Creation Workflow**

The platform has **TWO DISTINCT AGENT SYSTEMS**:

#### **System 1: Webhook Agents (N8N Integration)**
- **Use for:** Dynamic forms, server-side processing, file uploads, complex workflows
- **Examples:** Social Ads Generator, PDF Summarizer, Job Posting Generator
- **Flow:** Marketplace → Agent detail page → Dynamic form → N8N webhook → Results

#### **System 2: Direct Access Agents (External Forms)**
- **Use for:** External form services (JotForm, Google Forms), consultation interfaces
- **Examples:** SWOT Analysis Expert, CyberSec Career Navigator, AI Brand Strategist
- **Flow:** Marketplace → Payment processing → Quantum Tasks header + embedded external form

---

### **📝 Implementation Steps (All Agent Types)**

#### **Step 1: Create JSON Configuration**

Create a new file in `agents/configs/agents/your-agent-name.json`:

**Webhook Agent Example:**
```json
{
  "slug": "content-optimizer",
  "name": "Content Optimizer",
  "short_description": "AI-powered content optimization and enhancement",
  "description": "Enhance your content for better engagement with AI-powered optimization suggestions, tone analysis, and improvement recommendations.",
  "category": "marketing",
  "price": 5.0,
  "agent_type": "form",
  "system_type": "webhook",
  "form_schema": {
    "fields": [
      {
        "name": "content",
        "type": "textarea",
        "label": "Content to Optimize",
        "required": true
      },
      {
        "name": "content_type",
        "type": "select",
        "label": "Content Type",
        "required": true,
        "options": [
          {"value": "blog", "label": "Blog Post"},
          {"value": "social", "label": "Social Media"},
          {"value": "email", "label": "Email Marketing"}
        ]
      }
    ]
  },
  "webhook_url": "http://localhost:5678/webhook/content-optimizer",
  "access_url_name": "",
  "display_url_name": ""
}
```

**Direct Access Agent Example:**
```json
{
  "slug": "business-strategist",
  "name": "Business Strategist",
  "short_description": "Expert business strategy consultation",
  "description": "Get professional business strategy insights and recommendations from experienced consultants to grow your business effectively.",
  "category": "consulting",
  "price": 0.0,
  "agent_type": "form",
  "system_type": "direct_access",
  "form_schema": {
    "fields": []
  },
  "webhook_url": "https://agent.jotform.com/your-form-id",
  "access_url_name": "agents:direct_access_handler",
  "display_url_name": "agents:direct_access_display"
}
```

#### **Step 2: Run populate_agents Command**

```bash
# Development
source venv/bin/activate
python manage.py populate_agents

# Production (Railway)
python manage.py populate_agents  # Runs automatically on deployment
```

#### **Step 3: Additional Setup (Direct Access Agents Only)**

For direct access agents that need custom templates or marketplace integration:

**3a. Create Custom Template** (optional):
```html
<!-- templates/your_agent_name.html -->
{% extends 'base.html' %}
{% load static %}

{% block title %}Your Agent Name - Quantum Tasks AI{% endblock %}

{% block extra_css %}
<style>
.main-container { max-width: none; padding: 0; height: calc(100vh - 80px); }
.iframe-container { width: 100%; height: 100%; }
.iframe-container iframe { width: 100%; height: 100%; border: none; display: block; }
.footer { display: none !important; }
</style>
{% endblock %}

{% block content %}
<div class="iframe-container">
    <iframe src="{{ form_url }}" frameborder="0" scrolling="auto" title="Your Agent Name"></iframe>
</div>
{% endblock %}
```

**3b. Add Custom Views** (if needed):
Add view functions to `agents/views.py` following the pattern of existing direct access agents.

**3c. Add URL Routes** (if needed):
Add routes to `agents/urls.py` following the pattern of existing direct access agents.

**3d. Update Marketplace Template** (if needed):
Add button logic to `agents/templates/agents/marketplace.html` for custom marketplace behavior.

#### **Step 4: Setup External Services**

**For Webhook Agents:**
- Create N8N workflow at the webhook URL
- Configure webhook to accept JSON payload with `sessionId`, `message`, etc.

**For Direct Access Agents:**
- Create external form (JotForm, Google Forms, etc.)
- Ensure form URL is accessible and properly configured

---

### **✅ Benefits of This Approach**

- ✅ **Single source of truth** - JSON configs define everything
- ✅ **Railway-ready immediately** - No manual database setup needed
- ✅ **Error-free** - No category creation mistakes or typos
- ✅ **Consistent** - All agents use same reliable creation process
- ✅ **Scalable** - Easy to add 100+ agents
- ✅ **Version controlled** - Configs are tracked in git

### **🔧 Supported Form Field Types (Webhook Agents)**

- `text` - Single-line text input
- `textarea` - Multi-line text input  
- `select` - Dropdown with options array
- `file` - File upload with drag-and-drop
- `url` - URL input with validation
- `checkbox` - Boolean checkbox

### **⚠️ Common Mistakes to Avoid**

1. **Creating unnecessary categories** - Use existing ones first
2. **Missing system_type** - Include "webhook" or "direct_access" 
3. **Wrong access_url_name** - Empty for webhook agents, populated for direct access
4. **Forgetting populate_agents** - Run after creating JSON config
5. **Complex custom commands** - Use JSON + populate_agents instead

## Production Deployment

**Railway Configuration:**
- Automatic deployment from git repository
- PostgreSQL database provided by Railway
- Environment variables configured in Railway dashboard
- Static files served via WhiteNoise

**Security Features:**
- CSRF protection enabled
- Rate limiting on sensitive endpoints
- Secure headers in production
- HTTPS redirect and HSTS headers
- Session and cookie security

## Development Notes

- **Database**: Uses SQLite by default for development reliability
- **Cache**: Redis preferred, falls back to local memory cache
- **Email**: Console backend in development, SMTP in production
- **Debug Tools**: Debug toolbar and Django extensions available in development
- **Static Files**: Collected to `staticfiles/` directory for production
- **Media Files**: User uploads stored in `media/` directory

## Common Development Tasks

**Adding new environment variables:**
1. Add to `settings.py` with `config()` call
2. Add to required_env_vars list if production-required
3. Document in this file

**Database changes:**
1. Make model changes
2. Run `python manage.py makemigrations`
3. Review migration file
4. Run `python manage.py migrate`

**Testing agent webhooks locally:**
1. Use ngrok or similar to expose local server
2. Update webhook URLs in agent database records
3. Test agent execution flow
4. Check AgentExecution records and results display

## System Status

**Current Status: ✅ STABLE COMPREHENSIVE SYSTEM**
- **6 agents** confirmed working and tested (4 webhook + 2 direct access)
- **Dual integration architecture** with clear separation and documentation
- **Embedded form interfaces** with Quantum Tasks headers working correctly
- **Chat-based and form-based** agent systems operational
- **Scalable architecture** ready for 100+ agents

**Current Agents:**
- **Webhook Agents (4)**: Social Ads Generator, Job Posting Generator, PDF Summarizer, 5 Whys Analyzer
- **Direct Access Agents (2)**: CyberSec Career Navigator, AI Brand Strategist

**Latest Changes:**
- **Added AI Brand Strategist** with embedded JotForm interface and Quantum Tasks header
- **Documented complete agent creation process** with clear system distinctions
- **Established patterns** for both webhook and direct access agent development
- **Fixed architecture inconsistencies** between different agent types
- **Updated comprehensive documentation** to prevent future agent creation issues

**Architecture Clarity:**
- **Two distinct systems** clearly documented with implementation examples
- **Common mistakes** section added to prevent development issues
- **Step-by-step guides** for both agent types with complete code examples
- **Key differences table** for quick reference during development

**Future Development:**
- **New agents** should follow documented patterns in "Adding New Agents" section
- **Direct access agents** require dedicated templates, views, and URL routes
- **Webhook agents** use generic dynamic form generation system
- **No more architecture confusion** - clear documentation prevents implementation issues

---
Last updated: 2025-08-04 20:00:00
