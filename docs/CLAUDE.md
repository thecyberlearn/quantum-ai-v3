# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NetCop Hub is a Django-based AI agent marketplace that allows users to purchase and use various AI-powered agents for tasks like social media ad generation, data analysis, weather reporting, and more. The system features a wallet-based payment system with Stripe integration and N8N webhook processing.

### Project Structure
```
netcop_django/
├── 📁 docs/              # All documentation, guides, and logs
├── 📁 tests/             # All test files and scripts
├── 📁 agent_base/        # Agent framework and creation tools
├── 📁 authentication/    # User management system
├── 📁 core/              # Main app (homepage, marketplace, wallet)
├── 📁 wallet/            # Payment and transaction system
├── 📁 weather_reporter/  # Example individual agent app
│   └── templates/        # Agent-specific templates
├── 📁 templates/         # Global templates (core, auth)
├── 📁 static/            # Static assets (CSS, JS, images)
├── 📁 media/             # User-uploaded files
├── 📁 netcop_hub/        # Django project configuration
└── manage.py             # Django management commands
```

## Key Architecture Components

### Individual Agent Architecture
The project uses a modular individual agent architecture where each agent is a separate Django app:

- **Base Framework**: `agent_base/` provides common functionality:
  - `BaseAgent` model for agent marketplace catalog
  - `BaseAgentRequest`/`BaseAgentResponse` abstract models for tracking
  - `BaseAgentProcessor` abstract class for webhook handling
  - `BaseAgentView` abstract class for form processing and authentication

- **Individual Agent Apps**: Each agent has its own app (`agent_social_ads/`, `agent_weather/`, etc.):
  - Custom models extending base classes
  - Specialized processors for webhook communication
  - Individual views and URL routing
  - Separate templates and static files

### Webhook Processing System
All agents communicate with external AI services via N8N webhooks:
- Processors handle data preparation, request/response processing
- Webhook URLs configured via environment variables
- Built-in error handling and timeout management
- Processing time tracking and logging

### User Authentication & Wallet System
- Custom User model with wallet balance functionality
- Stripe integration for payments (`wallet/stripe_handler.py`)
- Transaction tracking via `WalletTransaction` model
- Balance checking before agent usage

## Essential Commands

### Development Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (no requirements.txt - manual installation needed)
pip install django djangorestframework python-decouple stripe requests

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Populate agents catalog
python manage.py populate_base_agents
```

### Running the Application
```bash
# Start development server
python manage.py runserver

# Run with specific settings
python manage.py runserver --settings=netcop_hub.settings
```

### Database Management
```bash
# Create new migrations
python manage.py makemigrations [app_name]

# Apply migrations
python manage.py migrate

# Reset database (if needed)
python manage.py flush

# Django shell
python manage.py shell
```

### Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test agent_social_ads

# Run with verbosity
python manage.py test --verbosity=2
```

## Environment Configuration

The project uses python-decouple for environment management. Key variables in `.env`:

### Required Settings
- `SECRET_KEY`: Django secret key
- `DEBUG`: Development mode flag
- `ALLOWED_HOSTS`: Comma-separated host list
- `DATABASE_URL`: PostgreSQL connection string (uses SQLite by default)

### Webhook Configuration
Each agent requires webhook URLs in format:
- `N8N_WEBHOOK_[AGENT_NAME]`: Django backend webhook URL
- `NEXT_PUBLIC_N8N_WEBHOOK_[AGENT_NAME]`: Frontend webhook URL

### Payment Integration
- `STRIPE_SECRET_KEY`: Stripe API secret key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook signing secret
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Stripe publishable key

## Agent Creation System (Automated)

### Automated Agent Creation Command
The project features a sophisticated automated agent creation system via the `create_agent` management command:

```bash
# Create webhook-based agent (N8N integration)
python manage.py create_agent "Agent Name" "agent-slug" webhook \
  --category utilities --price 2.5 \
  --webhook-url "https://webhook.url" --agent-id "123"

# Create API-based agent (Direct API integration)
python manage.py create_agent "Weather Reporter" "weather-reporter" api \
  --category utilities --price 2.5 \
  --api-base-url "https://api.openweathermap.org/data/2.5/weather" \
  --api-key-env "OPENWEATHER_API_KEY" --auth-method query
```

### Agent Creation System Architecture

#### Core Framework (agent_base app)
- **BaseAgent Model**: Database catalog for agent marketplace
- **BaseAgentRequest/BaseAgentResponse**: Abstract models for tracking requests
- **StandardWebhookProcessor**: Handles N8N webhook integrations with message payload format
- **StandardAPIProcessor**: Handles direct API calls with flexible authentication methods
- **WebhookFormatDetector**: Utility to test and detect webhook formats

#### Template-Based Code Generation
The system uses Django templates to generate complete agent apps:

**Template Files:**
- `webhook_models.py` / `api_models.py`: Models with custom fields
- `webhook_processor.py` / `api_processor.py`: Processor classes
- `views.py`: Django views with authentication and wallet integration
- `urls.py`: URL routing patterns
- `admin.py`: Django admin configuration
- `apps.py`: Django app configuration

#### Supported Agent Types

**1. Webhook Agents (N8N Integration)**
- Uses `StandardWebhookProcessor` base class
- Message-based payload format: `{'message': {'text': 'content'}, 'sessionId': '...', 'userId': '...', 'agentId': '...'}`
- Automatic error handling and retry logic
- Processing time tracking

**2. API Agents (Direct Integration)**
- Uses `StandardAPIProcessor` base class
- Multiple authentication methods: bearer, api-key, basic, query
- GET/POST request support
- Response parsing and formatting

#### Weather Reporter Example
The system includes a complete Weather Reporter agent example:
- **API Integration**: OpenWeatherMap API
- **Custom Fields**: location, report_type, temperature, humidity, wind_speed
- **Formatted Reports**: Both current and detailed weather reports
- **Error Handling**: API failures and invalid locations

### Management Commands

#### create_agent
Generates complete agent apps with:
- Database models and migrations
- Processor classes
- Django views with authentication
- URL routing
- Admin interface
- Custom field definitions based on agent type

```bash
python manage.py create_agent --help
```

#### test_webhook
Tests webhook endpoints to determine compatible formats:
```bash
# Test all formats
python manage.py test_webhook https://webhook.url

# Detect best format only
python manage.py test_webhook https://webhook.url --detect-best
```

### Manual Agent Creation (Legacy)

For custom agents requiring manual setup:

#### Step 1: Create Django App
```bash
python manage.py startapp agent_[name]
```

#### Step 2: Define Models
Extend `BaseAgentRequest` and `BaseAgentResponse` in `models.py`:
```python
from agent_base.models import BaseAgentRequest, BaseAgentResponse

class MyAgentRequest(BaseAgentRequest):
    # Add agent-specific fields
    input_text = models.TextField()

class MyAgentResponse(BaseAgentResponse):
    request = models.OneToOneField(MyAgentRequest, on_delete=models.CASCADE, related_name='response')
    output_text = models.TextField(blank=True)
```

#### Step 3: Create Processor
Choose between webhook or API processor:

**Webhook Processor:**
```python
from agent_base.processors import StandardWebhookProcessor

class MyAgentProcessor(StandardWebhookProcessor):
    agent_slug = 'my-agent'
    webhook_url = settings.N8N_WEBHOOK_MY_AGENT
    agent_id = '123'
    
    def prepare_message_text(self, **kwargs):
        return f"Process: {kwargs.get('input_text')}"
```

**API Processor:**
```python
from agent_base.processors import StandardAPIProcessor

class MyAgentProcessor(StandardAPIProcessor):
    agent_slug = 'my-agent'
    api_base_url = 'https://api.example.com/v1/process'
    api_key_env = 'MY_API_KEY'
    auth_method = 'bearer'
    
    def prepare_request_data(self, **kwargs):
        return {'text': kwargs.get('input_text')}
```

#### Step 4: Add to Configuration
- Add app to `INSTALLED_APPS` in `settings.py`
- Add URL routing in `netcop_hub/urls.py`
- Run migrations: `python manage.py makemigrations && python manage.py migrate`
- Create BaseAgent entry in database

## Database Models Relationships

### Core Models
- `User` (authentication): Custom user with wallet functionality
- `BaseAgent` (agent_base): Agent catalog/marketplace entries
- `WalletTransaction` (wallet): Payment and usage tracking

### Agent-Specific Models
Each agent app has:
- `[Agent]Request`: Inherits from `BaseAgentRequest`, tracks user requests
- `[Agent]Response`: Inherits from `BaseAgentResponse`, stores AI responses

### Key Relationships
- `User` 1:N `BaseAgentRequest` (user can make multiple requests)
- `BaseAgent` 1:N `BaseAgentRequest` (agent can have multiple requests)
- `BaseAgentRequest` 1:1 `BaseAgentResponse` (each request has one response)
- `User` 1:N `WalletTransaction` (user has transaction history)

## URL Structure

```
/                           # Homepage (core app)
/auth/login/               # Authentication
/auth/register/            # User registration
/agents/[agent-slug]/      # Individual agent pages
/admin/                    # Django admin
```

## Template Organization

Templates follow clean Django app structure:
- `templates/core/`: Homepage, marketplace, wallet (global templates)
- `templates/authentication/`: Login, registration (global templates)
- `[agent_name]/templates/`: Individual agent templates within their respective apps (detail.html)
- `docs/`: All documentation and guides
- `tests/`: All test files

## Common Development Patterns

### Adding New Agent Fields
1. Add fields to agent request/response models
2. Update processor's `prepare_request_data()` method
3. Modify view's `process_request()` method
4. Update templates to include new fields

### Debugging Webhook Issues
1. Check webhook URL in `.env` file
2. Examine processor logs in console output
3. Verify JSON payload format in `prepare_request_data()`
4. Test webhook independently with tools like Postman

### Managing Agent Pricing
1. Update price in `populate_base_agents.py`
2. Run `python manage.py populate_base_agents` to update database
3. Pricing is enforced in `BaseAgentView.post()` method

## Current Architecture (Clean & Modern)

The project uses a clean, modular individual agent architecture:

### Current System Features
- **Individual agent apps**: Each agent is a separate Django app (`weather_reporter/`, etc.)
- **Clean template organization**: Templates live within their respective agent apps
- **Organized project structure**: Documentation in `docs/`, tests in `tests/`, clean root directory
- **BaseAgent catalog system**: Centralized marketplace with individual agent implementations
- **Modular processors**: Each agent has its own processor for API/webhook integration
- **App-specific templates**: `agent_name/templates/detail.html`

### Best Practices
- All new agents should follow the individual app architecture
- Templates should be placed within the agent app, not in global templates
- Use the `create_agent` command for automated setup, then follow the setup checklist
- Keep root directory clean - use `docs/` and `tests/` folders for organization