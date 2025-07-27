# 🛠️ Local Development Setup Guide

Complete guide for setting up Quantum Tasks AI for local development.

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (recommended: Python 3.10+)
- **Git** for version control
- **Code Editor** (VS Code, PyCharm, etc.)

### Optional but Recommended
- **PostgreSQL** for database parity with production
- **Redis** for caching (falls back to memory cache if unavailable)
- **N8N** for testing webhook agents locally

---

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/quantum_ai.git
cd quantum_ai
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python --version
pip list | grep Django
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Minimum required for local development:
SECRET_KEY=your-50-character-secret-key-for-development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

### 5. Setup Database
```bash
# Check database configuration
python manage.py check_db

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Populate agent catalog
python manage.py populate_agents
```

### 6. Create Admin User
```bash
# Create superuser
python manage.py check_admin

# Or create manually
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
# Quick start (recommended)
./run_dev.sh

# Or manual start
python manage.py runserver
```

### 8. Verify Installation
Open browser and visit:
- **Application:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin/
- **Health Check:** http://localhost:8000/health/

---

## ⚙️ Detailed Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Core Django Settings
SECRET_KEY=your-development-secret-key-50-characters-minimum
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Database (SQLite by default, PostgreSQL optional)
# Uncomment for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/quantum_ai
# USE_POSTGRESQL=True

# Email (console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stripe (use test keys)
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret

# External APIs
OPENWEATHER_API_KEY=your_openweather_api_key

# N8N Webhooks (local N8N instance)
N8N_WEBHOOK_DATA_ANALYZER=http://localhost:5678/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=http://localhost:5678/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=http://localhost:5678/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=http://localhost:5678/webhook/social-ads
N8N_WEBHOOK_FAQ_GENERATOR=http://localhost:5678/webhook/faq-generator

# Cache (optional)
# REDIS_URL=redis://127.0.0.1:6379/1
```

### Database Options

**Option 1: SQLite (Default)**
- No additional setup required
- Database file: `db.sqlite3`
- Perfect for development

**Option 2: PostgreSQL (Production Parity)**
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql
brew services start postgresql

# Create database
createdb quantum_ai

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/quantum_ai
```

---

## 🧪 Testing Setup

### Run Tests
```bash
# Test specific agent
python tests/test_weather_agent.py

# Test homepage
python tests/test_homepage.py

# Test webhook functionality
python tests/test_five_whys_webhook.py
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health/

# Test admin access
# Visit: http://localhost:8000/admin/
# Login with created superuser credentials
```

---

## 🔧 Development Tools

### Management Commands
```bash
# Create new agent (interactive)
python manage.py create_agent

# Create test user
python manage.py create_user

# Reset database (development only)
python manage.py reset_database

# Test webhook functionality
python manage.py test_webhook

# Cleanup uploaded files
python manage.py cleanup_uploads

# Backup user data
python manage.py backup_users --action info
```

### N8N Workflow Management
```bash
# List all workflows
python manage_n8n_workflows.py list

# Import workflow to local N8N
python manage_n8n_workflows.py import data_analyzer

# Sync workflows
python manage_n8n_workflows.py sync
```

### Debug Tools
```bash
# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Check deployment readiness
python manage.py check --deploy
```

---

## 🔌 Optional Services

### Redis Cache Setup
```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis
brew services start redis

# Test Redis connection
redis-cli ping
# Should return: PONG

# Update .env
REDIS_URL=redis://127.0.0.1:6379/1
```

### N8N Local Setup
```bash
# Install N8N globally
npm install n8n -g

# Start N8N
n8n start

# Access N8N UI
# Visit: http://localhost:5678

# Import workflows
python manage_n8n_workflows.py import data_analyzer
```

---

## 🐛 Troubleshooting

### Common Issues

**❌ Module Not Found Error:**
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**❌ Database Migration Error:**
```bash
# Solution: Reset migrations (development only)
python manage.py reset_database

# Or fix specific migration
python manage.py migrate --fake-initial
```

**❌ Port Already in Use:**
```bash
# Solution: Use different port
python manage.py runserver 8001

# Or kill process using port 8000
sudo lsof -t -i tcp:8000 | xargs kill -9
```

**❌ Secret Key Error:**
```bash
# Solution: Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add to .env file
SECRET_KEY=generated-secret-key
```

### Development Tips

**Performance:**
- Use SQLite for development (faster)
- Enable Django Debug Toolbar (if installed)
- Use `--verbosity 2` for detailed command output

**Database:**
- Reset database frequently during development
- Use fixtures for test data
- Backup important data before major changes

**Static Files:**
- No need to collect static files in development
- Django serves static files automatically with DEBUG=True

---

## 📚 Next Steps

After successful setup:

1. **Explore the codebase:** Read [docs/README.md](../README.md) for architecture overview
2. **Create an agent:** Follow [Agent Creation Guide](./agent-creation.md)
3. **Test functionality:** Run test suite and manual testing
4. **Deploy to staging:** Follow [Railway Deployment Guide](../deployment/railway-deployment.md)

---

## 🔗 Related Documentation

- [Agent Creation Guide](./agent-creation.md) - Build new AI agents
- [Testing Guide](./testing.md) - Testing procedures
- [Environment Variables](../deployment/environment-variables.md) - Complete environment reference
- [Railway Deployment](../deployment/railway-deployment.md) - Production deployment

---

**🎉 You're ready to develop! Visit http://localhost:8000 to see your local Quantum Tasks AI instance.**