# Deployment Checklist

Use this checklist to ensure safe and successful deployments to Railway.

## Pre-Development Setup ✅

### Branch Protection (One-time setup)
- [ ] Run `./scripts/setup_branch_protection.sh`
- [ ] Verify main branch requires PR approval
- [ ] Confirm staging branch protection (optional)
- [ ] Set development as default branch for PRs

### Railway Configuration (One-time setup)
- [ ] Production service connected to `main` branch only
- [ ] Staging service connected to `staging` branch (optional)
- [ ] Auto-deploy enabled only for designated branches
- [ ] Environment variables configured per environment
- [ ] Custom domain configured for production

## Development Phase 🛠️

### Before Starting Work
- [ ] Working on `development` branch
- [ ] Local environment up to date: `git pull origin development`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`

### During Development
- [ ] Regular local testing: `python manage.py runserver`
- [ ] Use appropriate subagents for specialized tasks:
  - [ ] `agent-architect` for new agents
  - [ ] `django-expert` for Django development
  - [ ] `security-auditor` for security reviews
  - [ ] `template-optimizer` for UI improvements
  - [ ] `django-debugger` for error fixes

### Code Quality Checks
- [ ] Code follows project conventions
- [ ] No hardcoded secrets or API keys
- [ ] Environment variables used for configuration
- [ ] Error handling implemented
- [ ] Input validation in place
- [ ] CSRF protection on forms
- [ ] Authentication/authorization properly handled

## Pre-Staging Deployment 🧪

### Code Readiness
- [ ] All changes committed to `development` branch
- [ ] Local tests passing: `python manage.py test`
- [ ] Django system check: `python manage.py check --deploy`
- [ ] No migration conflicts
- [ ] Static files collection works: `python manage.py collectstatic --dry-run`

### Documentation
- [ ] CLAUDE.md updated (if needed)
- [ ] Feature documentation added
- [ ] API changes documented (if applicable)
- [ ] Environment variable changes noted

### Database Migrations
- [ ] Migrations created: `python manage.py makemigrations`
- [ ] Migration files reviewed for correctness
- [ ] Backward compatibility confirmed
- [ ] Migration tested locally

## Staging Deployment 🎭

### Deployment Process
- [ ] Merge `development` → `staging`
- [ ] Push to remote: `git push origin staging`
- [ ] Verify staging deployment successful
- [ ] Check staging logs for errors

### Staging Testing
- [ ] Full application workflow testing
- [ ] All agent functionality working
- [ ] Payment processing working (test mode)
- [ ] File uploads working correctly
- [ ] Email functionality working
- [ ] Database migrations applied correctly
- [ ] Static files serving correctly
- [ ] Mobile/responsive design verified
- [ ] Cross-browser compatibility checked

### Performance Testing
- [ ] Page load times acceptable
- [ ] Agent processing times normal
- [ ] Database query performance good
- [ ] No memory leaks or high resource usage

### Security Testing
- [ ] Authentication working correctly
- [ ] Authorization enforced properly
- [ ] CSRF protection active
- [ ] XSS prevention in place
- [ ] File upload security working
- [ ] Payment security measures active

## Pre-Production Deployment 🚀

### Final Approval
- [ ] Staging tests completed successfully
- [ ] Client/stakeholder approval received
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] All acceptance criteria satisfied

### Production Readiness
- [ ] Production environment variables ready
- [ ] Database backup completed
- [ ] SSL certificates valid
- [ ] Custom domain configuration ready
- [ ] Monitoring and alerting configured

### Deployment Strategy
- [ ] Rollback plan prepared and tested
- [ ] Deployment window scheduled (if needed)
- [ ] Team notified of deployment
- [ ] Post-deployment verification plan ready

## Production Deployment 🎯

### Deployment Process
- [ ] Create Pull Request: `staging` → `main`
- [ ] PR review completed and approved
- [ ] All CI/CD checks passing
- [ ] Merge PR to `main` branch
- [ ] Verify automatic deployment triggered

### Post-Deployment Verification
- [ ] Application responding correctly
- [ ] Health check endpoint working: `/health/`
- [ ] Database migrations applied successfully
- [ ] Static files serving correctly
- [ ] Custom domain working
- [ ] SSL certificate active
- [ ] Payment processing working
- [ ] Email functionality working

### Monitoring
- [ ] Application logs monitored for errors
- [ ] Performance metrics within normal range
- [ ] Error rates within acceptable limits
- [ ] User feedback monitored
- [ ] Support channels ready for issues

## Post-Deployment 📊

### Success Confirmation
- [ ] All critical user flows tested in production
- [ ] Analytics and monitoring data normal
- [ ] No critical errors in logs
- [ ] Customer support tickets minimal
- [ ] Team notified of successful deployment

### Documentation Updates
- [ ] Deployment notes recorded
- [ ] Version/release notes updated
- [ ] Any configuration changes documented
- [ ] Lessons learned documented

### Environment Cleanup
- [ ] Development branch updated from main
- [ ] Staging branch synced with main
- [ ] Feature branches cleaned up (if any)
- [ ] Local environment updated

## Emergency Procedures 🚨

### If Deployment Fails
- [ ] Check Railway deployment logs
- [ ] Review application error logs
- [ ] Verify environment variables
- [ ] Check database migration status
- [ ] Consider immediate rollback if critical

### Rollback Process
- [ ] Use Railway dashboard rollback feature, OR
- [ ] Git rollback: `git reset --hard HEAD~1` and force push
- [ ] Verify rollback successful
- [ ] Investigate and fix issue
- [ ] Plan re-deployment

### Communication
- [ ] Notify team of deployment status
- [ ] Update stakeholders on any issues
- [ ] Document any problems encountered
- [ ] Plan fixes for next deployment

## Environment-Specific Checklists

### Staging Environment
- [ ] DEBUG=True for better error visibility
- [ ] Test Stripe keys used
- [ ] Test email configuration
- [ ] Staging database used
- [ ] Test domain configured

### Production Environment
- [ ] DEBUG=False for security
- [ ] Live Stripe keys configured
- [ ] Production email settings
- [ ] Production database
- [ ] Live domain with SSL
- [ ] Performance monitoring active

## Tools and Commands

### Useful Commands
```bash
# Check deployment readiness
python manage.py check --deploy

# Test database connection
python manage.py check_db

# Collect static files
python manage.py collectstatic --noinput

# Run security check
python -m bandit -r . -x ./venv/

# Check for vulnerabilities
pip-audit
```

### Monitoring URLs
- Production: https://www.quantumtaskai.com/health/
- Staging: https://staging-quantumtaskai.railway.app/health/
- Railway Dashboard: https://railway.app/dashboard

---

**Remember**: When in doubt, test on staging first! 🧪