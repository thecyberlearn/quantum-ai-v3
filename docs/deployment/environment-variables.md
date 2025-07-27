# ⚙️ Environment Variables Guide

Complete reference for all environment variables used in Quantum Tasks AI.

## 📋 Overview

This guide covers all environment variables needed for:
- 🏠 Local development
- 🚀 Railway production deployment
- 🔧 Testing and staging environments

---

## 🔐 Required Variables

### Core Django Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | None | Django secret key (50+ random characters) |
| `DEBUG` | ⚠️ Production | `True` | Debug mode (`True` for dev, `False` for production) |
| `ALLOWED_HOSTS` | ⚠️ Production | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | ⚠️ Production | `http://localhost:8000` | Comma-separated list of trusted origins |

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | 🔶 Railway | SQLite | PostgreSQL connection string |
| `USE_POSTGRESQL` | ❌ Optional | `False` | Force PostgreSQL in local development |

### Email Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_BACKEND` | ⚠️ Production | `console` | Email backend type |
| `EMAIL_HOST` | ⚠️ Production | `smtp.gmail.com` | SMTP server hostname |
| `EMAIL_PORT` | ❌ Optional | `587` | SMTP server port |
| `EMAIL_USE_TLS` | ❌ Optional | `True` | Use TLS encryption |
| `EMAIL_HOST_USER` | ⚠️ Production | None | SMTP username/email |
| `EMAIL_HOST_PASSWORD` | ⚠️ Production | None | SMTP password/app password |
| `DEFAULT_FROM_EMAIL` | ❌ Optional | `Quantum Tasks AI <noreply@quantumtaskai.com>` | Default sender email |

### Payment Processing (Stripe)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | ⚠️ Production | None | Stripe secret key (`sk_test_...` or `sk_live_...`) |
| `STRIPE_WEBHOOK_SECRET` | ⚠️ Production | None | Stripe webhook endpoint secret |

---

## 🔗 External Integrations

### N8N Webhook URLs

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `N8N_WEBHOOK_DATA_ANALYZER` | 🔶 Agent | None | Data analyzer webhook URL |
| `N8N_WEBHOOK_FIVE_WHYS` | 🔶 Agent | None | Five whys analyzer webhook URL |
| `N8N_WEBHOOK_JOB_POSTING` | 🔶 Agent | None | Job posting generator webhook URL |
| `N8N_WEBHOOK_SOCIAL_ADS` | 🔶 Agent | None | Social ads generator webhook URL |
| `N8N_WEBHOOK_FAQ_GENERATOR` | 🔶 Agent | None | FAQ generator webhook URL |

### Weather API

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENWEATHER_API_KEY` | 🔶 Agent | None | OpenWeather API key for weather agent |

---

## 🌍 Environment-Specific Configurations

### 🏠 Local Development

Create `.env` file in project root:

```env
# Core Settings
SECRET_KEY=your-50-character-secret-key-for-development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Database (uses SQLite by default)
# Uncomment to use PostgreSQL locally:
# DATABASE_URL=postgresql://user:password@localhost:5432/quantum_ai

# Email (uses console backend by default)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stripe (use test keys)
STRIPE_SECRET_KEY=sk_test_your_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret

# N8N (local or development instance)
N8N_WEBHOOK_DATA_ANALYZER=http://localhost:5678/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=http://localhost:5678/webhook/five-whys

# External APIs
OPENWEATHER_API_KEY=your_test_api_key
```

### 🚀 Railway Production

Set in Railway Dashboard → Variables:

```env
# Core Settings
SECRET_KEY=your-production-secret-key-50-characters-minimum
DEBUG=False
ALLOWED_HOSTS=quantum-ai.up.railway.app,quantumtaskai.com
CSRF_TRUSTED_ORIGINS=https://quantum-ai.up.railway.app,https://quantumtaskai.com

# Database (automatically provided by Railway)
DATABASE_URL=${{ Postgres.DATABASE_URL }}

# Cache (automatically provided by Railway if Redis added)
REDIS_URL=${{ Redis.REDIS_URL }}

# Email (production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-production-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=Quantum Tasks AI <your-production-email@gmail.com>

# Stripe (production keys)
STRIPE_SECRET_KEY=sk_live_your_live_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret

# N8N (production instance)
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n-instance.com/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=https://your-n8n-instance.com/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=https://your-n8n-instance.com/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n-instance.com/webhook/social-ads
N8N_WEBHOOK_FAQ_GENERATOR=https://your-n8n-instance.com/webhook/faq-generator

# External APIs (production keys)
OPENWEATHER_API_KEY=your_production_openweather_key
```

---

## 🔧 Advanced Configuration

### Cache Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | ❌ Optional | `redis://127.0.0.1:6379/1` | Redis connection URL |

**Cache Behavior:**
- **Redis available**: Uses Redis for sessions and caching
- **Redis unavailable**: Falls back to in-memory cache
- **Railway**: Automatically configured when Redis service added

### Domain Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SITE_URL` | ❌ Optional | Auto-detected | Base URL for email links |
| `RAILWAY_PUBLIC_DOMAIN` | ❌ Optional | Auto-detected | Custom Railway domain |

**Auto-Detection Logic:**
```python
# Development
SITE_URL = "http://localhost:8000"

# Railway Production
SITE_URL = "https://quantum-ai.up.railway.app"

# Custom Domain
SITE_URL = "https://your-custom-domain.com"
```

### Security Headers

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECURE_SSL_REDIRECT` | ❌ Auto | `True` in production | Force HTTPS redirects |
| `SECURE_HSTS_SECONDS` | ❌ Auto | `31536000` in production | HSTS header duration |

---

## 🛠️ Setup Instructions

### 1. Generate Secret Key

```python
# In Django shell or Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 2. Configure Gmail SMTP

1. **Enable 2FA** on your Gmail account
2. **Generate App Password:**
   - Go to Google Account Settings
   - Security → 2-Step Verification
   - App passwords → Generate password
   - Use the generated password as `EMAIL_HOST_PASSWORD`

### 3. Configure Stripe

1. **Get API Keys:**
   - Login to [Stripe Dashboard](https://dashboard.stripe.com/)
   - Developers → API keys
   - Copy Publishable and Secret keys

2. **Set up Webhooks:**
   - Developers → Webhooks → Add endpoint
   - URL: `https://your-domain.com/wallet/stripe/webhook/`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`

### 4. Configure N8N Webhooks

```bash
# List available workflows
python manage_n8n_workflows.py list

# Import to N8N instance
python manage_n8n_workflows.py import data_analyzer

# Get webhook URLs from N8N and add to environment variables
```

---

## ✅ Validation & Testing

### Environment Variable Checker

```bash
# Check required variables are set
python manage.py check --deploy

# Test database connection
python manage.py check --database default

# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

### Health Check Endpoint

```bash
# Test all systems
curl https://your-domain.com/health/

# Expected response
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "cache": {"status": "healthy"},
    "agents": {"status": "healthy", "active_count": 7}
  }
}
```

---

## 🆘 Troubleshooting

### Common Issues

**❌ Secret Key Error:**
```bash
# Error: SECRET_KEY setting must not be empty
# Solution: Set SECRET_KEY environment variable
SECRET_KEY=your-50-character-secret-key
```

**❌ Database Connection Error:**
```bash
# Error: FATAL: database "railway" does not exist
# Solution: Ensure PostgreSQL service is added in Railway
DATABASE_URL=${{ Postgres.DATABASE_URL }}
```

**❌ CSRF Verification Failed:**
```bash
# Error: CSRF verification failed
# Solution: Add your domain to CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

**❌ Email Not Sending:**
```bash
# Error: SMTPAuthenticationError
# Solution: Use Gmail App Password, not regular password
EMAIL_HOST_PASSWORD=your-16-character-app-password
```

### Environment Validation Script

```python
# Check all required variables
import os
from decouple import config

required_vars = [
    'SECRET_KEY',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD',
    'STRIPE_SECRET_KEY'
]

missing_vars = []
for var in required_vars:
    if not config(var, default=''):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing variables: {', '.join(missing_vars)}")
else:
    print("✅ All required variables are set")
```

---

## 📚 Related Documentation

- [Railway Deployment Guide](./railway-deployment.md)
- [Domain Change Guide](./domain-change-guide.md)
- [Database Management](../operations/database-management.md)

---

**📝 Note:** Always use test keys during development and live keys only in production. Never commit sensitive environment variables to version control.