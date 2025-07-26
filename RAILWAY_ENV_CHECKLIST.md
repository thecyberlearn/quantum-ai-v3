# 🔐 Railway Environment Variables Checklist

## Critical Variables for Health Check Success

### ✅ **Required Variables (Must Set These)**
```bash
# Django Core (REQUIRED)
SECRET_KEY=your-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=your-project.railway.app,quantumtaskai.com

# Database (AUTO-SET by Railway PostgreSQL service)
# DATABASE_URL=postgresql://... (Railway sets this automatically)
```

### ⚠️ **Optional Variables (Set if Using Features)**
```bash
# Email Configuration (for contact form, password reset)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=Quantum Tasks AI <noreply@quantumtaskai.com>

# Stripe Payment (for wallet functionality)
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# N8N Webhooks (for AI agents that use webhooks)
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n-url/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=https://your-n8n-url/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=https://your-n8n-url/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n-url/webhook/social-ads

# OpenWeather API (for weather agent)
OPENWEATHER_API_KEY=your_openweather_key
```

## 🚨 Health Check Failure Troubleshooting

### Most Common Issues:

1. **Missing SECRET_KEY**
   ```
   Error: "The SECRET_KEY setting must not be empty"
   Solution: Set SECRET_KEY in Railway variables
   ```

2. **Database Not Ready**
   ```
   Error: "connection to server failed"
   Solution: Wait 30-60 seconds, Railway PostgreSQL is starting
   ```

3. **Wrong ALLOWED_HOSTS**
   ```
   Error: "DisallowedHost at /health/"
   Solution: Add Railway domain to ALLOWED_HOSTS
   ```

## 🔧 Quick Fixes

### Generate SECRET_KEY
```python
# Run locally
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Minimal Working Configuration
```bash
# These 3 variables will make health check pass:
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-project.railway.app
```

### Test Health Check Locally
```bash
# Set minimal env vars and test
export SECRET_KEY="your-secret-key"
export DEBUG=False
export ALLOWED_HOSTS="localhost,127.0.0.1"
python manage.py runserver
curl http://localhost:8000/health/
```

## 📊 Expected Health Check Response
```json
{
  "status": "healthy",
  "timestamp": 1690123456,
  "version": "1.0",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12.3,
      "attempt": 1
    },
    "agents": {
      "status": "healthy",
      "active_count": 6
    },
    "application": {
      "status": "healthy",
      "django_ready": true
    }
  },
  "response_time_ms": 45.2
}
```

## 🎯 Deployment Steps
1. Set minimum required variables in Railway
2. Deploy with updated railway.json (60s timeout)
3. Check Railway logs for errors
4. Test health endpoint: `curl https://your-project.railway.app/health/`
5. Add optional variables as needed for full functionality

**Health check should pass within 60 seconds with just the 3 critical variables!**