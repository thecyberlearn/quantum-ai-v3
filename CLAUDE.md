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

### Agent Management (File-Based System)
```bash
# Agents are managed via JSON files - no commands needed!
# Simply add/edit JSON files in agents/configs/agents/

# View agent statistics
python -c "
from agents.services import AgentFileService
stats = AgentFileService.get_agent_stats()
print('Agent Stats:', stats)
"
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
- **agents/**: File-based agent system (marketplace, execution history, REST API for executions)
- **wallet/**: Stripe payments, wallet management, transactions

### Agent System (agents app)
**Key Files:**
- `agents/services.py`: AgentFileService - file-based agent management
- `agents/configs/agents/`: JSON agent configuration files
- `agents/configs/categories/`: JSON category configuration files  
- `agents/models.py`: AgentExecution, ChatSession models (execution history)
- `agents/views.py`: Main imports for backwards compatibility
- `agents/api_views.py`: REST API endpoints (execute_agent, execution_list/detail)
- `agents/chat_views.py`: Chat session management and message handling
- `agents/web_views.py`: Web interface views (marketplace, agent detail pages)
- `agents/direct_access_views.py`: External form integration handlers
- `agents/utils.py`: Utility functions (webhook validation, message formatting)
- `agents/templates/agents/`: Dynamic agent templates and marketplace
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

**Current System:**
The platform supports **8 total agents** across **6 categories**:
- **4 Webhook Agents** (N8N integration): Social Ads Generator, Job Posting Generator, PDF Summarizer, 5 Whys Analyzer
- **4 Direct Access Agents** (External forms): CyberSec Career Navigator, AI Brand Strategist, Lean Six Sigma Expert, SWOT Analysis Expert

For detailed agent information and creation instructions, see `docs/AGENT_CREATION.md`.

### URL Structure
```
/                       # Homepage (core app)
/digital-branding/      # Digital branding services page
/auth/                  # Authentication (login, register, etc.)
/agents/                # Agent marketplace (agents app)
/agents/{slug}/         # Individual agent pages (webhook agents)
/agents/{slug}/access/  # Direct access agent payment processing
/wallet/                # Wallet management
/admin/                 # Django admin
```

### Key Components
**Agent Configuration (File-driven):**
- All agent metadata stored in JSON files (pricing, descriptions, webhooks)
- JSON form schemas for dynamic form generation
- Instant agent creation by adding JSON files (no commands needed)
- Automatic database sync for foreign key compatibility

**Templates:**
- `templates/base.html`: Main layout with navigation
- `templates/components/`: Reusable UI components
- `agents/templates/agents/`: Dynamic agent forms and marketplace pages

## Adding New Agents

For comprehensive agent creation instructions, see **`docs/AGENT_CREATION.md`**.

**Quick Summary:**
1. Create JSON config in `agents/configs/agents/your-agent-name.json`
2. Git push (or restart server locally)
3. Agent appears in marketplace automatically - no commands needed!

The platform supports 2 agent types:
- **Webhook Agents** - N8N integration with dynamic forms
- **Direct Access Agents** - External forms (JotForm, etc.) with embedded interfaces

## External Service Wrappers

**Simple template-based system for event invitations, demos, and external forms:**

**Configuration:** Edit `EXTERNAL_PAGES` dict in `core/views.py`:
```python
EXTERNAL_PAGES = {
    'event-invitation': {
        'title': 'Event Registration',
        'external_url': 'https://form.jotform.com/252214924850455',
        'template': 'iframe',  # iframe, landing, or redirect
    }
}
```

**Templates Available:**
- `templates/wrapper/iframe.html` - Full-screen iframe embed
- `templates/wrapper/landing.html` - Branded landing page with embed
- `templates/wrapper/redirect.html` - Auto-redirect with countdown

**Access:** `/{page-name}/` (e.g., `/event-invitation/`)

**Features:**
- Rate limiting protection
- Consistent branding
- Mobile responsive
- No database needed

## Social Media Integration

**Rich social media previews implemented in `templates/base.html`:**

**Open Graph Tags:**
- `og:title` - Page title for social sharing
- `og:description` - Page description  
- `og:image` - Preview image (`static/img/social-preview.png`)
- `og:url` - Canonical page URL
- `og:site_name` - "Quantum Tasks AI"

**Twitter Card Tags:**
- `twitter:card` - Large image format
- `twitter:title/description/image` - Twitter-specific metadata

**Custom Per-Page:** Override blocks in templates:
```django
{% block og_title %}Custom Page Title{% endblock %}
{% block meta_description %}Custom description{% endblock %}
```

**Result:** Rich previews on WhatsApp, Discord, Twitter, LinkedIn with branded image and professional descriptions.

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
- **8 agents** confirmed working and tested (4 webhook + 4 direct access)
- **6 categories** with clean, logical organization
- **Dual integration architecture** with clear separation and documentation
- **Streamlined agent creation** via JSON configs (instant file-based loading)
- **Scalable architecture** ready for 100+ agents

**Current Agents:**
- **Webhook Agents (4)**: Social Ads Generator, Job Posting Generator, PDF Summarizer, 5 Whys Analyzer
- **Direct Access Agents (4)**: CyberSec Career Navigator, AI Brand Strategist, Lean Six Sigma Expert, SWOT Analysis Expert

**Latest Changes:**
- **External service wrapper system** - Simple template-based system for JotForm, Zapier, event invitations
- **Social media meta tags** - Rich previews with Open Graph and Twitter Card tags
- **View separation completed** - Split large views.py into focused modules (api, chat, web, direct access)
- **Restored digital-branding.css** from git history with proper design system integration
- **Added SWOT Analysis Expert** with proper category assignment (analysis)
- **Streamlined agent creation process** via JSON configs (instant file-based loading)
- **Separated documentation** into focused files (`docs/AGENT_CREATION.md`)
- **Removed 10+ redundant management commands** for cleaner codebase
- **Fixed marketplace consistency** and updated documentation

**Architecture Status:**
- **Modular view architecture** - 5 focused modules for better code organization and maintainability
- **Error-free agent creation** via file-based JSON configuration
- **Railway-ready deployment** with automatic agent population
- **Consistent UI standards** across all marketplace components
- **Professional styling** - All pages properly styled with design system integration
- **Comprehensive documentation** prevents common development mistakes

**Future Development:**
- **New agents** should follow patterns in `docs/AGENT_CREATION.md`
- **Use existing categories first** to avoid unnecessary proliferation
- **JSON file-based approach** is the only supported creation method
- **New views** should be added to appropriate focused modules (api_views, chat_views, web_views, direct_access_views)

---
Last updated: 2025-01-14

## Documentation
- **Quick Agent Requests**: See `docs/AGENT_REQUEST_TEMPLATE.md` for simple agent request template
- **Agent Creation**: See `docs/AGENT_CREATION.md` for comprehensive agent creation guide  
- **Project Overview**: This file (CLAUDE.md) for Django development and architecture
