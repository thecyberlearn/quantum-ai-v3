# 🚨 Emergency Railway Startup Fix

## Issue: Service Unavailable (Django Not Starting)

We've regressed from 400 Bad Request (Django running) back to "service unavailable" (app not starting). This is likely an environment variable issue.

## 🔧 IMMEDIATE FIXES TO TRY

### Fix 1: Minimal Environment Variables
**Set ONLY these in Railway Variables:**
```bash
SECRET_KEY=your-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=*
```
**Remove all other variables temporarily**

### Fix 2: Check ALLOWED_HOSTS Syntax
**Bad (causes crash):**
```bash
ALLOWED_HOSTS=*.railway.app, quantumtaskai.com  # NO SPACES
ALLOWED_HOSTS="*.railway.app,quantumtaskai.com"  # NO QUOTES
```

**Good:**
```bash
ALLOWED_HOSTS=*.railway.app,quantumtaskai.com
# OR for debugging:
ALLOWED_HOSTS=*
```

### Fix 3: Generate New SECRET_KEY
**The SECRET_KEY might be invalid:**
```bash
# Generate new one:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set in Railway:
SECRET_KEY=django-insecure-your-new-key-here
```

## 🚀 Deployment Strategy

### Step 1: Minimal railway.json (DONE)
- Removed health check
- Removed collectstatic
- Bare minimum startup

### Step 2: Set Minimal Variables
```bash
SECRET_KEY=your-generated-key
DEBUG=False  
ALLOWED_HOSTS=*
```

### Step 3: Deploy and Test
```bash
git add .
git commit -m "Emergency fix - minimal config"
git push origin main
```

### Step 4: Check Direct Access
```bash
# Once deployed, test direct access:
curl https://your-railway-domain.railway.app/
# Should return HTML page, not connection error
```

## 🔍 Debug Commands

### Check Railway Logs
```bash
railway logs --tail 50
```

**Look for these errors:**
- `ImproperlyConfigured: The SECRET_KEY setting must not be empty`
- `ImproperlyConfigured: You must set settings.ALLOWED_HOSTS`
- `ModuleNotFoundError`
- `ImportError`
- `Address already in use`

### Check Variables
```bash
railway variables
```

## 📊 Success Indicators

### ✅ App Starting
- Railway logs show: `Starting gunicorn`
- No Python errors in logs
- Direct URL access works (returns HTML)

### ✅ Ready for Health Check
Once basic startup works, we can add back:
```json
{
  "deploy": {
    "startCommand": "gunicorn netcop_hub.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health/",
    "healthcheckTimeout": 30
  }
}
```

## 🎯 Goal
Get back to where Django was at least starting (even with 400 error), then fix the ALLOWED_HOSTS properly.

**The issue is likely in environment variable syntax or SECRET_KEY format.**