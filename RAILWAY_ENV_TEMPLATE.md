# 🔐 Railway Environment Variables Template

## Required Environment Variables for Production Deployment

Copy these environment variables to your Railway project settings. Replace placeholder values with your actual production values.

### 🔒 Core Security Settings
```bash
# Django Security
SECRET_KEY=django-insecure-REPLACE-WITH-50-RANDOM-CHARACTERS-FOR-PRODUCTION
DEBUG=False
ALLOWED_HOSTS=your-project-name.railway.app,quantumtaskai.com,www.quantumtaskai.com
CSRF_TRUSTED_ORIGINS=https://your-project-name.railway.app,https://quantumtaskai.com,https://www.quantumtaskai.com
```

### 📧 Email Configuration (Gmail Example)
```bash
# Email Settings - Use Gmail App Password or SMTP service
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=Quantum Tasks AI <noreply@quantumtaskai.com>
```

### 💳 Stripe Payment Configuration
```bash
# Stripe - Use LIVE keys for production
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_endpoint_secret
```

### 🤖 N8N AI Agent Webhooks (External Server URLs)

⚠️ **IMPORTANT**: These URLs point to your SEPARATE N8N instance, NOT hosted on Railway with Django.

```bash
# N8N Webhook URLs - Replace with your actual N8N instance URLs
# Option A: N8N Cloud
N8N_WEBHOOK_DATA_ANALYZER=https://yourworkspace.app.n8n.cloud/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=https://yourworkspace.app.n8n.cloud/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=https://yourworkspace.app.n8n.cloud/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://yourworkspace.app.n8n.cloud/webhook/social-ads

# Option B: Self-hosted or separate Railway N8N project  
# N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n-server.com/webhook/data-analyzer
# N8N_WEBHOOK_FIVE_WHYS=https://your-n8n-server.com/webhook/five-whys
# N8N_WEBHOOK_JOB_POSTING=https://your-n8n-server.com/webhook/job-posting
# N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n-server.com/webhook/social-ads
```

### 🌤️ External API Keys
```bash
# OpenWeather API for Weather Agent
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### ⚡ Performance & Caching (Optional)
```bash
# Redis URL - Automatically set by Railway Redis service
# REDIS_URL=redis://default:password@host:port
```

---

## 🔍 Environment Variable Setup Instructions

### Step 1: Generate SECRET_KEY
Use Django to generate a secure secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 2: Gmail App Password Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account Settings → Security → App passwords
3. Generate an app password for "Django Email"
4. Use the 16-character app password (not your regular password)

### Step 3: Stripe Configuration
1. Login to your Stripe Dashboard
2. Go to Developers → API Keys
3. Copy your "Secret key" (starts with `sk_live_` for production)
4. Go to Developers → Webhooks
5. Create webhook endpoint: `https://your-domain.railway.app/wallet/stripe/webhook/`
6. Copy the webhook signing secret (starts with `whsec_`)

### Step 4: N8N Webhook URLs (Separate Server)

⚠️ **N8N RUNS SEPARATELY** from your Django app. Choose one hosting option:

**Option A: N8N Cloud (Easiest)**
1. Sign up at [n8n.cloud](https://n8n.cloud)
2. Import your workflow JSON files from agent directories
3. Configure OpenAI API credentials in N8N
4. Copy webhook URLs from each workflow
5. Add URLs to Railway environment variables

**Option B: Separate Railway Project for N8N**
1. Create a NEW Railway project (different from your Django app)
2. Deploy N8N using Railway's template or Docker
3. Import workflows and configure credentials
4. Copy webhook URLs and add to Django app environment

**Option C: Self-Hosted N8N**
1. Deploy N8N on DigitalOcean, AWS, VPS, or local server
2. Ensure server is publicly accessible for webhook calls
3. Import workflows and get webhook URLs
4. Ensure N8N workflows are active and accessible

### Step 5: OpenWeather API
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add it to the environment variables

---

## 🚫 Important Security Notes

### Never Include in Git:
- ❌ Real SECRET_KEY values
- ❌ Production API keys
- ❌ Email passwords
- ❌ Stripe live keys
- ❌ Database credentials

### Railway Automatic Variables:
Railway automatically provides these - **DO NOT SET MANUALLY**:
- `DATABASE_URL` (PostgreSQL connection string)
- `PORT` (Application port)
- `RAILWAY_*` (Railway-specific variables)

### Testing Configuration:
Use Railway's "Preview" deployments to test environment variables before going live.

---

## 📋 Environment Variable Checklist

Before deploying, verify you have set:

### Core Settings ✓
- [ ] `SECRET_KEY` (50+ random characters)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` (includes your Railway domain)
- [ ] `CSRF_TRUSTED_ORIGINS` (HTTPS URLs only)

### Email Configuration ✓
- [ ] `EMAIL_HOST_USER` (your Gmail address)
- [ ] `EMAIL_HOST_PASSWORD` (Gmail app password)
- [ ] `DEFAULT_FROM_EMAIL` (your sender email)

### Payment System ✓
- [ ] `STRIPE_SECRET_KEY` (live key for production)
- [ ] `STRIPE_WEBHOOK_SECRET` (webhook endpoint secret)

### AI Agents ✓
- [ ] All `N8N_WEBHOOK_*` URLs are accessible
- [ ] `OPENWEATHER_API_KEY` (for weather agent)

### External Services ✓
- [ ] PostgreSQL database added to Railway project
- [ ] Redis service added (optional but recommended)
- [ ] Custom domain configured (if applicable)

---

## 🔧 Advanced Configuration

### Production-Ready Gunicorn Settings
The `railway.json` includes optimized Gunicorn configuration:
- 2 workers (scales with CPU cores)
- 120-second timeout for AI processing
- Request recycling for memory management
- Health check integration

### Database Connection Pooling
Railway's PostgreSQL automatically handles connection pooling for optimal performance.

### Static Files & CDN
WhiteNoise configuration in your Django settings handles static file serving efficiently.

---

## 🎯 Environment Variable Testing

After setting variables in Railway:

1. **Deploy Application**: Railway will automatically deploy with new variables
2. **Check Health Endpoint**: `https://your-domain.railway.app/health/`
3. **Test Authentication**: Try user registration and login
4. **Verify Payments**: Test Stripe integration (use test cards)
5. **Check AI Agents**: Test each agent workflow
6. **Monitor Logs**: Watch Railway application logs for errors

---

## 🆘 Troubleshooting

### Common Issues:

**Secret Key Error:**
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty
```
→ Ensure SECRET_KEY is set and not empty

**Email Authentication Failed:**
```
SMTPAuthenticationError: Username and Password not accepted
```
→ Use Gmail App Password, not regular password

**Stripe Webhook Verification Failed:**
```
stripe.error.SignatureVerificationError
```
→ Verify webhook secret matches Stripe dashboard

**N8N Webhook Not Responding:**
```
requests.exceptions.ConnectionError
```
→ Ensure N8N instance is running and accessible

---

This template ensures your Quantum Tasks AI application runs securely and efficiently on Railway.app! 🚀