# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quantum Tasks AI is a Django-based AI agent marketplace platform. Users can purchase AI agent services through a web interface, with agent execution handled via N8N webhooks and payments processed through Stripe.

**Key Architecture:**
- **Django Framework**: Main web application using Django 5.2.4
- **Agent System**: Database-driven agents app with marketplace and N8N webhook execution
- **Authentication**: Custom user model with email verification
- **Payments**: Stripe integration with wallet system
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
- `agents/models.py`: Agent, AgentCategory, AgentExecution models
- `agents/views.py`: REST API and web interface views
- `agents/templates/agents/`: Dynamic agent templates with form generation
- `agents/management/commands/`: Agent creation and management commands

**Agent Flow:**
1. User browses marketplace (`/agents/`)
2. Selects agent and fills dynamic form (`/agents/{slug}/`)
3. Form submission creates AgentExecution and calls N8N webhook
4. N8N processes request and returns response via webhook
5. Results displayed with file upload support and real-time wallet updates

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

**N8N Webhook URLs:**
Agent-specific webhook URLs are stored in the database with each agent. Current working agents (all tested and confirmed working):

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

### URL Structure
```
/                       # Homepage (core app)
/auth/                  # Authentication (login, register, etc.)
/agents/                # Agent marketplace (agents app)
/agents/{slug}/         # Individual agent pages
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

1. **Create management command** (recommended approach):
```python
# agents/management/commands/create_new_agent.py
from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    def handle(self, *args, **options):
        category, _ = AgentCategory.objects.get_or_create(
            slug='category-slug',
            defaults={'name': 'Category Name', 'icon': '🤖'}
        )
        
        Agent.objects.get_or_create(
            slug='agent-slug',
            defaults={
                'name': 'Agent Name',
                'short_description': 'Brief description',
                'description': 'Full description',
                'category': category,
                'price': 10.0,
                'form_schema': {
                    'fields': [
                        {
                            'name': 'input_field',
                            'type': 'text',
                            'label': 'Input Field',
                            'required': True
                        }
                    ]
                },
                'webhook_url': 'http://your-n8n-webhook-url'
            }
        )
```

2. **Run the command**: `python manage.py create_new_agent`
3. **Update N8N workflow** to handle the new agent
4. **Agent will automatically appear** in marketplace with dynamic form generation

**Supported Form Field Types:**
- `text`: Text input
- `textarea`: Multi-line text
- `select`: Dropdown with options
- `file`: File upload with drag-and-drop
- `url`: URL input with validation
- `checkbox`: Boolean checkbox

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

**Current Status: ✅ STABLE WORKING SYSTEM**
- All 3 agents confirmed working and tested
- Clean agents-only architecture (workflows app completely removed)
- Emergency recovery completed from optimization failures
- System restored to stable commit 657712f

**Latest Changes:**
- Removed workflows app completely for simplified architecture
- Enhanced agent marketplace with modern responsive design
- Fixed all authentication-aware UI components
- Implemented file upload support for PDF Summarizer
- Real-time wallet balance updates after agent execution

**Future Development:**
- Optimization work available in feature/optimization-backup branch
- Safe to add new agents via database-driven approach
- Performance optimizations should be applied incrementally with testing

---
Last updated: Last updated: Last updated: Last updated: Last updated: 2025-08-01 09:22:55
