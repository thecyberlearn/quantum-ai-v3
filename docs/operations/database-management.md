# 🗄️ Database Management Guide

Comprehensive guide for managing databases in Quantum Tasks AI across development and production environments.

## 📋 Overview

**Database Types by Environment:**
- **Local Development:** SQLite (default) or PostgreSQL (optional)
- **Railway Production:** PostgreSQL (managed)
- **Testing:** SQLite (isolated)

---

## 🛠️ Development Database Management

### SQLite (Default)

**Basic Operations:**
```bash
# Check database configuration
python manage.py check_db

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py reset_database

# Access database shell
python manage.py dbshell
```

**Database File Location:**
- File: `db.sqlite3` in project root
- Backup: Copy the file to safe location
- Reset: Delete file and run migrations

### PostgreSQL (Local)

**Setup:**
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql
brew services start postgresql

# Create database
createdb quantum_ai

# Create user (optional)
createuser quantum_user -P

# Update .env
USE_POSTGRESQL=True
DATABASE_URL=postgresql://quantum_user:password@localhost:5432/quantum_ai
```

**Management:**
```bash
# Connect to database
psql -d quantum_ai

# Backup database
pg_dump quantum_ai > backup.sql

# Restore database
psql quantum_ai < backup.sql

# Check connections
psql -c "SELECT datname, numbackends FROM pg_stat_database;"
```

---

## 🚀 Production Database Management

### Railway PostgreSQL

**Automatic Setup:**
- Railway automatically provisions PostgreSQL when added
- `DATABASE_URL` environment variable auto-configured
- Managed backups and scaling

**Accessing Production Database:**
```bash
# Via Railway CLI
railway connect postgres

# Via connection string
psql $DATABASE_URL

# Or get connection details from Railway dashboard
```

**Production Commands:**
```bash
# Run migrations on production
railway run python manage.py migrate

# Check production database status
railway run python manage.py check_db

# Create admin user
railway run python manage.py check_admin

# Backup users data
railway run python manage.py backup_users --action export
```

### Connection Management

**Connection Pooling (Auto-configured):**
```python
# In settings.py
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
```

**Connection Monitoring:**
```sql
-- Check active connections
SELECT datname, numbackends FROM pg_stat_database;

-- Check connection limits
SELECT setting FROM pg_settings WHERE name = 'max_connections';

-- View current connections
SELECT * FROM pg_stat_activity WHERE datname = 'railway';
```

---

## 🔄 Database Migrations

### Creating Migrations

```bash
# Auto-detect model changes
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations agent_base

# Create empty migration
python manage.py makemigrations --empty agent_base

# Name migration
python manage.py makemigrations --name add_user_preferences agent_base
```

### Applying Migrations

```bash
# Apply all migrations
python manage.py migrate

# Apply specific app migrations
python manage.py migrate agent_base

# Apply to specific migration
python manage.py migrate agent_base 0001

# Fake migration (mark as applied without running)
python manage.py migrate --fake agent_base 0001
```

### Migration Management

```bash
# Show migration status
python manage.py showmigrations

# Show SQL for migration
python manage.py sqlmigrate agent_base 0001

# Reverse migration
python manage.py migrate agent_base 0001

# List migrations
ls -la */migrations/
```

### Migration Best Practices

**Safe Migration Patterns:**
```python
# ✅ Safe: Add new field with default
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, default=''),
        ),
    ]

# ✅ Safe: Add new model
class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[...],
        ),
    ]

# ⚠️ Caution: Rename field (data migration needed)
# ❌ Dangerous: Drop field without backup
```

---

## 🔧 Database Maintenance

### Regular Maintenance Tasks

**Daily (Automated):**
- Connection monitoring
- Performance metrics review
- Error log analysis

**Weekly:**
- Database size monitoring
- Query performance review
- Index usage analysis

**Monthly:**
- Full database backup
- Cleanup old data (if applicable)
- Performance optimization review

### Performance Optimization

**Query Optimization:**
```sql
-- Find slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename = 'authentication_user';

-- Analyze table statistics
ANALYZE authentication_user;
```

**Django Optimization:**
```python
# Use select_related for foreign keys
users = User.objects.select_related('wallet').all()

# Use prefetch_related for many-to-many
users = User.objects.prefetch_related('transactions').all()

# Add database indexes
class Meta:
    indexes = [
        models.Index(fields=['email', 'created_at']),
        models.Index(fields=['-created_at']),
    ]
```

### Cleanup Operations

```bash
# Cleanup uploaded files
python manage.py cleanup_uploads

# Clear sessions (if using database sessions)
python manage.py clearsessions

# Custom cleanup command example
python manage.py shell -c "
from authentication.models import User
from datetime import datetime, timedelta
# Delete inactive users older than 1 year
cutoff = datetime.now() - timedelta(days=365)
inactive_users = User.objects.filter(
    last_login__lt=cutoff,
    is_active=False
)
print(f'Found {inactive_users.count()} inactive users')
# inactive_users.delete()  # Uncomment to actually delete
"
```

---

## 💾 Backup & Recovery

### Local Development Backups

**SQLite Backup:**
```bash
# Simple file copy
cp db.sqlite3 backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Using Django
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

**PostgreSQL Backup:**
```bash
# Full database dump
pg_dump quantum_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump quantum_ai | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Data only
pg_dump --data-only quantum_ai > data_backup.sql

# Schema only
pg_dump --schema-only quantum_ai > schema_backup.sql
```

### Production Backups

**Railway Managed Backups:**
- Railway automatically creates daily backups
- Access via Railway dashboard
- Point-in-time recovery available

**Manual Production Backup:**
```bash
# Backup via Railway CLI
railway run pg_dump $DATABASE_URL > production_backup_$(date +%Y%m%d).sql

# User data backup
railway run python manage.py backup_users --action export > users_backup.json

# Backup specific tables
railway run pg_dump $DATABASE_URL -t authentication_user -t wallet_wallettransaction > critical_backup.sql
```

### Recovery Procedures

**Local Recovery:**
```bash
# SQLite restore
cp backups/db_20241225_120000.sqlite3 db.sqlite3

# PostgreSQL restore
psql quantum_ai < backup_20241225_120000.sql

# Django fixtures restore
python manage.py loaddata backup_20241225_120000.json
```

**Production Recovery:**
```bash
# Contact Railway support for point-in-time recovery
# Or restore from manual backup

# Restore to new database (safest)
railway run psql $DATABASE_URL < backup_file.sql

# Partial restore (specific tables)
railway run psql $DATABASE_URL -c "\copy authentication_user FROM 'users_backup.csv' WITH CSV HEADER"
```

---

## 🔍 Monitoring & Diagnostics

### Health Checks

```bash
# Django database check
python manage.py check --database default

# Custom health check
curl http://localhost:8000/health/

# Railway health check
railway run python manage.py check_db
```

### Performance Monitoring

**Database Metrics:**
```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Database size
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
WHERE datname = 'railway';

-- Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

**Django Debug:**
```python
# In Django shell
from django.db import connection
from django.db import connections

# Check database connection
connections['default'].cursor()

# View queries
from django.conf import settings
settings.LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
}
```

### Log Analysis

```bash
# Railway PostgreSQL logs
railway logs --service postgres

# Django database queries (if DEBUG=True)
python manage.py runserver --verbosity=2

# Check for long-running queries
# Use Railway dashboard metrics
```

---

## 🚨 Troubleshooting Database Issues

### Common Problems

**Connection Refused:**
```bash
# Check if PostgreSQL is running
systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# Check connection parameters
psql -h localhost -p 5432 -U username -d database

# Railway connection test
railway run psql $DATABASE_URL -c "SELECT 1;"
```

**Migration Conflicts:**
```bash
# Show migration conflicts
python manage.py showmigrations | grep "\[ \]"

# Resolve conflicts
python manage.py migrate --fake app_name migration_number
python manage.py migrate app_name

# Nuclear option (development only)
python manage.py reset_database
```

**Performance Issues:**
```sql
-- Find slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Check for blocking queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks 
        ON blocking_locks.locktype = blocked_locks.locktype
        AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

## 📚 Related Documentation

- [Environment Variables](../deployment/environment-variables.md) - Database configuration
- [Railway Deployment](../deployment/railway-deployment.md) - Production setup
- [Troubleshooting Guide](./troubleshooting.md) - Common database issues
- [Maintenance Guide](./maintenance.md) - Ongoing maintenance procedures

---

**⚡ Pro Tips:**
- Always backup before major operations
- Test migrations on development environment first
- Monitor connection counts in production
- Use database indexes for frequently queried fields
- Keep development and production database structures in sync