# 🔄 Domain Change Guide

This guide provides step-by-step instructions for changing the domain of your Quantum Tasks AI application.

## 📋 Overview

When changing domains, you need to update several configuration files and environment variables to ensure:
- ✅ Email verification links work correctly
- ✅ Password reset links work correctly
- ✅ Admin URLs are correct
- ✅ CSRF protection works
- ✅ SSL certificates are properly configured

## 🎯 Quick Reference

**Current Domain:** `quantum-ai.up.railway.app`  
**Files That Need Updates:** 6 files  
**Estimated Time:** 15-30 minutes  

---

## 📍 Files That Reference Domains

### 1. Environment Configuration
- **Local Development:** `.env` (if exists)
- **Railway Production:** Environment variables in Railway dashboard

### 2. Django Settings
- `netcop_hub/settings.py` - SITE_URL configuration

### 3. Management Commands (Display Only)
- `core/management/commands/check_admin.py` - Admin URL in output
- `core/management/commands/reset_admin.py` - Admin URL in output

### 4. Documentation Files
- Various documentation files with example URLs

---

## 🚀 Step-by-Step Domain Change Process

### Step 1: Pre-Change Preparation

**📋 Checklist:**
- [ ] Have new domain ready and configured in DNS
- [ ] Have Railway admin access
- [ ] Have backup of current environment variables
- [ ] Note current domain for rollback if needed

**🔍 Current Domain Detection:**
```bash
# Check current configuration
grep -r "quantum-ai.up.railway.app" . --exclude-dir=.git
```

### Step 2: Update Railway Environment Variables

**🌐 Railway Dashboard Steps:**
1. Go to [railway.app](https://railway.app) and select your project
2. Navigate to **Variables** tab
3. Update these environment variables:

```env
# Update this variable
SITE_URL=https://your-new-domain.com

# Optional: If using custom Railway domain
RAILWAY_PUBLIC_DOMAIN=your-new-domain.com

# Update allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1,testserver,your-new-domain.com,quantumtaskai.com

# Update CSRF trusted origins
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://your-new-domain.com,https://quantumtaskai.com
```

### Step 3: Update Django Settings (If Needed)

**📝 File:** `netcop_hub/settings.py`

Most domain changes only require environment variable updates. However, if you need to update the hardcoded fallback:

```python
# Around line 60, update the hardcoded fallback domain:
if config('RAILWAY_ENVIRONMENT', default=''):
    # Use actual Railway domain for email verification links
    SITE_URL = 'https://your-new-domain.com'  # Update this line
else:
    SITE_URL = config('SITE_URL', default='http://localhost:8000')
```

### Step 4: Update Management Commands (Optional)

If you want to update the hardcoded URLs in management command outputs:

**📝 File:** `core/management/commands/check_admin.py`
```python
# Around line 53, update:
self.stdout.write(f"URL: https://your-new-domain.com/admin/")
```

**📝 File:** `core/management/commands/reset_admin.py`
```python
# Around line 69, update:
self.stdout.write("URL: https://your-new-domain.com/admin/")
```

### Step 5: DNS & Railway Configuration

**🌐 DNS Setup:**
1. Point your domain to Railway:
   - Add CNAME record: `your-domain.com` → `your-app.up.railway.app`
   - Or follow Railway's custom domain setup guide

**⚙️ Railway Domain Setup:**
1. In Railway dashboard, go to **Settings** > **Domains**
2. Add your custom domain
3. Follow Railway's verification steps
4. Wait for SSL certificate provisioning (5-10 minutes)

### Step 6: Deploy Changes

**🚀 Deployment Options:**

**Option A: Automatic Deployment (Recommended)**
- Railway auto-deploys when environment variables change
- Monitor the deployment in Railway dashboard

**Option B: Manual Git Deploy**
```bash
# If you made code changes, commit and push
git add .
git commit -m "🔧 Update domain configuration to your-new-domain.com"
git push
```

### Step 7: Testing & Verification

**🧪 Test Checklist:**

**Basic Functionality:**
- [ ] Application loads at new domain
- [ ] Admin panel works: `https://your-new-domain.com/admin/`
- [ ] User registration works
- [ ] Login/logout works

**Email Functionality:**
- [ ] Register new test user
- [ ] Check email verification link points to new domain
- [ ] Test password reset email link
- [ ] Test resend verification email

**Agent Functionality:**
- [ ] Test agent marketplace: `https://your-new-domain.com/marketplace/`
- [ ] Test individual agents work
- [ ] Test wallet functionality

**Command Verification:**
```bash
# Test admin command shows new URL
python manage.py check_admin

# Test health check
curl https://your-new-domain.com/health/
```

---

## 🔧 Local Development Domain Changes

For local development, update your `.env` file:

```env
# Update these in your local .env file
SITE_URL=http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1,testserver,your-new-domain.com
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://your-new-domain.com
```

---

## 🆘 Troubleshooting

### Common Issues & Solutions

**🚫 CSRF Verification Failed**
```bash
# Solution: Update CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS=https://your-new-domain.com,https://quantumtaskai.com
```

**📧 Email Links Point to Old Domain**
```bash
# Solution: Update SITE_URL environment variable
SITE_URL=https://your-new-domain.com
```

**🔒 SSL Certificate Issues**
- Wait 5-10 minutes for Railway to provision SSL certificate
- Check Railway dashboard for SSL status
- Ensure DNS propagation is complete

**🌐 DNS Not Resolving**
```bash
# Check DNS propagation
nslookup your-new-domain.com
dig your-new-domain.com
```

### Rollback Process

If something goes wrong, quickly rollback:

1. **Revert Environment Variables:**
   ```env
   SITE_URL=https://quantum-ai.up.railway.app
   ALLOWED_HOSTS=localhost,127.0.0.1,testserver,quantum-ai.up.railway.app,quantumtaskai.com
   ```

2. **Revert Code Changes (if any):**
   ```bash
   git revert HEAD
   git push
   ```

---

## 📚 Related Documentation

- [Railway Deployment Guide](./railway-deployment.md)
- [Environment Variables](./environment-variables.md)
- [Troubleshooting Guide](../operations/troubleshooting.md)

---

## ✅ Post-Change Checklist

After successful domain change:

- [ ] Update documentation with new domain examples
- [ ] Update any external integrations (N8N webhooks, Stripe, etc.)
- [ ] Notify users of domain change (if applicable)
- [ ] Update bookmarks and saved links
- [ ] Monitor error logs for any domain-related issues
- [ ] Update README or other project documentation

---

**🎉 Congratulations!** Your domain change is complete. The system is now fully configured for your new domain with all email links, admin URLs, and security settings updated automatically.