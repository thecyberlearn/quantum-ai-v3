# 🚀 Railway.app Deployment Guide for Quantum Tasks AI

## Overview
This guide will help you deploy your Quantum Tasks AI Django application to Railway.app. Your application is already optimized for Railway deployment with the existing `railway.json` configuration.

### 🏗️ Architecture Overview (Important!)

**What Deploys to Railway:**
- ✅ Django Application (Quantum Tasks AI)
- ✅ PostgreSQL Database (automatic)
- ✅ Redis Cache (optional but recommended)

**What DOES NOT Deploy to Railway:**
- ❌ N8N Instance (runs on separate server)
- ❌ N8N Workflows (hosted elsewhere)

**How They Connect:**
```
Railway Django App → HTTP POST Requests → N8N Instance (Separate Hosting) → AI Processing → Response → Railway Django App
```

Your Django app only needs the N8N webhook URLs as environment variables to connect to your separately-hosted N8N instance.

## 📋 Pre-Deployment Checklist

### Required Accounts & Services
- [ ] GitHub account with your repository
- [ ] Railway.app account (free signup)
- [ ] Stripe account for payments (test/live keys)
- [ ] Gmail or SMTP service for emails
- [ ] N8N instance for AI agent webhooks

### Code Verification
- [ ] Latest code pushed to GitHub
- [ ] All migrations created and committed
- [ ] `railway.json` file present in root directory
- [ ] Environment variables documented in `.env.example`

## 🔧 Step-by-Step Deployment

### Step 1: Connect to Railway
1. Visit [railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `quantum_ai` repository
4. Railway will automatically detect Django and start building

### Step 2: Configure Environment Variables
Navigate to your project settings and add these environment variables:

#### 🔐 Security Settings
```bash
SECRET_KEY=your-50-character-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,quantumtaskai.com
CSRF_TRUSTED_ORIGINS=https://your-domain.railway.app,https://quantumtaskai.com
```

#### 📧 Email Configuration  
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Quantum Tasks AI <noreply@quantumtaskai.com>
```

#### 💳 Stripe Configuration
```bash
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

#### 🤖 N8N Webhook URLs
```bash
N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n.com/webhook/data-analyzer
N8N_WEBHOOK_FIVE_WHYS=https://your-n8n.com/webhook/five-whys
N8N_WEBHOOK_JOB_POSTING=https://your-n8n.com/webhook/job-posting
N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n.com/webhook/social-ads
```

**Note**: Only webhook-based agents need N8N workflows. API-based agents (weather_reporter, email_writer) work independently.

#### 🗄️ Database Configuration
Railway automatically provides `DATABASE_URL` - no manual configuration needed!

#### ⚡ Redis Configuration (Optional but Recommended)
```bash
REDIS_URL=redis://your-redis-url:6379
```

### Step 3: Add PostgreSQL Database
1. In your Railway project dashboard
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway automatically sets the `DATABASE_URL` environment variable

### Step 4: Add Redis (Recommended)
1. Click "New" → "Database" → "Add Redis"
2. Railway automatically sets the `REDIS_URL` environment variable

### Step 5: Set Up N8N Instance (Separate Hosting)

⚠️ **IMPORTANT**: N8N is NOT deployed to Railway with your Django app. N8N runs on a separate server and your Django app connects to it via webhooks.

#### Architecture Overview:
```
User → Django App (Railway) → HTTP POST → N8N Webhooks (Separate Server) → AI Processing → Response → Django → User
```

#### N8N Hosting Options (Choose One):

**Option A: N8N Cloud (Recommended - Easiest)**
1. Sign up at [n8n.cloud](https://n8n.cloud)
2. Create a new workflow instance
3. Import your workflow JSON files
4. Copy webhook URLs for environment variables

**Option B: Deploy N8N on Railway (Separate Project)**
1. Create a NEW Railway project (separate from your Django app)
2. Deploy N8N using Railway's N8N template
3. Configure OpenAI API credentials in N8N
4. Import workflows and get webhook URLs

**Option C: Self-Hosted N8N**
1. Deploy N8N on DigitalOcean, AWS, or VPS
2. Use Docker: `docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n`
3. Configure and import workflows
4. Ensure server is publicly accessible for webhooks

#### Deploy Workflows to Your N8N Instance:
```bash
# Set connection details for YOUR N8N instance
export N8N_BASE_URL=https://your-n8n-instance.com  # Your N8N URL
export N8N_API_KEY=your-api-key                    # Your N8N API key

# Deploy all workflows to your N8N instance
./deploy_n8n_workflows.sh
```

#### Configure Django App to Connect to N8N:
1. Copy webhook URLs from your N8N instance
2. Add these URLs to your Railway Django project environment variables:
   ```
   N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n.com/webhook/data-analyzer
   N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n.com/webhook/social-ads
   N8N_WEBHOOK_JOB_POSTING=https://your-n8n.com/webhook/job-posting
   N8N_WEBHOOK_FIVE_WHYS=https://your-n8n.com/webhook/five-whys
   ```
3. Verify workflows are active in your N8N instance

### Step 6: Custom Domain (Optional)
1. Go to project Settings → Domains
2. Add your custom domain (e.g., `quantumtaskai.com`)
3. Update DNS records as instructed by Railway
4. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` environment variables

## 🔍 Post-Deployment Verification

### Health Check
Visit your deployed application health endpoint:
```
https://your-domain.railway.app/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "version": "1.0",
  "checks": {
    "database": {"status": "healthy", "response_time_ms": 2.5},
    "agents": {"status": "healthy", "active_count": 7}
  },
  "response_time_ms": 5.2
}
```

### Application Testing
- [ ] Homepage loads correctly (`/`)
- [ ] User registration works (`/auth/register/`)
- [ ] Login functionality (`/auth/login/`)
- [ ] Marketplace displays agents (`/marketplace/`)
- [ ] Payment system functional (Stripe webhooks)
- [ ] Contact form submits successfully (`/contact/`)
- [ ] Admin panel accessible (`/admin/`)

### Monitoring Setup
1. **Application Logs**: Available in Railway dashboard
2. **Health Monitoring**: Set up external monitoring to ping `/health/`
3. **Error Tracking**: Monitor Railway application logs
4. **Database Performance**: Use Railway's built-in database metrics

## 🚨 Troubleshooting

### Common Issues & Solutions

#### Migration Errors
```bash
# If you see migration conflicts, check Railway logs
# Your railway.json already handles complex migrations
```

#### Static Files Not Loading
```bash
# Already handled by WhiteNoise configuration
# Verify STATIC_URL and STATIC_ROOT in settings
```

#### Environment Variable Issues
```bash
# Check Railway project settings
# Ensure all required variables are set
# Restart deployment after adding variables
```

#### Database Connection Issues
```bash
# Verify PostgreSQL service is running in Railway
# Check DATABASE_URL is automatically set
# Review connection logs in Railway dashboard
```

## 📊 Cost Estimation

### Railway.app Pricing (Monthly)
- **Web Service**: $5/month (scales with usage)
- **PostgreSQL**: $5/month (1GB storage, scales up)
- **Redis**: $5/month (256MB, scales up)
- **Bandwidth**: $0.10/GB (generous free tier)

**Total Estimated Cost**: $15-25/month for production usage

### Scaling Thresholds
- **Free Tier**: Good for development and testing
- **Scale Up**: When you hit 1000+ daily active users
- **Database**: Scales automatically with your data growth

## 🔒 Security Best Practices

### Environment Variables
- Never commit real environment variables to Git
- Use Railway's environment variable encryption
- Rotate API keys regularly (Stripe, email, N8N)

### Domain Security
- Always use HTTPS (Railway provides SSL automatically)
- Configure proper CORS settings
- Monitor your `/health/` endpoint for unauthorized access

### Database Security
- Railway PostgreSQL is automatically encrypted
- Enable database backups (Railway provides automatic backups)
- Monitor database performance and queries

## 📈 Performance Optimization

### Railway-Specific Optimizations
1. **Region Selection**: Choose region closest to your users
2. **Resource Allocation**: Monitor CPU/memory usage in dashboard
3. **Caching**: Redis is automatically configured for session caching
4. **Static Files**: WhiteNoise serves static files efficiently

### Monitoring & Alerts
1. Set up monitoring for your `/health/` endpoint
2. Configure alerts for high error rates
3. Monitor database performance metrics
4. Track user registration and payment success rates

## 🎉 Success!

Once deployed successfully, your Quantum Tasks AI application will be live at:
- **Production URL**: `https://your-domain.railway.app`
- **Custom Domain**: `https://quantumtaskai.com` (if configured)
- **Health Check**: `https://your-domain.railway.app/health/`
- **Admin Panel**: `https://your-domain.railway.app/admin/`

Your AI agent marketplace is now ready to serve users worldwide! 🌍

## 📞 Support

If you encounter issues:
1. Check Railway application logs first
2. Verify all environment variables are set correctly
3. Test the `/health/` endpoint for system status
4. Review this deployment guide for common solutions

Railway.app provides excellent documentation and support for Django applications.