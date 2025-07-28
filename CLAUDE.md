# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.

The plan should have a list of todo items that you can check off as you complete them.

Before you begin working, check in with me and I will verify the plan.

Then, begin working on the todo items, marking them as complete as you go.

Please every step of the way just give me a high level explanation of what changes you made.

Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.

Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information.

DO NOT BE LAZY. NEVER BE LAZY. IF THERE IS A BUG FIND THE ROOT CAUSE AND FIX IT. NO TEMPORARY FIXES. YOU ARE A SENIOR DEVELOPER. NEVER BE LAZY

MAKE ALL FIXES AND CODE CHANGES AS SIMPLE AS HUMANLY POSSIBLE. THEY SHOULD ONLY IMPACT NECESSARY CODE RELEVANT TO THE TASK AND NOTHING ELSE. IT SHOULD IMPACT AS LITTLE CODE AS POSSIBLE. YOUR GOAL IS TO NOT INTRODUCE ANY BUGS. IT’S ALL ABOUT SIMPLICITY

## 📚 Documentation

**Complete documentation is now organized in the `/docs/` directory:**
- **📖 Main Index:** [docs/README.md](./docs/README.md)
- **🚀 Deployment:** [docs/deployment/](./docs/deployment/) - Railway deployment, domain changes, environment setup
- **🛠️ Development:** [docs/development/](./docs/development/) - Local setup, agent creation, testing
- **⚙️ Operations:** [docs/operations/](./docs/operations/) - Database management, troubleshooting, maintenance

**Quick Links:**
- [Development Workflow](./DEVELOPMENT_WORKFLOW.md) - **🚀 START HERE** - Daily development workflow
- [Deployment Control Guide](./docs/deployment/deployment-control-guide.md) - Branch strategy and Railway control
- [Subagents Guide](./docs/development/subagents-guide.md) - AI development assistants
- [Auto-Documentation System](./docs/development/auto-documentation-system.md) - Automated documentation updates
- [Railway Deployment](./docs/deployment/railway-deployment.md) - Production deployment guide
- [Environment Variables](./docs/deployment/environment-variables.md) - Complete environment reference

## Project Overview

Quantum Tasks AI is a Django-based AI agent marketplace platform where users can purchase and interact with specialized AI agents. The system supports both webhook-based and API-based agents with integrated payment processing via Stripe.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Operations
```bash
# Check database configuration
python manage.py check_db

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Backup user data
python manage.py backup_users --action info

# Populate agent catalog
python manage.py populate_agents
```

### Development Server
```bash
# Quick start (recommended - handles migrations and environment)
./run_dev.sh

# Manual start
python manage.py runserver
```

### Testing
```bash
# Run specific agent tests
python tests/test_weather_agent.py
python tests/test_five_whys_webhook.py

# Test homepage functionality
python tests/test_homepage.py

# Test health check endpoint
curl http://localhost:8000/health/
```

### Custom Management Commands
```bash
# Create new agent
python manage.py create_agent

# Create test user
python manage.py create_user

# Reset database (development only)
python manage.py reset_database

# Test webhook functionality
python manage.py test_webhook

# Cleanup uploaded files
python manage.py cleanup_uploads
```

### Documentation Management
```bash
# Auto-update documentation (manual trigger)
./scripts/update_docs_manual.sh

# Setup git hooks for automatic documentation updates
./scripts/setup_git_hooks.sh

# Run documentation update script directly
python3 scripts/auto_update_docs.py
```

### N8N Workflow Management
```bash
# List all workflows (local and N8N instance)
python manage_n8n_workflows.py list

# Import specific agent workflow to N8N
python manage_n8n_workflows.py import data_analyzer

# Export workflow from N8N to local files
python manage_n8n_workflows.py export social_ads_generator

# Sync all workflows between local and N8N
python manage_n8n_workflows.py sync

# Backup all workflows with timestamp
python manage_n8n_workflows.py backup

# Deploy all workflows (recommended for production)
./deploy_n8n_workflows.sh
```

## Architecture Overview

### Agent System Architecture (`agent_base/`)

**Centralized Agent Management:**
- `agent_base/models.py` - `BaseAgent` model for marketplace catalog
- `agent_base/processors.py` - `BaseAgentProcessor` abstract class for agent interactions
- `agent_base/views.py` - Marketplace and agent discovery views
- `agent_base/urls.py` - Agent system URL routing
- `agent_base/generators/` - Template generation system for creating new agents
- `templates/agent_base/` - Marketplace and agent catalog templates

**Agent Types:**
1. **Webhook Agents** - Process requests via external N8N webhook APIs (require N8N workflows)
   - `data_analyzer` - File analysis and insights
   - `social_ads_generator` - Social media ad creation
   - `job_posting_generator` - Professional job postings
   - `five_whys_analyzer` - Root cause analysis
2. **API Agents** - Direct API integration for immediate responses
   - `weather_reporter` - OpenWeather API integration
   - `email_writer` - Custom email composition logic

**Individual Agent Apps:**
Each agent is a separate Django app following this structure:
- `models.py` - Agent-specific request/response models
- `processor.py` - Inherits from `BaseAgentProcessor`, implements specific logic
- `views.py` - Agent detail page and request handling
- `templates/[agent_name]/detail.html` - Agent interface
- `urls.py` - Agent-specific URL routing
- `n8n_workflows/` - N8N workflow configurations (webhook agents only)
  - `workflow.json` - Production workflow
  - `README.md` - Setup and configuration documentation

### N8N Workflow Architecture

⚠️ **IMPORTANT**: N8N runs on a SEPARATE server from your Django application. They communicate via HTTP webhooks.

**System Architecture:**
```
User Request → Django App (Railway) → HTTP POST → N8N Instance (Separate Hosting) → AI Processing → JSON Response → Django → User Display
```

**Hosting Separation:**
- **Django App**: Deployed on Railway (your main application)
- **N8N Instance**: Deployed separately (N8N Cloud, separate Railway project, or self-hosted)
- **Communication**: HTTP POST requests between the two systems

**Webhook Agent Integration:**
- Django application sends POST requests to N8N webhook URLs (external server)
- N8N workflows process requests using AI services (OpenAI GPT-4) 
- N8N workflows return structured JSON responses back to Django
- Environment variables configure webhook URLs pointing to your N8N instance

**Workflow Management:**
- `manage_n8n_workflows.py` - Import, export, sync, and backup workflows
- `deploy_n8n_workflows.sh` - Automated deployment script
- Individual agent README files document setup and configuration
- Version control tracks workflow changes alongside agent code

**Environment Configuration:**
- `N8N_WEBHOOK_DATA_ANALYZER` - Data analysis workflow URL
- `N8N_WEBHOOK_SOCIAL_ADS` - Social ads generation workflow URL
- `N8N_WEBHOOK_JOB_POSTING` - Job posting generation workflow URL
- `N8N_WEBHOOK_FIVE_WHYS` - Five whys analysis workflow URL

### Core System Architecture

**Authentication System (`authentication/`):**
- Custom User model with wallet integration
- Password reset functionality with email tokens
- Profile management

**Payment System (`wallet/`):**
- Stripe integration for payments
- User balance tracking
- Transaction history

**Core App (`core/`):**
- Homepage and platform overview
- Pricing page for non-authenticated users
- Platform-wide functionality only (no business logic)

**Agent Base App (`agent_base/`):**
- Agent marketplace and catalog views
- Agent discovery and filtering
- Cross-agent functionality and API endpoints

**Wallet App (`wallet/`):**
- Complete payment system with Stripe integration
- Wallet dashboard and transaction history
- Payment processing and webhook handling

**Workflows App (`workflows/`):**
- Unified agent processing system with hybrid architecture
- Individual agent templates with shared components and utilities
- Direct N8N webhook integration with Django fallback processing
- Configuration-driven agent definitions (no separate Django apps needed)
- Shared CSS from main static directory (`{% static 'css/agent-base.css' %}`)
- Self-contained JavaScript utilities in main static directory (`{% static 'js/workflows-core.js' %}`)
- **Architecture Decision**: Uses external CSS/JS to avoid Django static file conflicts
- Template Component Architecture with local components in `workflows/templates/workflows/components/`

### URL Structure

```
/                           # Homepage (core app)
/pricing/                   # Pricing page (core app)
/health/                    # Health check endpoint for monitoring (core app)
/contact/                   # Contact form submission (core app)
/marketplace/               # Agent marketplace (agent_base app)
/agents/<slug>/             # Agent detail redirect (agent_base app)
/auth/                      # Authentication (login, register, profile)
/wallet/                    # Wallet management and top-up (wallet app)
/wallet/stripe/             # Stripe webhooks and debug (wallet app)
/agents/[agent-slug]/       # Individual agent pages (individual apps)
/workflows/<agent-slug>/   # Unified workflows app agent processing (NEW)
/admin/                     # Django admin
/api/agents/               # Agent API endpoint (agent_base app)
```

### Template Architecture

**Template Hierarchy:**
- `templates/base.html` - Main layout with navigation and auth
- `templates/components/` - Reusable components (agent_header, wallet_card, etc.)
- `templates/core/` - Platform pages (homepage, pricing)
- `templates/agent_base/` - Agent marketplace and catalog
- `templates/wallet/` - Payment and wallet management
- `templates/authentication/` - User authentication pages
- Agent-specific templates in individual app directories

**CSS Architecture:**
- `base.css` - Global styles and CSS variables
- `agent-base.css` - Agent page styling
- `header-component.css` - Header styling (replaces deprecated header.css)
- Component-specific CSS files

### Database Design

**Key Models:**
- `BaseAgent` - Agent catalog and marketplace data
- `User` - Extended Django user with wallet functionality
- Agent-specific request models (e.g., `WeatherReportAgentRequest`)

### Environment Configuration

Required environment variables (see `.env.example`):
- `SECRET_KEY` - Django secret key
- `DEBUG` - Development mode flag
- Stripe keys for payment processing
- Email configuration for password reset

### Simplified Agent Creation Process

**New Streamlined Workflow (90% less complexity!):**

The workflows app now uses a dramatically simplified agent creation process. No more complex configurations or dynamic field systems - just simple metadata and individual templates.

### 4-Step Agent Creation Process

#### **Step 1: Add Agent Configuration (5 lines)**
```python
# In workflows/config/agents.py - add to AGENT_CONFIGS
'your-agent-slug': {
    'name': 'Your Agent Name',
    'description': 'What this agent does',
    'category': 'utilities',  # or 'marketing', 'analytics', 'content'
    'price': 3.0,
    'icon': '🤖',
    'webhook_url': 'http://localhost:5678/webhook/your-webhook-id',
},
```

#### **Step 2: Create Individual Template**
```bash
# Copy the starter template
cp workflows/templates/workflows/agent-template-starter.html workflows/templates/workflows/your-agent.html

# Customize the template by replacing:
# - Form fields section with your agent-specific inputs
# - Processing messages and result titles
# - How it works steps (optional)
```

#### **Step 3: Add Template Mapping**
```python
# In workflows/views.py - add to template_mapping dict
template_mapping = {
    'social-ads-generator': 'workflows/social-ads-generator.html',
    # ... existing mappings ...
    'your-agent-slug': 'workflows/your-agent.html',  # <-- Add this line
}
```

#### **Step 4: Optional - Add to Marketplace**
```python
# If you want the agent in the marketplace
from agent_base.models import BaseAgent

BaseAgent.objects.create(
    name="Your Agent Name",
    slug="your-agent-slug", 
    description="What this agent does",
    price=3.0,
    is_active=True
)
```

### Configuration Comparison

**Before (Complex):**
```python
# 50+ lines of complex configuration
'agent-slug': {
    'name': 'Agent Name',
    'form_sections': [
        {
            'title': '📝 Section Title',
            'fields': [
                {
                    'name': 'field_name',
                    'type': 'textarea',
                    'label': 'Field Label',
                    'placeholder': 'Placeholder text...',
                    'required': True,
                    'rows': 4,
                    'validation': {...},
                    # ... 20+ more lines per field
                }
            ]
        }
    ],
    'message_template': 'Complex template string...',
    'result_format': 'Format description...'
}
```

**After (Simplified):**
```python
# 5 lines of essential metadata
'agent-slug': {
    'name': 'Agent Name',
    'description': 'What this agent does',
    'price': 3.0,
    'icon': '🤖',
    'webhook_url': 'http://localhost:5678/webhook/...',
},
```

### Template Structure

All templates use shared components for consistency:
```django
{% extends 'base.html' %}
{% load static %}

{% block content %}
<!-- Shared components (automatic functionality) -->
{% include "workflows/components/agent_header.html" %}
{% include "workflows/components/quick_agents_panel.html" %}

<!-- Your agent-specific form (customize this part only) -->
<div class="agent-widget widget-large">
    <form id="agentForm" method="POST">
        <!-- Your unique form fields go here -->
    </form>
</div>

<!-- Shared components (automatic functionality) -->
{% include "workflows/components/processing_status.html" %}
{% include "workflows/components/results_container.html" %}
{% endblock %}
```

### Enhanced JavaScript Utilities

All agents automatically get access to enhanced WorkflowsCore utilities:
- `WorkflowsCore.showToast(message, type)` - Toast notifications
- `WorkflowsCore.showProcessing(title)` - Show processing status
- `WorkflowsCore.showResults(content, title)` - Display results
- `WorkflowsCore.copyToClipboard(text, message)` - Copy functionality
- `WorkflowsCore.downloadAsFile(content, filename)` - File downloads
- `WorkflowsCore.handleFileChange(input)` - File upload handling
- Plus many more utilities for common agent operations

### Development Workflow

1. **Start with Template Starter** - Copy `agent-template-starter.html`
2. **Customize Form Section** - Replace example fields with your agent's inputs
3. **Add Configuration** - 5-line config entry
4. **Map Template** - One line in views.py
5. **Test & Deploy** - Agent ready to use!

**Benefits:**
- ✅ **90% less code** - 5 lines vs 50+ lines of configuration
- ✅ **Shared components** - Consistent UI, automatic updates
- ✅ **Enhanced utilities** - Advanced JavaScript functions included
- ✅ **Dynamic data** - Agent lists update automatically
- ✅ **Simple maintenance** - Easy to understand and modify

### Template Component Architecture

**CRITICAL: Always Use Component-Based Architecture**

All agent templates MUST use the established component system. Never recreate shared functionality inline.

**Required Components for Every Agent:**
```django
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/agent-base.css' %}">
{% endblock %}

{% block content %}
<!-- Agent Header Component -->
{% include "components/agent_header.html" with agent_title="Your Agent Name" agent_subtitle="Description" %}

<!-- Quick Agents Panel Component -->
{% include "components/quick_agents_panel.html" %}

<!-- Agent-Specific Form Content ONLY -->
<div class="agent-grid">
    <div class="agent-widget widget-large">
        <!-- ONLY write agent-specific form/content here -->
    </div>
    <!-- How It Works widget using existing patterns -->
</div>

<!-- Processing Status Component -->
{% include "components/processing_status.html" with status_title="Processing..." status_text="Please wait..." %}

<!-- Results Component -->
{% include "components/results_container.html" with results_title="Results" %}
{% endblock %}
```

**Component Checklist:**
- ✅ `{% include "components/agent_header.html" %}` - Page header and wallet card
- ✅ `{% include "components/quick_agents_panel.html" %}` - Agent navigation
- ✅ `{% include "components/processing_status.html" %}` - Loading states
- ✅ `{% include "components/results_container.html" %}` - Result display
- ✅ `<link rel="stylesheet" href="{% static 'css/agent-base.css' %}">` - Shared CSS

**Template Best Practices:**
1. **Check Existing Agents First** - Look at `data_analyzer` or `social_ads_generator` templates for patterns
2. **Component-First Development** - Use includes for all shared functionality
3. **Agent-Specific Content Only** - Write only unique form logic and processing
4. **Line Count Target** - Keep templates under 500 lines by leveraging components
5. **Consistency Verification** - Ensure all agents follow the same component pattern

**Anti-Pattern Warning:**
❌ **NEVER recreate these inline:**
- Agent headers with wallet cards
- Quick agents navigation panels  
- Processing status displays
- Results containers with action buttons
- CSS frameworks or JavaScript utilities

**Why This Matters:**
- Maintains consistent UI/UX across all agents
- Ensures easier maintenance and updates
- Reduces code duplication and template bloat
- Provides shared functionality improvements automatically

### How to Request Component Architecture

When asking Claude to work on agent templates, use these specific phrases to ensure component architecture is applied:

**For New Agents:**
- "Apply Template Component Architecture from CLAUDE.md to create [agent name]"
- "Create [agent name] using the component architecture pattern"
- "Follow Template Component Architecture guidelines for [agent name]"

**For Existing Agents:**
- "Convert [agent name] to Template Component Architecture from CLAUDE.md"
- "Optimize [agent name] template using component architecture"
- "Apply component pattern to [agent name] like data_analyzer and social_ads_generator"

**Key Trigger Phrase:** "Template Component Architecture"

This ensures Claude will:
✅ Use component includes instead of inline HTML
✅ Link to agent-base.css instead of recreating CSS
✅ Keep templates under 500 lines
✅ Follow established patterns from working agents
✅ Maintain consistency across the platform

### Deployment & Production

**Railway.app (Recommended)**
- **Configuration**: `railway.json` with optimized Gunicorn settings
- **Deployment Guide**: See `RAILWAY_DEPLOYMENT_GUIDE.md` for step-by-step instructions
- **Environment Variables**: Use `RAILWAY_ENV_TEMPLATE.md` for production configuration
- **Health Check**: `/health/` endpoint for monitoring and load balancers
- **Verification**: Follow `POST_DEPLOYMENT_CHECKLIST.md` after deployment

**Production Features:**
- PostgreSQL database with connection pooling
- Redis caching for sessions and performance  
- SSL certificates and HTTPS enforcement
- Static files served via WhiteNoise
- Database migrations run automatically on deployment
- Rate limiting and security headers
- Custom 404/500 error pages

**Health Monitoring:**
```bash
# Check application health
curl https://your-domain.railway.app/health/

# Expected response:
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy", "response_time_ms": 2.5},
    "agents": {"status": "healthy", "active_count": 7}
  }
}
```

**Production Commands:**
```bash
# Test deployment readiness
DEBUG=False python manage.py check --deploy

# Collect static files for production
python manage.py collectstatic --noinput

# Test health check locally
python manage.py runserver
curl http://localhost:8000/health/
```

### File Upload Handling

- `media/uploads/[agent_name]/` - User uploaded files
- Cleanup command available: `python manage.py cleanup_uploads`
- Files are processed by individual agent processors

### Architecture Principles

**Single Responsibility:**
- `core` - Platform presentation and static pages only
- `agent_base` - Agent marketplace, catalog, and cross-agent functionality
- `wallet` - Complete payment system with Stripe integration
- Individual agent apps - Specific agent logic and interfaces

**URL Namespacing:**
- Use `agent_base:marketplace` for marketplace links
- Use `wallet:wallet` for wallet-related links
- Use `core:homepage` for platform homepage
- Individual agents have their own URL namespaces

**Template Organization:**
- Templates are organized by app responsibility
- Use proper URL namespacing in templates
- Marketplace functionality is in `agent_base` app, not `core`

Always run `python manage.py check_db` before making database-related changes to ensure proper configuration.

---
Last updated: Last updated: 2025-07-28 20:06:47
