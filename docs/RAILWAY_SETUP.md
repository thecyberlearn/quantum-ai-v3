# Railway Deployment Setup Guide

## Current Issue: SQLite Database (Ephemeral)

Your Railway deployment is currently using SQLite, which is **ephemeral** and loses all data on every deployment. This is why your users disappear.

## Solution: Add PostgreSQL Database

### Step 1: Add PostgreSQL to Railway Project

1. **Go to your Railway project dashboard**
2. **Click "New" → "Database" → "Add PostgreSQL"**
3. **Railway will automatically create a PostgreSQL database**
4. **Railway will automatically set the `DATABASE_URL` environment variable**

### Step 2: Verify Environment Variables

After adding PostgreSQL, check that these environment variables are set in Railway:

**Required Variables:**
- `DATABASE_URL` - Should be automatically set by Railway PostgreSQL addon
- `SECRET_KEY` - Set to a secure random string
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Set to `netcop.up.railway.app,*.railway.app`
- `CSRF_TRUSTED_ORIGINS` - Set to `https://netcop.up.railway.app`

**API Keys:**
- `OPENWEATHER_API_KEY` - Your OpenWeather API key
- `STRIPE_SECRET_KEY` - Your Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Your Stripe webhook secret
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` - Your Stripe publishable key

**Webhook URLs:**
- `N8N_WEBHOOK_DATA_ANALYZER` - Your N8N webhook URL
- `N8N_WEBHOOK_JOB_POSTING` - Your N8N webhook URL  
- `N8N_WEBHOOK_SOCIAL_ADS` - Your N8N webhook URL

### Step 3: Deploy with PostgreSQL

Once PostgreSQL is added:

1. **Your next deployment will use PostgreSQL**
2. **The database will persist between deployments**
3. **Users and data will be preserved**

### Step 4: Create Your Admin User

After successful deployment with PostgreSQL, create your admin user:

**Option A: Use Railway Console**
```bash
# In Railway project console, run:
python manage.py create_user your-email@example.com your-password --superuser --balance 100
```

**Option B: Use Django Admin**
```bash
# Create superuser via Railway console:
python manage.py createsuperuser
```

## Database Verification Commands

Use these commands in Railway console to check database status:

```bash
# Check database info and user count
python manage.py backup_users --action info

# Create a new user with wallet balance
python manage.py create_user user@example.com password123 --balance 50.00

# Create admin user
python manage.py create_user admin@yoursite.com securepassword --superuser --balance 100
```

## Environment Variables Template

Copy these to Railway environment variables:

```env
# Django Core
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=netcop.up.railway.app,*.railway.app
CSRF_TRUSTED_ORIGINS=https://netcop.up.railway.app

# Database (automatically set by Railway PostgreSQL addon)
DATABASE_URL=postgresql://...

# OpenWeather API
OPENWEATHER_API_KEY=your-openweather-api-key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# N8N Webhooks
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n.com/webhook/data-analyzer
N8N_WEBHOOK_JOB_POSTING=https://your-n8n.com/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n.com/webhook/social-ads
```

## Quick Fix Steps

1. **Add PostgreSQL database in Railway**
2. **Wait for deployment to complete**  
3. **Run: `python manage.py backup_users --action info`**
4. **Create your user: `python manage.py create_user your@email.com password --superuser --balance 100`**
5. **Test login at https://netcop.up.railway.app/auth/login/**

## Troubleshooting

### If still using SQLite:
- Check that `DATABASE_URL` environment variable is set in Railway
- Restart the Railway app after adding PostgreSQL
- Check Railway logs for connection errors

### If users still disappearing:
- Verify PostgreSQL addon is active
- Check Railway database tab shows PostgreSQL (not empty)
- Run database info command to verify connection

### If login still fails:
- Check CSRF_TRUSTED_ORIGINS includes your Railway domain
- Verify ALLOWED_HOSTS includes your Railway domain
- Check browser network tab for CSRF errors

## Expected Railway Logs (After PostgreSQL)

```
=== DATABASE INFO ===
Database Engine: django.db.backends.postgresql
Database Name: railway
Total Users: X
Superusers: 1
```

**Key:** Look for `postgresql` engine, not `sqlite3`!