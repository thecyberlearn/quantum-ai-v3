# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NetCop Hub is a Django-based AI agent marketplace platform where users can purchase and interact with specialized AI agents. The system supports both webhook-based and API-based agents with integrated payment processing via Stripe.

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
1. **Webhook Agents** - Process requests via external webhook APIs (e.g., weather_reporter)
2. **API Agents** - Direct API integration for immediate responses

**Individual Agent Apps:**
Each agent is a separate Django app following this structure:
- `models.py` - Agent-specific request/response models
- `processor.py` - Inherits from `BaseAgentProcessor`, implements specific logic
- `views.py` - Agent detail page and request handling
- `templates/[agent_name]/detail.html` - Agent interface
- `urls.py` - Agent-specific URL routing

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

### URL Structure

```
/                           # Homepage (core app)
/pricing/                   # Pricing page (core app)
/marketplace/               # Agent marketplace (agent_base app)
/agents/<slug>/             # Agent detail redirect (agent_base app)
/auth/                      # Authentication (login, register, profile)
/wallet/                    # Wallet management and top-up (wallet app)
/wallet/stripe/             # Stripe webhooks and debug (wallet app)
/agents/[agent-slug]/       # Individual agent pages (individual apps)
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

### Agent Creation with Template Prototype

**Quick Agent Creation:**
- Use `agent_template_prototype.html` as foundation for all new agents
- Follow detailed guide in `AGENT_CREATION_GUIDE.md`
- Template provides complete CSS framework, JavaScript utilities, and UI components
- Ensures consistent user experience across all agents

### Development Workflow

1. **Adding New Agent:**
   - Use `python manage.py create_agent` command
   - Follow existing agent patterns (inherit from `BaseAgentProcessor`)
   - **Convert `agent_template_prototype.html` to Django template** - see `AGENT_CREATION_GUIDE.md`
   - Add URL routing in main `urls.py`
   - Agent will automatically appear in marketplace via `BaseAgent` model

2. **Template Development:**
   - **ALWAYS use `agent_template_prototype.html` as starting point**
   - Copy all CSS (lines 8-632) and JavaScript (lines 808-967) from prototype
   - Replace placeholder sections with agent-specific content
   - Use existing components: wallet card, processing status, quick access panel
   - Follow responsive design patterns and accessibility features

3. **Agent Template Structure:**
   ```
   templates/agent_name/detail.html:
   - Copy complete CSS framework from prototype
   - Replace "Agent Grid Section" with your form
   - Replace "Results Section" with your results display  
   - Keep "How It Works" widget and all JavaScript utilities
   - Preserve responsive design and accessibility features
   ```

4. **Database Changes:**
   - Always run migrations after model changes
   - Use `check_db` command to verify configuration
   - Test with `populate_agents` to ensure agent catalog works

### Deployment

- **Railway.app** integration via `railway.json`
- Production settings in `netcop_hub/production_settings.py`
- Static files served via WhiteNoise
- Database migrations run automatically on deployment

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