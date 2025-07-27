# Deployment Control Guide

This guide explains how to control deployments to Railway and prevent unwanted automatic deployments while maintaining development velocity.

## Branch Strategy

### Branch Structure
```
main (production) ← Only deploys to Railway production
│
├── staging (pre-production) ← Deploys to Railway staging environment  
│   │
│   └── development (active development) ← No automatic deployment
       │
       ├── feature/new-agent
       ├── feature/ui-improvements
       └── hotfix/critical-bug
```

### Branch Purposes

**`main` Branch (Production)**
- ✅ Protected branch - no direct commits
- ✅ Automatically deploys to Railway production
- ✅ Requires Pull Request approval
- ✅ Must pass all tests and security checks
- ✅ Tagged releases for version tracking

**`staging` Branch (Pre-Production)**
- ✅ Deploys to Railway staging environment
- ✅ Used for final testing before production
- ✅ Merges from `development` via Pull Request
- ✅ Client preview and acceptance testing

**`development` Branch (Active Development)**
- ✅ Default branch for all new work
- ✅ No automatic deployment
- ✅ Continuous integration testing
- ✅ Subagent development and testing
- ✅ Documentation updates

## Railway Deployment Configuration

### Production Environment (main branch)
```json
{
  "environments": {
    "production": {
      "variables": {
        "DEBUG": "False",
        "DEPLOYMENT_ENVIRONMENT": "production",
        "BRANCH_NAME": "main"
      }
    }
  }
}
```

### Staging Environment (staging branch)
```json
{
  "environments": {
    "staging": {
      "variables": {
        "DEBUG": "True",
        "DEPLOYMENT_ENVIRONMENT": "staging", 
        "BRANCH_NAME": "staging"
      }
    }
  }
}
```

## Railway Setup Instructions

### 1. Production Service Configuration
In Railway dashboard for production service:

1. **Connect to Repository**: Link to your GitHub repository
2. **Branch Configuration**: Set deployment branch to `main`
3. **Auto Deploy**: Enable automatic deployments from `main` only
4. **Environment Variables**: Use production environment variables
5. **Custom Domain**: Configure www.quantumtaskai.com

### 2. Staging Service Configuration (Optional but Recommended)
Create a separate Railway service for staging:

1. **Create New Service**: Deploy from same repository
2. **Branch Configuration**: Set deployment branch to `staging`
3. **Environment Variables**: Use staging environment variables
4. **Subdomain**: Use staging-quantumtaskai.railway.app

### 3. Environment Variable Management
Copy `.railway.env.example` to Railway dashboard and configure:

```bash
# Production Environment
DEBUG=False
ALLOWED_HOSTS=www.quantumtaskai.com,quantumtaskai.railway.app
DATABASE_URL=postgresql://production-db-url
STRIPE_SECRET_KEY=sk_live_your_production_key

# Staging Environment  
DEBUG=True
ALLOWED_HOSTS=staging-quantumtaskai.railway.app
DATABASE_URL=postgresql://staging-db-url
STRIPE_SECRET_KEY=sk_test_your_test_key
```

## Development Workflow

### 1. Day-to-Day Development
```bash
# Always work on development branch
git checkout development
git pull origin development

# Create feature branch for specific work
git checkout -b feature/new-sentiment-agent

# Make your changes, test locally
python manage.py runserver

# Commit and push to feature branch
git add .
git commit -m "Add sentiment analysis agent"
git push origin feature/new-sentiment-agent

# Create Pull Request: feature/new-sentiment-agent → development
```

### 2. Testing on Staging
```bash
# When feature is ready for testing
git checkout staging
git pull origin staging

# Merge development into staging
git merge development
git push origin staging

# This triggers deployment to Railway staging environment
# Test at: https://staging-quantumtaskai.railway.app
```

### 3. Production Deployment
```bash
# Only when staging tests pass
git checkout main  
git pull origin main

# Create Pull Request: staging → main
# This requires approval and triggers production deployment
```

## Preventing Accidental Deployments

### 1. GitHub Branch Protection Rules
Configure these rules for `main` branch:

- ✅ Require pull request reviews (minimum 1)
- ✅ Require status checks to pass
- ✅ Require up-to-date branches
- ✅ Restrict pushes to specific users/teams
- ✅ No force pushes allowed
- ✅ No deletions allowed

### 2. Railway Auto-Deploy Settings
- ✅ Production service: Deploy only from `main` branch
- ✅ Staging service: Deploy only from `staging` branch  
- ✅ No deployment from `development` branch
- ✅ Manual deployment approval (optional extra protection)

### 3. Pre-Deploy Checks
Add these checks to your workflow:

```bash
# Before merging to main
python manage.py check --deploy
python manage.py test
python manage.py collectstatic --dry-run

# Security check
python -m bandit -r . -x ./venv/

# Dependency check
pip-audit
```

## Emergency Procedures

### Hotfix Process (Critical Production Bug)
```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-security-fix

# Make minimal fix
# Test thoroughly
git add .
git commit -m "🚨 HOTFIX: Fix critical security vulnerability"

# Direct merge to main (emergency only)
git checkout main
git merge hotfix/critical-security-fix
git push origin main

# Backport to other branches
git checkout development
git merge hotfix/critical-security-fix
git push origin development
```

### Rollback Process
```bash
# If production deployment fails
git checkout main
git reset --hard HEAD~1  # Go back one commit
git push --force-with-lease origin main

# Or use Railway dashboard rollback feature
```

## Deployment Checklist

### Pre-Staging Deployment
- [ ] All tests passing locally
- [ ] Code reviewed by team member
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations tested

### Pre-Production Deployment  
- [ ] Staging environment fully tested
- [ ] Client/stakeholder approval
- [ ] Security audit completed
- [ ] Performance testing passed
- [ ] Backup strategy confirmed
- [ ] Rollback plan prepared

## Monitoring and Alerts

### Railway Monitoring
- ✅ Set up deployment notifications
- ✅ Configure health check endpoints
- ✅ Monitor application logs
- ✅ Set up error alerting

### GitHub Monitoring
- ✅ Enable branch protection notifications
- ✅ Monitor Pull Request activity
- ✅ Track deployment status checks

## Best Practices

### Development
- Always work on `development` branch
- Create descriptive commit messages
- Test locally before pushing
- Use feature branches for significant changes
- Keep commits small and focused

### Testing
- Test all functionality on staging first
- Verify database migrations work correctly
- Check all environment-specific configurations
- Test payment processing in staging environment

### Security
- Never commit secrets to any branch
- Use environment variables for all sensitive data
- Regular security audits before production deployment
- Monitor for dependency vulnerabilities

### Documentation
- Update documentation with every feature
- Document deployment procedures
- Maintain accurate environment variable lists
- Keep rollback procedures current

This workflow ensures that your development work stays safe and controlled while maintaining the ability to deploy quickly when needed.