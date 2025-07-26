# Data Analyzer Agent - N8N Workflow

## Overview
This directory contains the N8N workflow configuration for the Data Analyzer Agent, which processes uploaded files (CSV, Excel, PDF) and provides intelligent data analysis.

## Workflow Files
- `workflow.json` - Production workflow for N8N import
- `workflow_dev.json` - Development/testing version (optional)
- `workflow_backup.json` - Backup version for disaster recovery

## Webhook Configuration
- **Webhook URL**: Configured via `N8N_WEBHOOK_DATA_ANALYZER` environment variable
- **HTTP Method**: POST
- **Expected Data Format**:
  ```json
  {
    "file_name": "data.csv",
    "file_content": "base64_encoded_content",
    "analysis_type": "statistical",
    "user_request": "Analyze sales trends"
  }
  ```

## Setup Instructions

### 1. Import Workflow to N8N
1. Open your N8N instance
2. Click "Import from File" or "Import from URL"
3. Upload the `workflow.json` file
4. Configure credentials (OpenAI API key, etc.)
5. Activate the workflow

### 2. Configure Webhook URL
1. Copy the webhook URL from N8N
2. Set environment variable: `N8N_WEBHOOK_DATA_ANALYZER=https://your-n8n.com/webhook/data-analyzer`
3. Restart your Django application

### 3. Test the Workflow
```bash
# Test via Django application
python manage.py test_webhook data_analyzer

# Or test directly via curl
curl -X POST https://your-n8n.com/webhook/data-analyzer \
  -H "Content-Type: application/json" \
  -d '{"file_name":"test.csv","file_content":"dGVzdA==","analysis_type":"basic"}'
```

## Workflow Components
- **Webhook Node**: Receives requests from Django application
- **AI Processing**: Uses OpenAI GPT-4 for data analysis
- **Response Node**: Returns structured analysis results
- **Error Handling**: Manages failures and timeouts

## Expected Response Format
```json
{
  "success": true,
  "analysis": {
    "summary": "Data analysis summary",
    "insights": ["Key insight 1", "Key insight 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "charts": [{"type": "bar", "data": {...}}]
  },
  "processing_time": 1.5
}
```

## Troubleshooting
- **Webhook not responding**: Check N8N workflow is active and URL is correct
- **Authentication errors**: Verify OpenAI API credentials in N8N
- **Timeout issues**: Increase workflow timeout settings for large files
- **Rate limiting**: Monitor OpenAI API usage limits

## Maintenance
- Regularly backup workflow configurations
- Monitor workflow execution logs in N8N
- Update AI prompts based on user feedback
- Scale webhook handling based on usage patterns