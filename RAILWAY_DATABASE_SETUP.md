# 🗄️ Railway PostgreSQL Database Setup

## Current Status
✅ Django settings.py is already configured to use Railway PostgreSQL  
✅ Django app is starting successfully  
❌ Need to set DATABASE_URL environment variable

## Step-by-Step Railway Database Configuration

### Step 1: Ensure PostgreSQL Service is Added
1. Go to your Railway project dashboard
2. Click "Add Service" → "Database" → "PostgreSQL"
3. Wait for PostgreSQL service to deploy (shows green/active status)

### Step 2: Set DATABASE_URL Environment Variable
1. Go to your Railway project → **Variables** tab
2. Click "**Add Variable**"
3. Set:
   - **Name**: `DATABASE_URL`
   - **Value**: `${{ Postgres.DATABASE_URL }}`

### Step 3: Verify Variable Resolution
Railway will automatically resolve `${{ Postgres.DATABASE_URL }}` to the actual PostgreSQL connection string:
```
postgresql://postgres:password@hostname:5432/railway
```

### Step 4: Deploy Changes
Since you're updating environment variables, Railway will automatically redeploy your app.

## How Django Will Use This

### Your Current Settings (Already Perfect)
```python
# In settings.py - already configured correctly
database_url = config('DATABASE_URL', default='')

if database_url:
    # Parse Railway PostgreSQL URL
    DATABASES = {
        'default': dj_database_url.parse(database_url, conn_max_age=600)
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', ...}}
```

### What Happens After Setup
1. **Railway resolves variable**: `${{ Postgres.DATABASE_URL }}` → actual connection string
2. **Django reads DATABASE_URL**: From environment variables
3. **dj_database_url parses**: Converts URL to Django database config
4. **Connection pooling**: `conn_max_age=600` keeps connections alive

## Testing Database Connection

### After Railway Deployment
```bash
# Test database connection
railway run python manage.py check_db

# Run migrations and setup
railway run python manage.py setup_database

# Or manually:
railway run python manage.py migrate
railway run python manage.py populate_agents
```

### Expected Success Output
```
Database connection successful!
Running database migrations...
Migrations completed successfully!
Populating agents...
Agents populated successfully!
Database setup completed!
```

## Troubleshooting

### Issue: Database Connection Failed
**Cause**: PostgreSQL service not running or DATABASE_URL not set
**Fix**: Ensure PostgreSQL service is active and DATABASE_URL variable is set

### Issue: No Such Table Errors
**Cause**: Migrations haven't been run
**Fix**: Run `railway run python manage.py setup_database`

### Issue: Permission Denied
**Cause**: Database user permissions
**Fix**: Railway PostgreSQL should have full permissions by default

## Verification Steps

### 1. Check Railway Dashboard
- ✅ PostgreSQL service shows "Active"
- ✅ DATABASE_URL variable exists
- ✅ App deployment successful

### 2. Test Health Endpoint
```bash
curl https://your-railway-domain.railway.app/health/
```
**Expected response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "agents": {"status": "healthy", "active_count": 6}
  }
}
```

### 3. Test Application Access
- Visit Railway domain in browser
- Should show homepage without database errors
- All 6 AI agents should be accessible

## Summary
Your Django code is already perfectly configured for Railway PostgreSQL. You just need to:

1. **Add PostgreSQL service** (if not already added)
2. **Set DATABASE_URL = ${{ Postgres.DATABASE_URL }}** in Railway variables
3. **Run database setup** after deployment

That's it! 🚀