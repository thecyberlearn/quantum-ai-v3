# Development Guide

## Quick Start

### Option 1: Use the Development Script (Recommended)
```bash
./run_dev.sh
```

### Option 2: Manual Startup
```bash
# Clear any interfering environment variables
unset DATABASE_URL

# Activate virtual environment
source venv/bin/activate

# Start server
python manage.py runserver
```

## Common Issues

### Issue: "Connection refused" Error with PostgreSQL
**Cause:** You have `DATABASE_URL` set as an environment variable pointing to PostgreSQL.

**Solution:**
```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# Temporarily unset it
unset DATABASE_URL

# Start server
python manage.py runserver
```

**Permanent Fix:**
If `DATABASE_URL` keeps getting set, check these files:
- `~/.bashrc`
- `~/.bash_profile` 
- `~/.profile`
- `~/.zshrc`
- `~/.env` (global)

Remove any lines containing `DATABASE_URL=` unless you specifically need them.

### Issue: Database Tables Don't Exist
```bash
# Run migrations
python manage.py migrate

# Create admin user and populate data
python manage.py populate_agents --create-admin
```

### Issue: Admin Login Not Working
```bash
# Check if admin user exists
python manage.py backup_users --action info

# Create admin user
python manage.py create_user admin@example.com password123 --superuser
```

## Database Configuration

### Local Development (Default)
- **Engine:** SQLite
- **Location:** `db.sqlite3`
- **Setup:** None required

### Local Development with PostgreSQL (Optional)
1. **Set up PostgreSQL:**
   ```bash
   # Using Docker (easiest)
   docker run --name netcop-postgres \\
     -e POSTGRES_DB=netcop_hub \\
     -e POSTGRES_USER=netcop_user \\
     -e POSTGRES_PASSWORD=netcop_pass \\
     -p 5432:5432 -d postgres:15
   ```

2. **Enable in .env:**
   ```env
   USE_POSTGRESQL=True
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py populate_agents --create-admin
   ```

### Railway Production
- **Engine:** PostgreSQL (automatic)
- **Configuration:** Via Railway's `DATABASE_URL`
- **Setup:** None required

## Environment Variables

### Required for Development
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### Optional for Development
```env
# Force PostgreSQL (requires PostgreSQL setup)
USE_POSTGRESQL=True

# Or specify exact database URL
DATABASE_URL=postgresql://netcop_user:netcop_pass@localhost:5432/netcop_hub

# API Keys (for full functionality)
OPENWEATHER_API_KEY=your-key-here
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Development Workflow

### Daily Development
```bash
# Start development server
./run_dev.sh

# In another terminal - run commands
source venv/bin/activate
python manage.py check_db          # Check database status
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
```

### Testing Changes
```bash
# Check for issues
python manage.py check

# Test migrations
python manage.py migrate --plan

# Create test data
python manage.py populate_agents --create-admin
```

### Debugging
```bash
# Check database configuration
python manage.py check_db

# Check migration status
python manage.py showmigrations

# Django shell
python manage.py shell
```

## File Structure

```
netcop_django/
├── run_dev.sh              # Development startup script
├── manage.py               # Django management
├── requirements.txt        # Python dependencies
├── .env                   # Local environment variables
├── db.sqlite3             # SQLite database (local)
├── docs/                  # Documentation
├── static/                # Static files
├── templates/             # Global templates
├── netcop_hub/            # Django project settings
├── core/                  # Main app (homepage, marketplace)
├── authentication/       # User management
├── wallet/               # Payment system
├── agent_base/           # Agent framework
├── weather_reporter/     # Weather agent
├── data_analyzer/        # Data analysis agent
├── job_posting_generator/ # Job posting agent
└── social_ads_generator/ # Social ads agent
```

## Useful Commands

```bash
# Development
./run_dev.sh                                    # Start dev server
python manage.py check_db                       # Check database
python manage.py migrate                        # Run migrations
python manage.py populate_agents --create-admin # Setup data

# User Management
python manage.py create_user email@example.com password123 --superuser
python manage.py backup_users --action info

# Database Management
python manage.py reset_database --action full --confirm
python manage.py fix_migrations --app data_analyzer

# Debugging
python manage.py check                          # System check
python manage.py showmigrations                 # Migration status
python manage.py shell                          # Django shell
```

## Troubleshooting

### Server Won't Start
1. Check if `DATABASE_URL` is set: `echo $DATABASE_URL`
2. Unset it: `unset DATABASE_URL` 
3. Use the development script: `./run_dev.sh`

### Database Issues
1. Check configuration: `python manage.py check_db`
2. Run migrations: `python manage.py migrate`
3. Reset if needed: `python manage.py reset_database --action full --confirm`

### Import Errors
1. Activate virtual environment: `source venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`

### Permission Errors
1. Make script executable: `chmod +x run_dev.sh`
2. Check file permissions: `ls -la`

Happy coding! 🎉