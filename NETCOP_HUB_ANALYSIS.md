# NetCop Hub - Application Architecture Analysis

*Analysis Date: 2025-07-24*  
*Analyst: Claude Code Assistant*

## Overview

NetCop Hub is a Django-based AI agent marketplace platform where users can purchase and interact with specialized AI agents through a pay-per-use model with integrated Stripe payments. The application demonstrates sophisticated architecture with clear separation of concerns and extensible design patterns.

## Project Structure

```
quantum_ai/
├── CLAUDE.md                    # Project documentation and instructions
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # SQLite database (development)
├── run_dev.sh                   # Development server startup script
├── railway.json                 # Railway.app deployment configuration
├── netcop_hub/                  # Main Django project
│   ├── settings.py              # Django settings with environment config
│   ├── urls.py                  # Main URL routing
│   └── production_settings.py   # Production-specific settings
├── static/                      # Static assets (CSS, JS, images)
├── templates/                   # Django templates
├── media/                       # User uploaded files
├── logs/                        # Application logs
└── [apps]/                      # Individual Django applications
```

## Core Architecture

### Django Applications Structure

1. **Core App** (`core/`)
   - Purpose: Platform homepage, pricing pages, static content
   - Responsibility: Platform presentation layer only
   - URL namespace: `core:homepage`, `core:pricing`

2. **Agent Base** (`agent_base/`)
   - Purpose: Agent marketplace, catalog management, cross-agent functionality
   - Key Models: `BaseAgent`, `BaseAgentRequest`, `BaseAgentResponse`
   - URL namespace: `agent_base:marketplace`
   - Location: `agent_base/models.py:9-90`

3. **Authentication** (`authentication/`)
   - Purpose: User management with integrated wallet functionality
   - Key Model: Custom `User` extending AbstractUser
   - Features: Email-based auth, password reset tokens, wallet integration
   - Location: `authentication/models.py:9-83`

4. **Wallet** (`wallet/`)
   - Purpose: Complete payment system with Stripe integration
   - Key Model: `WalletTransaction` for financial tracking
   - Features: Top-ups, usage tracking, transaction history
   - Location: `wallet/models.py:8-31`

5. **Individual Agent Apps**
   - Structure: Each agent is a separate Django app
   - Examples: `weather_reporter/`, `data_analyzer/`, `job_posting_generator/`
   - Pattern: `models.py`, `processor.py`, `views.py`, `urls.py`, `templates/`

## Agent System Architecture

### Agent Types

The platform supports two distinct agent processing patterns:

#### 1. Webhook Agents
- **Processing**: External N8N webhook APIs
- **Examples**: data_analyzer, five_whys_analyzer, job_posting_generator
- **Base Class**: `StandardWebhookProcessor`
- **Use Cases**: Complex data processing, file uploads, multi-step workflows

#### 2. API Agents  
- **Processing**: Direct API integration
- **Examples**: weather_reporter (OpenWeather API)
- **Base Class**: `StandardAPIProcessor` 
- **Use Cases**: Real-time data fetching, simple request/response patterns

### Agent Processing Framework

Location: `agent_base/processors.py:10-255`

#### Base Classes Hierarchy
```python
BaseAgentProcessor (ABC)
├── StandardWebhookProcessor
└── StandardAPIProcessor
```

#### Key Methods
- `prepare_request_data(**kwargs)` - Format input data
- `make_request(data, timeout=60)` - Execute HTTP request
- `process_response(response_data, request_obj)` - Handle response and create DB objects
- `process_request(**kwargs)` - Main orchestration method

#### Example Implementation - Weather Reporter
Location: `weather_reporter/processor.py:7-139`
```python
class WeatherReporterProcessor(StandardAPIProcessor):
    agent_slug = 'weather-reporter'
    api_base_url = 'https://api.openweathermap.org/data/2.5/weather'
    api_key_env = 'OPENWEATHER_API_KEY'
    auth_method = 'query'
```

#### Example Implementation - Data Analyzer
Location: `data_analyzer/processor.py:11-217`
```python
class DataAnalysisAgentProcessor(StandardWebhookProcessor):
    agent_slug = 'data-analyzer'
    webhook_url = settings.N8N_WEBHOOK_DATA_ANALYZER
    agent_id = 'data-analysis-001'
```

## Database Models

### User Model (`authentication/models.py:9-83`)
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Wallet methods
    def has_sufficient_balance(self, amount)
    def deduct_balance(self, amount, description="", agent_slug="")
    def add_balance(self, amount, description="", stripe_session_id="")
```

### BaseAgent Model (`agent_base/models.py:9-59`)
```python
class BaseAgent(models.Model):
    CATEGORIES = [
        ('analytics', 'Analytics'),
        ('utilities', 'Utilities'),
        ('content', 'Content'),
        ('marketing', 'Marketing'),
        ('customer-service', 'Customer Service'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    agent_type = models.CharField(max_length=20, choices=[
        ('webhook', 'Webhook'),
        ('api', 'API'),
    ])
```

### WalletTransaction Model (`wallet/models.py:8-31`)
```python
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('top_up', 'Top Up'),
        ('agent_usage', 'Agent Usage'),
        ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    stripe_session_id = models.CharField(max_length=200, blank=True)
```

## URL Structure & Routing

From `netcop_hub/urls.py:22-33`:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('wallet/', include('wallet.urls')),
    path('', include('agent_base.urls')),           # Marketplace
    path('agents/weather-reporter/', include('weather_reporter.urls')),
    path('agents/data-analyzer/', include('data_analyzer.urls')),
    path('agents/job-posting-generator/', include('job_posting_generator.urls')),
    path('agents/social-ads-generator/', include('social_ads_generator.urls')),
    path('agents/five-whys-analyzer/', include('five_whys_analyzer.urls')),
    path('', include('core.urls')),                 # Homepage
]
```

### URL Mapping
- `/` - Homepage (core app)
- `/pricing/` - Pricing page (core app)
- `/marketplace/` - Agent marketplace (agent_base)
- `/agents/<agent-slug>/` - Individual agent pages
- `/auth/` - Authentication (login, register, profile)
- `/wallet/` - Wallet management and Stripe integration
- `/admin/` - Django admin interface

## Technology Stack

### Core Dependencies (from `requirements.txt`)
```
Django==5.2.4
djangorestframework==3.15.2
python-decouple==3.8
stripe==12.3.0
Pillow==11.3.0
requests==2.32.4
gunicorn==21.2.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
whitenoise==6.8.2
redis==5.2.0
django-redis==5.4.0
```

### Database Configuration
- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL via Railway
- **Smart Detection**: Auto-detects environment and configures appropriately

### Caching Strategy
From `netcop_hub/settings.py:293-323`:
- **Primary**: Redis cache with django-redis client
- **Fallback**: Local memory cache if Redis unavailable
- **Session Storage**: Cache-based sessions

### Static Files & Media
- **Static Files**: WhiteNoise for production serving
- **Media Files**: Local filesystem with cleanup management
- **Upload Handling**: Automatic file cleanup after processing

## Payment System

### Stripe Integration
- **Environment Variables**: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- **Payment Flow**: Checkout sessions → webhook handling → wallet top-up
- **Transaction Tracking**: Complete audit trail in `WalletTransaction`

### Wallet Functionality
- **Balance Management**: User model integrates wallet operations
- **Usage Deduction**: Automatic deduction after successful agent processing
- **Transaction Types**: Top-up, agent usage, refunds

## Security Features

### Authentication & Authorization
- **Custom User Model**: Email-based authentication
- **Password Reset**: Token-based system with expiration
- **Session Management**: Cache-based with 1-hour timeout

### Production Security (from `netcop_hub/settings.py:114-123`)
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### File Upload Security
- **File Cleanup**: Automatic deletion after processing
- **Path Validation**: Secure file handling in processors
- **Content Type Validation**: PDF validation for data analyzer

## Development Tools & Commands

### Management Commands
Located in `agent_base/management/commands/`:
- `python manage.py create_agent` - Generate new agent boilerplate
- `python manage.py populate_agents` - Populate agent catalog
- `python manage.py create_user` - Create test users
- `python manage.py check_db` - Validate database configuration
- `python manage.py reset_database` - Reset development database
- `python manage.py backup_users` - User data backup utilities
- `python manage.py test_webhook` - Webhook testing utilities

### Development Workflow
1. **Quick Start**: `./run_dev.sh` (handles migrations and environment)
2. **Manual Start**: `python manage.py runserver`
3. **Testing**: Individual test files in `tests/` directory
4. **Agent Creation**: Use management command with template system

## Deployment

### Railway.app Integration
- **Configuration**: `railway.json` for deployment settings
- **Environment Detection**: Automatic Railway environment detection
- **Database**: PostgreSQL with automatic URL parsing
- **Static Files**: WhiteNoise middleware for production serving

### Environment Variables
From `netcop_hub/settings.py:31-38` - Required variables validation:
```python
required_env_vars = ['SECRET_KEY']
missing_vars = [var for var in required_env_vars if not config(var, default='')]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)
```

## Logging Configuration

### Log Levels & Handlers (from `netcop_hub/settings.py:337-389`)
- **File Logging**: `netcop.log` for persistent logging
- **Console Logging**: Development debugging
- **App-Specific Loggers**: `agent_base`, `wallet`, `netcop_hub`
- **Django Integration**: Complete Django logging integration

## Template Architecture

### Template Hierarchy
```
templates/
├── base.html                    # Main layout with navigation
├── components/                  # Reusable components
│   ├── agent_header.html
│   ├── wallet_card.html
│   ├── processing_status.html
│   └── results_container.html
├── core/                        # Platform pages
├── agent_base/                  # Marketplace templates
├── authentication/              # Auth templates
├── wallet/                      # Payment templates
└── [agent_apps]/                # Agent-specific templates
```

### CSS Architecture
```
static/css/
├── base.css                     # Global styles and CSS variables
├── agent-base.css               # Agent page styling
├── header-component.css         # Header styling
├── marketplace.css              # Marketplace styling
└── themes.css                   # Theme definitions
```

## Key Design Patterns

### 1. Single Responsibility Principle
- **Core**: Platform presentation only
- **Agent Base**: Marketplace and cross-agent functionality
- **Wallet**: Complete payment system
- **Individual Agents**: Specific agent logic

### 2. Abstract Base Classes
- `BaseAgentProcessor` for standardized agent processing
- `BaseAgentRequest` and `BaseAgentResponse` for consistent data models
- Template method pattern in processor classes

### 3. Environment-Based Configuration
- Automatic environment detection (Railway vs local)
- Smart database configuration with fallbacks
- Required environment variable validation

### 4. Extensible Agent System
- Template generation for new agents
- Standardized processor interfaces
- Automatic marketplace integration

## Performance Considerations

### Caching Strategy
- Redis for session storage and application caching
- Graceful fallback to memory cache
- Database query optimization with indexes

### File Management
- Automatic cleanup of uploaded files
- Efficient file processing in agent processors
- Media file organization by agent type

### Database Optimization
- UUID primary keys for distributed systems
- Strategic database indexes on User model
- Efficient query patterns in processors

## Error Handling & Monitoring

### Exception Management
- Standardized error handling in processor base classes
- Graceful degradation for external service failures  
- Comprehensive error logging throughout the application

### Transaction Safety
- Database transaction handling in wallet operations
- Rollback mechanisms for failed agent processing
- Consistent state management across agent requests

## Future Extensibility

### Adding New Agents
1. Use `python manage.py create_agent` management command
2. Implement processor class inheriting from appropriate base
3. Define agent-specific models and views
4. Agent automatically appears in marketplace via `BaseAgent`

### Scaling Considerations
- UUID-based primary keys support distributed architectures
- Redis caching ready for horizontal scaling
- Modular app structure supports microservice migration
- Environment-based configuration supports multi-environment deployments

## Security Best Practices

### Data Protection
- Automatic file cleanup prevents data accumulation
- Secure file upload handling with validation
- Environment variable configuration for sensitive data

### Authentication Security
- Email-based authentication with secure password handling
- Token-based password reset with expiration
- Production security headers and HTTPS enforcement

---

*This analysis provides a comprehensive overview of the NetCop Hub application architecture, suitable for development planning, maintenance, and future enhancements.*