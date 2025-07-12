# PostgreSQL Local Development Setup

## Why Use PostgreSQL Locally?

Using PostgreSQL locally matches your Railway production environment and prevents deployment failures caused by database engine differences.

## Quick Setup (Option 1: Docker - Easiest)

### 1. Install Docker
Download Docker Desktop from: https://www.docker.com/products/docker-desktop/

### 2. Run PostgreSQL Container
```bash
# Create and start PostgreSQL container
docker run --name netcop-postgres \
  -e POSTGRES_DB=netcop_hub \
  -e POSTGRES_USER=netcop_user \
  -e POSTGRES_PASSWORD=netcop_pass \
  -p 5432:5432 \
  -d postgres:15

# Verify it's running
docker ps
```

### 3. Update Your .env File
The `.env` file is already configured for this setup:
```env
DATABASE_URL=postgresql://netcop_user:netcop_pass@localhost:5432/netcop_hub
```

### 4. Start/Stop Database
```bash
# Start the database (if stopped)
docker start netcop-postgres

# Stop the database (when not needed)
docker stop netcop-postgres

# View logs (for debugging)
docker logs netcop-postgres
```

## Full Setup (Option 2: Native PostgreSQL)

### 1. Install PostgreSQL

**macOS (with Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Windows:**
Download from: https://www.postgresql.org/download/windows/

### 2. Create Database and User
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Or on macOS/Windows:
psql postgres

# Create database and user
CREATE DATABASE netcop_hub;
CREATE USER netcop_user WITH PASSWORD 'netcop_pass';
GRANT ALL PRIVILEGES ON DATABASE netcop_hub TO netcop_user;
\q
```

### 3. Test Connection
```bash
psql -h localhost -U netcop_user -d netcop_hub
# Enter password: netcop_pass
# You should see: netcop_hub=>
\q
```

## Django Setup

### 1. Install PostgreSQL Python Driver
```bash
pip install psycopg2-binary
```

### 2. Reset Migrations (Clean Start)
```bash
# Reset all migrations for clean PostgreSQL setup
python manage.py reset_database --action full --confirm

# Or manually:
python manage.py reset_database --action migrations --confirm
python manage.py makemigrations
python manage.py migrate
python manage.py populate_agents --create-admin
```

### 3. Test Your Setup
```bash
# Check database connection
python manage.py backup_users --action info

# Create test user
python manage.py create_user test@example.com testpass123 --balance 50

# Start development server
python manage.py runserver
```

## Troubleshooting

### Connection Refused Error
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solution:**
- Ensure PostgreSQL is running: `docker ps` or `brew services list`
- Check port 5432 is not in use: `lsof -i :5432`
- For Docker: `docker start netcop-postgres`

### Password Authentication Failed
```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solution:**
- Check `.env` file has correct credentials
- Recreate user with correct password:
```sql
DROP USER IF EXISTS netcop_user;
CREATE USER netcop_user WITH PASSWORD 'netcop_pass';
GRANT ALL PRIVILEGES ON DATABASE netcop_hub TO netcop_user;
```

### Migration Conflicts
```
django.db.utils.ProgrammingError: column "data_file" already exists
```

**Solution:**
```bash
# Fix migration conflicts
python manage.py fix_migrations --app data_analyzer

# Or clean reset
python manage.py reset_database --action full --confirm
```

### Database Permission Denied
```
django.db.utils.ProgrammingError: permission denied for relation
```

**Solution:**
```sql
# Grant all permissions to user
GRANT ALL PRIVILEGES ON DATABASE netcop_hub TO netcop_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO netcop_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO netcop_user;
```

## Development Workflow

### Daily Workflow
```bash
# 1. Start database (Docker)
docker start netcop-postgres

# 2. Start Django development server
python manage.py runserver

# 3. When done, stop database (optional)
docker stop netcop-postgres
```

### Making Model Changes
```bash
# 1. Edit your models.py
# 2. Create migrations
python manage.py makemigrations

# 3. Test migration locally (PostgreSQL)
python manage.py migrate

# 4. Test your changes
python manage.py runserver

# 5. Commit and push (will deploy to Railway)
git add .
git commit -m "Update models"
git push origin main
```

### Switching Between SQLite and PostgreSQL

**To use SQLite (quick testing):**
```env
# In .env file:
DATABASE_URL=sqlite:///db.sqlite3
```

**To use PostgreSQL (development/production parity):**
```env
# In .env file:
DATABASE_URL=postgresql://netcop_user:netcop_pass@localhost:5432/netcop_hub
```

## Benefits You'll See

✅ **Reliable deployments** - What works locally works on Railway  
✅ **Early error detection** - Catch PostgreSQL-specific issues  
✅ **Consistent behavior** - Same database engine everywhere  
✅ **Better performance testing** - Real PostgreSQL performance  
✅ **Migration confidence** - Test exact same migrations  

## Quick Commands Reference

```bash
# Database management
python manage.py backup_users --action info
python manage.py reset_database --action full --confirm
python manage.py fix_migrations --check-only

# User management
python manage.py create_user email@example.com password123 --superuser
python manage.py populate_agents --create-admin

# Docker PostgreSQL
docker start netcop-postgres
docker stop netcop-postgres
docker logs netcop-postgres
```

Your development environment now matches Railway production exactly! 🎉