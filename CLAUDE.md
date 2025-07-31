# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quantum Tasks AI is a Django-based AI agent marketplace platform. Users can purchase AI agent services through a web interface, with agent execution handled via N8N webhooks and payments processed through Stripe.

**Key Architecture:**
- **Django Framework**: Main web application using Django 5.2.4
- **Agent System**: Unified workflows app handling all AI agents via N8N webhooks
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
python manage.py test workflows
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
- **workflows/**: Unified agent system (marketplace, execution, models)
- **wallet/**: Stripe payments, wallet management, transactions

### Agent System (workflows app)
**Key Files:**
- `workflows/config/agents.py`: Agent definitions and configurations
- `workflows/models.py`: WorkflowRequest, WorkflowResponse, WorkflowAnalytics
- `workflows/views.py`: Marketplace and agent execution views
- `workflows/templates/workflows/`: Agent-specific templates

**Agent Flow:**
1. User selects agent from marketplace (`/agents/`)
2. Fills agent-specific form (`/agents/{slug}/`)
3. Form submission creates WorkflowRequest and calls N8N webhook
4. N8N processes request and returns response via webhook
5. WorkflowResponse stores results for user retrieval

### Database Models
**User Management:**
- `authentication.User`: Custom user model with email verification
- `authentication.PasswordResetToken`: Password reset tokens
- `authentication.EmailVerificationToken`: Email verification tokens

**Workflows:**
- `workflows.WorkflowRequest`: Universal agent request model
- `workflows.WorkflowResponse`: Universal agent response model  
- `workflows.WorkflowAnalytics`: Usage tracking and analytics

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
- `N8N_WEBHOOK_DATA_ANALYZER`: Data analysis agent webhook
- `N8N_WEBHOOK_FIVE_WHYS`: Five whys analysis webhook
- `N8N_WEBHOOK_JOB_POSTING`: Job posting generator webhook
- `N8N_WEBHOOK_FAQ_GENERATOR`: FAQ generator webhook
- `N8N_WEBHOOK_SOCIAL_ADS`: Social ads generator webhook

### URL Structure
```
/                       # Homepage (core app)
/auth/                  # Authentication (login, register, etc.)
/agents/                # Agent marketplace (workflows app)
/agents/{slug}/         # Individual agent pages
/wallet/                # Wallet management
/admin/                 # Django admin
```

### Key Components
**Agent Configuration (workflows/config/agents.py):**
- Centralizes all agent metadata (pricing, descriptions, webhooks)
- No database dependency for agent definitions
- Easy to add new agents by updating AGENT_CONFIGS

**Templates:**
- `templates/base.html`: Main layout with navigation
- `templates/components/`: Reusable UI components
- `workflows/templates/workflows/`: Agent-specific forms and pages

## Adding New Agents

1. **Add agent config** in `workflows/config/agents.py`:
```python
'new-agent-slug': {
    'name': 'Agent Name',
    'description': 'Agent description',
    'price': 10.0,
    'icon': '🤖',
    'webhook_url': 'N8N_WEBHOOK_URL',
}
```

2. **Create agent template** in `workflows/templates/workflows/{slug}.html`
3. **Add webhook URL** to environment variables
4. **Update N8N workflow** to handle new agent type

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
2. Update webhook URLs in agent config
3. Test agent execution flow
4. Check WorkflowRequest/WorkflowResponse creation

---
Last updated: Last updated: Last updated: Last updated: Last updated: Last updated: Last updated: Last updated: 2025-07-31 22:55:38
