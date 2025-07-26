#!/bin/bash

# N8N Workflow Deployment Script for Quantum Tasks AI
# This script helps deploy N8N workflows during application deployment

set -e

echo "🚀 Deploying N8N Workflows for Quantum Tasks AI"
echo "================================================="

# Check environment variables
if [ -z "$N8N_BASE_URL" ]; then
    echo "⚠️  N8N_BASE_URL not set, using default: http://localhost:5678"
    export N8N_BASE_URL="http://localhost:5678"
fi

if [ -z "$N8N_API_KEY" ]; then
    echo "⚠️  N8N_API_KEY not set - some operations may fail"
fi

# Check if Python script exists
if [ ! -f "manage_n8n_workflows.py" ]; then
    echo "❌ manage_n8n_workflows.py not found"
    exit 1
fi

# List available workflows
echo "📋 Checking available workflows..."
python3 manage_n8n_workflows.py list

echo ""
echo "🔄 Starting workflow sync..."

# Sync all workflows
python3 manage_n8n_workflows.py sync

echo ""
echo "💾 Creating backup of current workflows..."

# Create backup
python3 manage_n8n_workflows.py backup

echo ""
echo "✅ N8N workflow deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Verify workflows are active in your N8N instance"
echo "2. Test webhook endpoints with your Django application"
echo "3. Monitor workflow execution logs"
echo ""
echo "🔗 Webhook URLs should be configured in environment variables:"
echo "   - N8N_WEBHOOK_DATA_ANALYZER"
echo "   - N8N_WEBHOOK_SOCIAL_ADS"
echo "   - N8N_WEBHOOK_JOB_POSTING"
echo "   - N8N_WEBHOOK_FIVE_WHYS"