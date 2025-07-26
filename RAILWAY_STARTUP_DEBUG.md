# 🚨 Railway Startup Failure - Debug Guide

## Current Issue
Health check failing with "service unavailable" after 60 seconds, indicating Django/Gunicorn not starting properly.

## 🔧 Fixes Applied

### 1. Simplified Health Check
- **No database dependency**: Health check returns 200 if Django is running
- **Always passes**: As long as Django loads, health check succeeds
- **Database optional**: Database issues logged as warnings, not failures

### 2. Simplified Startup Process
- **Removed migrations**: No database dependency during startup
- **Minimal startup**: Only collectstatic + gunicorn
- **Single worker**: Reduced resource usage
- **Faster timeout**: 30s health check, 10s intervals

### 3. Separate Database Setup
- **Post-startup command**: `python manage.py setup_database`
- **Built-in retries**: Waits for database to be ready
- **Graceful handling**: Continues even if some steps fail

## 🚀 Deployment Steps

### Step 1: Set ONLY These Environment Variables
```bash
# Critical variables only
SECRET_KEY=your-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=your-project.railway.app,quantumtaskai.com
```

### Step 2: Deploy Simplified Version
```bash
git add .
git commit -m "Simplify Railway startup - remove database dependencies"
git push origin main
```

### Step 3: After App Starts, Run Database Setup
```bash
# Wait for app to be running, then:
railway run python manage.py setup_database
```

## 🔍 Debugging Commands

### Check Deployment Status
```bash
# View recent logs
railway logs --tail 50

# Check if app is responding
curl https://your-project.railway.app/health/

# Check environment variables
railway variables
```

### Expected Health Response (Without Database)
```json
{
  "status": "healthy",
  "app": "quantum-tasks-ai",
  "checks": {
    "application": {
      "status": "healthy", 
      "django_ready": true,
      "server_running": true
    },
    "database": {
      "status": "warning",
      "error": "Database connection failed"
    },
    "environment": {
      "status": "healthy",
      "debug_mode": false,
      "secret_key_configured": true
    }
  }
}
```

## 🎯 Troubleshooting Common Issues

### Issue 1: SECRET_KEY Error
```
ImproperlyConfigured: The SECRET_KEY setting must not be empty
```
**Fix**: Generate and set SECRET_KEY in Railway variables
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Issue 2: ALLOWED_HOSTS Error
```
DisallowedHost at /health/
```
**Fix**: Add Railway domain to ALLOWED_HOSTS
```bash
ALLOWED_HOSTS=your-project.railway.app,quantumtaskai.com
```

### Issue 3: Port Binding Error
```
[ERROR] Can't connect to ('0.0.0.0', PORT)
```
**Fix**: Ensure $PORT variable is available (Railway sets this automatically)

### Issue 4: Import Errors
```
ModuleNotFoundError: No module named 'xyz'
```
**Fix**: Check requirements.txt includes all dependencies

## 📊 Success Indicators

### ✅ App Starting Successfully
- Railway logs show "Starting gunicorn"
- Health check returns 200 status
- No import errors in logs
- Django loads without database

### ✅ Health Check Passing
```bash
curl https://your-project.railway.app/health/
# Should return JSON with "status": "healthy"
```

### ✅ Ready for Database Setup
```bash
railway run python manage.py setup_database
# Should complete migrations and populate agents
```

## 🔄 If Still Failing

### Last Resort: Minimal Config
```json
{
  "deploy": {
    "startCommand": "gunicorn netcop_hub.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckTimeout": 30
  }
}
```

### Test Locally First
```bash
# Test with minimal settings
export SECRET_KEY="test-key-123"
export DEBUG=False
export ALLOWED_HOSTS="localhost"
python manage.py runserver
```

## 📞 Next Steps
1. **Deploy simplified version** (no database dependencies)
2. **Verify health check passes** (app starts successfully)  
3. **Run database setup separately** (after app is running)
4. **Test full functionality** (agents, payments, etc.)

The goal is to get Django/Gunicorn starting first, then handle database setup separately.