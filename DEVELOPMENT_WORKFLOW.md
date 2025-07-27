# 🚀 Development Workflow - Quick Reference

## Current Branch Strategy
```
main (production) ← Railway Auto-Deploy ON
│
├── staging (pre-production) ← Railway Staging Environment  
│   │
│   └── development (active development) ← Railway Auto-Deploy OFF
```

## 📋 Daily Development Workflow

### 1. Start New Work
```bash
# Always start from development branch
git checkout development
git pull origin development

# Create feature branch (optional but recommended)
git checkout -b feature/your-feature-name
```

### 2. Make Changes & Test
```bash
# Make your changes
# Test locally
python manage.py runserver

# Use subagents for specialized tasks:
# - "Create new agent" → agent-architect subagent
# - "Fix Django error" → django-debugger subagent  
# - "Security review" → security-auditor subagent
# - "Optimize template" → template-optimizer subagent
```

### 3. Commit to Development
```bash
# Commit your changes
git add .
git commit -m "✨ Add your feature description"

# Push to development (safe - no auto-deploy)
git push origin development
```

### 4. Test on Staging (When Ready)
```bash
# Merge to staging for testing
git checkout staging
git merge development
git push origin staging

# This deploys to Railway staging environment
# Test at: https://staging-quantumtaskai.railway.app
```

### 5. Deploy to Production (Manual Approval Required)
```bash
# Only when staging tests pass
# Create Pull Request: staging → main
# Requires approval before merging
# Auto-deploys to production after merge
```

## 🛡️ Safety Features

### ✅ What's Protected
- **main branch**: Requires PR approval, auto-deploys to production
- **Railway production**: Only deploys from main branch
- **Accidental deployments**: Prevented by branch protection

### ✅ What's Safe
- **development branch**: No auto-deployment, safe for experimentation
- **feature branches**: No auto-deployment, safe for testing
- **Local testing**: Always safe with `python manage.py runserver`

## 🚨 Emergency Procedures

### Hotfix Critical Production Bug
```bash
git checkout main
git checkout -b hotfix/critical-fix
# Make minimal fix
git checkout main
git merge hotfix/critical-fix
git push origin main  # Deploys immediately
```

### Rollback Production
```bash
# Option 1: Git rollback
git checkout main
git reset --hard HEAD~1
git push --force-with-lease origin main

# Option 2: Railway dashboard rollback
# Use Railway UI to rollback to previous deployment
```

## 📞 Quick Commands

### Development Server
```bash
./run_dev.sh  # Quick start with migrations
python manage.py runserver  # Manual start
```

### Testing
```bash
python manage.py check --deploy  # Production readiness
python tests/test_agent_name.py  # Test specific agent
```

### Documentation
```bash
./scripts/update_docs_manual.sh  # Update documentation
/update-docs  # Claude Code slash command
```

### Branch Protection
```bash
./scripts/setup_branch_protection.sh  # Setup GitHub protections
```

## 🎯 Key Points

1. **Development branch = Safe zone** - No auto-deployment
2. **Staging branch = Test environment** - Deploys to staging
3. **Main branch = Production** - Requires approval, auto-deploys
4. **All new work** should start on development branch
5. **Subagents available** for specialized development tasks
6. **Auto-documentation** updates with each commit

## 🔗 Related Documentation

- [Complete Deployment Control Guide](./docs/deployment/deployment-control-guide.md)
- [Subagents Guide](./docs/development/subagents-guide.md)
- [Auto-Documentation System](./docs/development/auto-documentation-system.md)
- [Railway Deployment Guide](./docs/deployment/railway-deployment.md)

---

**Remember**: development branch is your safe space - experiment freely! 🧪