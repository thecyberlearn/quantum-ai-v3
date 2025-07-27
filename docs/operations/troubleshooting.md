# 🔧 Troubleshooting Guide

Common issues and solutions for Quantum Tasks AI platform.

## 🚨 Emergency Quick Fixes

### Application Won't Start
```bash
# 1. Check system health
python manage.py check --deploy

# 2. Test database connection
python manage.py check_db

# 3. Verify environment variables
python manage.py shell -c "from django.conf import settings; print('SECRET_KEY set:', bool(settings.SECRET_KEY))"

# 4. Check logs
railway logs  # For Railway deployment
```

### Health Check Failing
```bash
# Test health endpoint
curl http://localhost:8000/health/
curl https://quantum-ai.up.railway.app/health/

# Expected healthy response:
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "agents": {"status": "healthy", "active_count": 7}
  }
}
```

---

## 🌐 Domain & URL Issues

### CSRF Verification Failed
**Error:** `CSRF verification failed. Request aborted.`

**Solutions:**
```bash
# 1. Update CSRF trusted origins
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://quantumtaskai.com

# 2. Check allowed hosts
ALLOWED_HOSTS=your-domain.com,quantumtaskai.com,localhost

# 3. Clear browser cache and cookies
# 4. Verify HTTPS vs HTTP in origins
```

### Email Links Wrong Domain
**Issue:** Email verification/reset links point to wrong domain

**Solutions:**
```bash
# 1. Update SITE_URL environment variable
SITE_URL=https://your-correct-domain.com

# 2. Check Railway environment variables
railway variables

# 3. Follow domain change guide
# See: docs/deployment/domain-change-guide.md
```

### Page Not Found (404)
**Error:** `Page not found` for admin or other pages

**Solutions:**
```bash
# 1. Check URL patterns
python manage.py show_urls

# 2. Verify static files
python manage.py collectstatic --noinput

# 3. Check ALLOWED_HOSTS setting
# 4. Test with trailing slash: /admin/
```

---

## 🗄️ Database Issues

### Database Connection Failed
**Error:** `FATAL: database "railway" does not exist`

**Solutions:**
```bash
# 1. Verify Railway PostgreSQL service is running
# Check Railway dashboard

# 2. Test DATABASE_URL
python manage.py dbshell

# 3. Check environment variable
echo $DATABASE_URL

# 4. Recreate PostgreSQL service if needed
```

### Migration Errors
**Error:** `Migration conflicts` or `Table already exists`

**Solutions:**
```bash
# 1. Check migration status
python manage.py showmigrations

# 2. Fake initial migration (if safe)
python manage.py migrate --fake-initial

# 3. Reset migrations (development only)
python manage.py reset_database

# 4. Manual migration fix
python manage.py migrate --fake app_name 0001
python manage.py migrate app_name
```

### Slow Database Performance
**Issues:** Slow queries, timeouts

**Solutions:**
```python
# 1. Check connection pooling (Railway auto-configured)
DATABASES['default']['CONN_MAX_AGE'] = 600

# 2. Add database indexes (if needed)
python manage.py dbshell
# Run EXPLAIN ANALYZE on slow queries

# 3. Monitor Railway metrics
# Check Railway dashboard → Metrics
```

---

## 📧 Email Issues

### Email Not Sending
**Error:** `SMTPAuthenticationError` or emails not received

**Solutions:**
```bash
# 1. Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])

# 2. Check Gmail App Password (not regular password)
EMAIL_HOST_PASSWORD=your-16-character-app-password

# 3. Verify email backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# 4. Check spam folder
# 5. Verify sender domain reputation
```

### Email Templates Broken
**Issue:** Email formatting issues or missing content

**Solutions:**
```bash
# 1. Check email template syntax
# Verify: authentication/views.py email templates

# 2. Test with console backend
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# 3. Check SITE_URL for links
SITE_URL=https://your-correct-domain.com
```

---

## 💳 Payment Issues

### Stripe Integration Failed
**Error:** `InvalidRequestError` or payment not processing

**Solutions:**
```bash
# 1. Verify Stripe keys
STRIPE_SECRET_KEY=sk_test_... # for test
STRIPE_SECRET_KEY=sk_live_... # for production

# 2. Check webhook endpoint
# Stripe Dashboard → Webhooks
# URL: https://your-domain.com/wallet/stripe/webhook/

# 3. Test webhook secret
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# 4. Check Railway logs for Stripe errors
railway logs | grep stripe
```

### Wallet Balance Issues
**Issue:** Incorrect balance or transaction not recorded

**Solutions:**
```python
# 1. Check transaction history
python manage.py shell
>>> from authentication.models import User
>>> user = User.objects.get(email='user@example.com')
>>> user.wallet_transactions.all()

# 2. Verify Stripe webhook events
# Check Stripe Dashboard → Events

# 3. Manual balance correction (if needed)
>>> user.wallet_balance = 100.00
>>> user.save()
```

---

## 🤖 Agent Issues

### Webhook Agent Not Working
**Error:** Agent returns error or times out

**Solutions:**
```bash
# 1. Check N8N webhook URL
curl -X POST https://your-n8n-instance.com/webhook/test

# 2. Verify N8N environment variables
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n-instance.com/webhook/data-analyzer

# 3. Test N8N workflow directly
# Visit N8N dashboard and test workflow

# 4. Check agent processor code
# See: individual agent processor.py files
```

### API Agent Not Working
**Error:** Weather agent or other API agents failing

**Solutions:**
```bash
# 1. Check API key
OPENWEATHER_API_KEY=your_api_key

# 2. Test API directly
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# 3. Check rate limits
# Most APIs have rate limiting

# 4. Verify API endpoint URLs
```

### File Upload Issues
**Error:** File upload fails or files not processed

**Solutions:**
```bash
# 1. Check media directory permissions
ls -la media/uploads/

# 2. Verify file size limits
# Django default: 2.5MB

# 3. Check disk space (Railway)
# Monitor Railway dashboard

# 4. Clean up old files
python manage.py cleanup_uploads
```

---

## 🚀 Deployment Issues

### Railway Build Failed
**Error:** Build fails during deployment

**Solutions:**
```bash
# 1. Check Railway build logs
railway logs --deployment

# 2. Verify requirements.txt
pip freeze > requirements.txt

# 3. Check Python version
# Ensure compatible with Railway

# 4. Verify railway.json
{
  "build": {"builder": "nixpacks"},
  "deploy": {"startCommand": "gunicorn netcop_hub.wsgi:application"}
}
```

### Environment Variables Missing
**Error:** Settings errors in production

**Solutions:**
```bash
# 1. List current variables
railway variables

# 2. Add missing variables
railway variables set SECRET_KEY=your-secret-key

# 3. Verify environment template
# See: docs/deployment/environment-variables.md

# 4. Check variable spelling and format
```

### SSL Certificate Issues
**Error:** HTTPS not working or certificate errors

**Solutions:**
```bash
# 1. Wait for Railway SSL provisioning (5-10 minutes)

# 2. Check custom domain configuration
# Railway Dashboard → Settings → Domains

# 3. Verify DNS settings
nslookup your-domain.com
dig your-domain.com

# 4. Check HTTPS redirect settings
SECURE_SSL_REDIRECT=True  # for production
```

---

## 🔍 Debugging Tools

### Django Debug Information
```bash
# Check configuration
python manage.py check --deploy

# Database information
python manage.py dbshell

# Shell access
python manage.py shell

# Show URLs
python manage.py show_urls

# Migration status
python manage.py showmigrations
```

### Railway Debugging
```bash
# View logs
railway logs

# Live log streaming
railway logs --follow

# Variable management
railway variables
railway variables set KEY=value

# Service information
railway status
```

### Network Debugging
```bash
# Test connectivity
curl -I https://your-domain.com

# Check DNS
nslookup your-domain.com
dig your-domain.com

# Test specific endpoints
curl https://your-domain.com/health/
curl https://your-domain.com/admin/
```

---

## 📊 Performance Issues

### Slow Page Load
**Solutions:**
```python
# 1. Enable debug toolbar (development)
INSTALLED_APPS += ['debug_toolbar']

# 2. Check database queries
# Use Django Debug Toolbar to identify N+1 queries

# 3. Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['created_at']),
        models.Index(fields=['user', 'status']),
    ]

# 4. Use select_related and prefetch_related
User.objects.select_related('profile').all()
```

### High Memory Usage
**Solutions:**
```bash
# 1. Monitor Railway metrics
# Check Railway Dashboard → Metrics

# 2. Optimize queries
# Avoid loading large datasets

# 3. Use pagination
from django.core.paginator import Paginator

# 4. Check for memory leaks
# Monitor long-running processes
```

---

## 🆘 Getting More Help

### Log Analysis
```bash
# Railway logs with filtering
railway logs | grep ERROR
railway logs | grep "500"

# Django logging
# Check netcop.log file (if configured)

# Browser developer tools
# Check Network tab for failed requests
# Check Console for JavaScript errors
```

### Testing Procedures
```bash
# Health check first
curl https://your-domain.com/health/

# Test authentication
curl -c cookies.txt -b cookies.txt https://your-domain.com/auth/login/

# Test API endpoints
curl https://your-domain.com/api/agents/

# Test static files
curl https://your-domain.com/static/css/base.css
```

### Escalation Steps
1. **Check this troubleshooting guide**
2. **Review relevant documentation in `/docs/`**
3. **Check Railway service status**
4. **Test in local development environment**
5. **Review recent code changes**
6. **Check external service status (Stripe, N8N, email provider)**

---

## 📚 Related Documentation

- [Environment Variables](../deployment/environment-variables.md) - Configuration reference
- [Railway Deployment](../deployment/railway-deployment.md) - Deployment guide
- [Domain Change Guide](../deployment/domain-change-guide.md) - Domain configuration
- [Database Management](./database-management.md) - Database operations

---

**💡 Pro Tip:** Most issues are environment variable or configuration problems. Always check the basics first: SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS, and CSRF_TRUSTED_ORIGINS.