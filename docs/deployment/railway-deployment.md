# 🚀 Railway.app Deployment Guide

Complete guide for deploying Quantum Tasks AI to Railway.app with PostgreSQL database and Redis cache.

## 📋 Overview

**What Deploys to Railway:**
- ✅ Django Application (Quantum Tasks AI)
- ✅ PostgreSQL Database (automatic)
- ✅ Redis Cache (optional but recommended)

**External Dependencies:**
- ❌ N8N Instance (runs on separate server - see N8N section)
- ❌ N8N Workflows (hosted elsewhere)

**Architecture:**
```
Railway Django App → HTTP POST → N8N Instance (Separate) → AI Processing → Response → Railway Django App
```

---

## 🛠️ Pre-Deployment Setup

### Required Accounts
- [ ] **GitHub** account with repository access
- [ ] **Railway.app** account ([railway.app](https://railway.app))
- [ ] **Stripe** account for payments (test/live keys)
- [ ] **Email Service** (Gmail SMTP or similar)
- [ ] **N8N Instance** for AI agent webhooks (separate hosting)

### Repository Verification
- [ ] Latest code pushed to GitHub
- [ ] All Django migrations created and committed
- [ ] `railway.json` file present in root directory
- [ ] Environment variables documented in `.env.example`

---

## 🚀 Deployment Steps

### Step 1: Create Railway Project

1. **Connect Repository:**
   - Visit [railway.app](https://railway.app) and login
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Select your `quantum_ai` repository
   - Railway auto-detects Django and starts building

2. **Add Database:**
   - In your Railway project dashboard
   - Click **"New Service"** → **"Database"** → **"PostgreSQL"**
   - Railway automatically configures `DATABASE_URL`

3. **Add Redis (Optional):**
   - Click **"New Service"** → **"Database"** → **"Redis"**
   - Railway automatically configures `REDIS_URL`

### Step 2: Configure Environment Variables

Navigate to **Variables** tab in Railway dashboard and add:

#### 🔐 Core Django Settings
```env
SECRET_KEY=your-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=quantum-ai.up.railway.app,quantumtaskai.com,localhost
CSRF_TRUSTED_ORIGINS=https://quantum-ai.up.railway.app,https://quantumtaskai.com
```

#### 📧 Email Configuration
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Quantum Tasks AI <your-email@gmail.com>
```

#### 💳 Stripe Payment Settings
```env
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

#### 🔗 N8N Webhook URLs
```env
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n-instance.com/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=https://your-n8n-instance.com/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=https://your-n8n-instance.com/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n-instance.com/webhook/social-ads
N8N_WEBHOOK_FAQ_GENERATOR=https://your-n8n-instance.com/webhook/faq-generator
```

#### 🌤️ External API Keys
```env
OPENWEATHER_API_KEY=your_openweather_api_key
```

### Step 3: Deploy & Test

1. **Automatic Deployment:**
   - Railway deploys automatically after environment variables are set
   - Monitor deployment logs in Railway dashboard
   - Wait for deployment to complete (2-5 minutes)

2. **Test Deployment:**
   ```bash
   # Test application access
   curl https://quantum-ai.up.railway.app/
   
   # Test health endpoint
   curl https://quantum-ai.up.railway.app/health/
   
   # Expected health response
   {
     "status": "healthy",
     "checks": {
       "database": {"status": "healthy"},
       "agents": {"status": "healthy", "active_count": 7}
     }
   }
   ```

---

## 🎯 Post-Deployment Setup

### Create Admin User

```bash
# Use Railway CLI or dashboard console
railway run python manage.py check_admin
```

**Or create manually via Django shell:**
```python
# In Railway console
python manage.py shell

# Create superuser
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_superuser(
    username='admin',
    email='admin@quantumtaskai.com',
    password='YourSecurePassword123!'
)
user.add_balance(100, "Initial admin balance")
```

### Test Key Features

**🌐 Website Access:**
- Homepage: `https://quantum-ai.up.railway.app/`
- Marketplace: `https://quantum-ai.up.railway.app/marketplace/`
- Admin: `https://quantum-ai.up.railway.app/admin/`

**🧪 User Registration Flow:**
1. Register new user: `https://quantum-ai.up.railway.app/auth/register/`
2. Check email verification works
3. Test login functionality
4. Test wallet top-up

**🤖 Agent Functionality:**
1. Test individual agents work
2. Verify N8N webhook connections
3. Test file uploads and processing

---

## 🔧 Railway Configuration

### Custom Domain Setup

1. **In Railway Dashboard:**
   - Go to **Settings** → **Domains**
   - Click **"Custom Domain"**
   - Enter your domain (e.g., `app.yourcompany.com`)
   - Follow DNS verification steps

2. **DNS Configuration:**
   ```
   Type: CNAME
   Name: app (or @)
   Value: quantum-ai.up.railway.app
   ```

3. **Update Environment Variables:**
   ```env
   ALLOWED_HOSTS=app.yourcompany.com,quantum-ai.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://app.yourcompany.com,https://quantum-ai.up.railway.app
   ```

### Scaling Configuration

**In `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "gunicorn netcop_hub.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 60",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🔌 N8N Webhook Integration

### N8N Setup Requirements

**N8N must be hosted separately** (N8N Cloud, separate Railway project, or self-hosted):

1. **N8N Cloud (Recommended):**
   - Sign up at [n8n.cloud](https://n8n.cloud)
   - Import workflow files from `*/n8n_workflows/` directories
   - Configure webhook URLs in Railway environment

2. **Self-Hosted N8N:**
   - Deploy N8N to separate server/service
   - Import workflows using `manage_n8n_workflows.py`
   - Ensure webhooks are publicly accessible

### Workflow Management

```bash
# List all available workflows
python manage_n8n_workflows.py list

# Import specific agent workflow
python manage_n8n_workflows.py import data_analyzer

# Deploy all workflows
./deploy_n8n_workflows.sh
```

---

## 🆘 Troubleshooting

### Common Deployment Issues

**🚫 Build Failures:**
```bash
# Check Railway logs
railway logs

# Common fixes:
# 1. Ensure requirements.txt is complete
# 2. Check Python version compatibility
# 3. Verify Django settings are correct
```

**🔗 Database Connection Issues:**
```bash
# Verify DATABASE_URL is set correctly
railway variables

# Test database connection
railway run python manage.py check --database default
```

**📧 Email Not Working:**
```bash
# Test email configuration
railway run python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

**🌐 Domain/CSRF Issues:**
```env
# Ensure these match your actual domain
ALLOWED_HOSTS=your-actual-domain.com
CSRF_TRUSTED_ORIGINS=https://your-actual-domain.com
```

### Performance Optimization

**Database Connection Pooling:**
- Railway automatically optimizes PostgreSQL connections
- Connection pooling configured in `settings.py`

**Static Files:**
- WhiteNoise serves static files efficiently
- No additional CDN needed for small applications

**Monitoring:**
- Use Railway dashboard for logs and metrics
- Health check endpoint: `/health/`

---

## 📚 Related Documentation

- [Domain Change Guide](./domain-change-guide.md)
- [Environment Variables](./environment-variables.md)
- [Database Management](../operations/database-management.md)
- [Troubleshooting Guide](../operations/troubleshooting.md)

---

## ✅ Deployment Checklist

**Pre-Deployment:**
- [ ] Repository connected to Railway
- [ ] PostgreSQL database added
- [ ] All environment variables configured
- [ ] N8N instance set up separately

**Post-Deployment:**
- [ ] Application loads successfully
- [ ] Health check passes
- [ ] Admin user created
- [ ] Email verification works
- [ ] Payment processing works
- [ ] Agent functionality works
- [ ] Custom domain configured (if needed)

**🎉 Your Quantum Tasks AI application is now live on Railway!**