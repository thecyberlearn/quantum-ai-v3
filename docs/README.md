# 📚 Quantum Tasks AI Documentation

Welcome to the comprehensive documentation for Quantum Tasks AI - a Django-based AI agent marketplace platform.

## 🚀 Quick Start

- **New to the project?** Start with [Local Development Setup](./development/setup-guide.md)
- **Deploying to production?** See [Railway Deployment Guide](./deployment/railway-deployment.md)
- **Changing domains?** Follow [Domain Change Guide](./deployment/domain-change-guide.md)
- **Building agents?** Check [Agent Creation Guide](./development/agent-creation.md)

---

## 📂 Documentation Structure

### 🛠️ Development
Documentation for local development and agent creation.

| Document | Description |
|----------|-------------|
| [Setup Guide](./development/setup-guide.md) | Local development environment setup |
| [Agent Creation](./development/agent-creation.md) | Building new AI agents for the platform |
| [Testing Guide](./development/testing.md) | Testing procedures and best practices |

### 🚀 Deployment
Production deployment and configuration guides.

| Document | Description |
|----------|-------------|
| [Railway Deployment](./deployment/railway-deployment.md) | Complete Railway.app deployment guide |
| [Domain Change Guide](./deployment/domain-change-guide.md) | Step-by-step domain change instructions |
| [Environment Variables](./deployment/environment-variables.md) | Complete environment configuration reference |

### ⚙️ Operations
System maintenance, troubleshooting, and operations.

| Document | Description |
|----------|-------------|
| [Database Management](./operations/database-management.md) | Database operations and maintenance |
| [Troubleshooting](./operations/troubleshooting.md) | Common issues and solutions |
| [Maintenance](./operations/maintenance.md) | System maintenance procedures |

---

## 🏗️ Architecture Overview

**Core Components:**
- 🌐 **Django Application** - Main web platform
- 🗄️ **PostgreSQL Database** - User data and transactions
- 🔄 **Redis Cache** - Session storage and performance
- 🤖 **AI Agents** - Specialized AI tools for users
- 💳 **Stripe Integration** - Payment processing
- 📧 **Email System** - User notifications and verification

**Agent Architecture:**
- **API Agents** - Direct API integration (e.g., Weather Reporter)
- **Webhook Agents** - External N8N workflow processing (e.g., Data Analyzer)

---

## 📋 Essential Information

### 🔧 System Requirements

**Development:**
- Python 3.8+
- Django 5.2+
- SQLite (default) or PostgreSQL
- Redis (optional)

**Production:**
- Railway.app account
- PostgreSQL database
- Redis cache
- SMTP email service
- Stripe account

### 🌍 Environment Types

| Environment | Database | Cache | Email | Purpose |
|-------------|----------|-------|-------|---------|
| **Local Dev** | SQLite | Memory | Console | Development and testing |
| **Railway Staging** | PostgreSQL | Redis | SMTP | Pre-production testing |
| **Railway Production** | PostgreSQL | Redis | SMTP | Live application |

### 🔗 Key URLs

**Development:**
- Application: `http://localhost:8000`
- Admin: `http://localhost:8000/admin/`
- Health Check: `http://localhost:8000/health/`

**Production:**
- Application: `https://quantum-ai.up.railway.app`
- Admin: `https://quantum-ai.up.railway.app/admin/`
- Health Check: `https://quantum-ai.up.railway.app/health/`

---

## 🚨 Emergency Procedures

### Quick Fixes

**Application Won't Start:**
1. Check [Troubleshooting Guide](./operations/troubleshooting.md)
2. Verify [Environment Variables](./deployment/environment-variables.md)
3. Test database connection: `python manage.py check --database default`

**Domain Issues:**
1. Follow [Domain Change Guide](./deployment/domain-change-guide.md)
2. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
3. Test with health check endpoint

**Database Problems:**
1. See [Database Management](./operations/database-management.md)
2. Check Railway PostgreSQL service status
3. Verify `DATABASE_URL` environment variable

### Support Commands

```bash
# Check system health
python manage.py check --deploy

# Test database connection
python manage.py check_db

# Create admin user
python manage.py check_admin

# Test email functionality
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

---

## 🔍 Finding Information

### 📖 By Task

| What do you want to do? | Go to |
|-------------------------|--------|
| Set up local development | [Setup Guide](./development/setup-guide.md) |
| Deploy to production | [Railway Deployment](./deployment/railway-deployment.md) |
| Change domain/URL | [Domain Change Guide](./deployment/domain-change-guide.md) |
| Configure environment | [Environment Variables](./deployment/environment-variables.md) |
| Create new AI agent | [Agent Creation](./development/agent-creation.md) |
| Fix database issues | [Database Management](./operations/database-management.md) |
| Solve common problems | [Troubleshooting](./operations/troubleshooting.md) |

### 📖 By Component

| Component | Documentation |
|-----------|---------------|
| **Django App** | [Setup Guide](./development/setup-guide.md), [Railway Deployment](./deployment/railway-deployment.md) |
| **Database** | [Database Management](./operations/database-management.md), [Environment Variables](./deployment/environment-variables.md) |
| **AI Agents** | [Agent Creation](./development/agent-creation.md) |
| **Email System** | [Environment Variables](./deployment/environment-variables.md), [Troubleshooting](./operations/troubleshooting.md) |
| **Payments** | [Environment Variables](./deployment/environment-variables.md) |

---

## 🆘 Getting Help

### Documentation Issues
- 📝 Found outdated information? Check if there's a newer version
- 🔍 Can't find what you need? Check the [Troubleshooting Guide](./operations/troubleshooting.md)
- 📧 Still stuck? Review error logs and environment configuration

### Development Questions
- 🧪 Testing issues? See [Testing Guide](./development/testing.md)
- 🤖 Agent development? Check [Agent Creation](./development/agent-creation.md)
- 🔧 Environment setup? Follow [Setup Guide](./development/setup-guide.md)

### Production Issues
- 🚀 Deployment problems? See [Railway Deployment](./deployment/railway-deployment.md)
- 🌐 Domain/DNS issues? Follow [Domain Change Guide](./deployment/domain-change-guide.md)
- 🗄️ Database problems? Check [Database Management](./operations/database-management.md)

---

## 📅 Documentation Updates

This documentation is updated regularly. Key sections:

- **Environment Variables** - Updated with new integrations
- **Deployment Guides** - Updated for new Railway features
- **Troubleshooting** - Updated with new common issues
- **Agent Creation** - Updated with new agent types

**Last Major Update:** December 2024  
**Current Version:** Django 5.2, Python 3.8+, Railway.app deployment

---

**🎯 Pro Tip:** Bookmark this page and the [Quick Start](#-quick-start) section for fast access to essential guides!