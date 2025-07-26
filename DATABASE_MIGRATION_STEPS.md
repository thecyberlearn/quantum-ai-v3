# 🗄️ Database Migration Steps

## Current Issue
Database is not migrated because we removed migrations from railway.json startup to fix startup issues.

## Step-by-Step Migration Process

### Step 1: Ensure DATABASE_URL is Set
1. Go to Railway project → **Variables**
2. Add if not exists:
   ```
   DATABASE_URL = ${{ Postgres.DATABASE_URL }}
   ```
3. Wait for Railway to redeploy (30-60 seconds)

### Step 2: Test Database Connection
```bash
# Test if Django can connect to database
railway run python manage.py check

# Check database specifically
railway run python manage.py check --database default
```

### Step 3: Run Migrations Manually
```bash
# Run all pending migrations
railway run python manage.py migrate

# If that fails, try step by step:
railway run python manage.py migrate --run-syncdb
```

### Step 4: Populate Initial Data
```bash
# Create superuser (optional)
railway run python manage.py createsuperuser

# Populate agents
railway run python manage.py populate_agents
```

### Step 5: Use Our Setup Command (Recommended)
```bash
# This does everything automatically with retries
railway run python manage.py setup_database
```

## Expected Output

### Successful Migration:
```
Operations to perform:
  Apply all migrations: admin, agent_base, auth, authentication, contenttypes, core, data_analyzer, email_writer, five_whys_analyzer, job_posting_generator, sessions, social_ads_generator, wallet, weather_reporter
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying authentication.0004_user_email_verified_emailverificationtoken... OK
```

### Successful Agent Population:
```
Creating default agents...
Updated: Weather Reporter
Updated: Data Analyzer
Updated: Job Posting Generator
Updated: Social Ads Generator
Updated: 5 Whys Analysis Agent
Successfully processed 5 agents: 0 created, 5 updated
```

## Troubleshooting

### Error: "No module named 'psycopg2'"
**Cause**: PostgreSQL driver not installed
**Fix**: Already in requirements.txt, should be available

### Error: "Connection refused"
**Cause**: DATABASE_URL not set or PostgreSQL service not running
**Fix**: 
1. Check Railway PostgreSQL service is active
2. Verify DATABASE_URL variable is set
3. Wait a few minutes for services to start

### Error: "relation already exists"
**Cause**: Some tables already exist
**Fix**: 
```bash
railway run python manage.py migrate --fake-initial
```

### Error: "permission denied"
**Cause**: Database user doesn't have permissions
**Fix**: Railway PostgreSQL should have full permissions by default

## Quick Fix Commands

### If Migration Fails:
```bash
# Reset migrations (dangerous - only if needed)
railway run python manage.py migrate --fake-initial

# Or try individual apps:
railway run python manage.py migrate auth
railway run python manage.py migrate authentication
railway run python manage.py migrate agent_base
```

### If Agents Don't Populate:
```bash
# Check if command exists
railway run python manage.py help populate_agents

# Run manually
railway run python manage.py shell
# Then in shell:
from agent_base.management.commands.populate_agents import Command
cmd = Command()
cmd.handle()
```

## Verification

### Check Database Tables:
```bash
railway run python manage.py dbshell
# In database shell:
\dt  # List all tables
\q   # Quit
```

### Test Health Endpoint:
```bash
curl https://your-railway-domain.railway.app/health/
```

Should return database as "healthy" instead of "warning".

## Next Steps After Migration

1. **Add health check back** to railway.json
2. **Test all AI agents** work correctly
3. **Verify user registration** and payments work
4. **Check admin panel** functionality

Run the migrations and let me know what output you get! 🚀