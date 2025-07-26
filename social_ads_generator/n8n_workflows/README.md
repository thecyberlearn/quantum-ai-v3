# Social Ads Generator Agent - N8N Workflow

## Overview
This directory contains the N8N workflow configuration for the Social Ads Generator Agent, which creates compelling social media advertisements for various platforms.

## Workflow Files
- `workflow.json` - Production workflow for N8N import
- `workflow_dev.json` - Development/testing version (optional)
- `workflow_backup.json` - Backup version for disaster recovery

## Webhook Configuration
- **Webhook URL**: Configured via `N8N_WEBHOOK_SOCIAL_ADS` environment variable
- **HTTP Method**: POST
- **Expected Data Format**:
  ```json
  {
    "platform": "facebook",
    "product": "AI Marketing Tool",
    "audience": "small business owners",
    "tone": "professional",
    "features": ["automation", "analytics", "ROI tracking"],
    "requirements": "Include call-to-action"
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
2. Set environment variable: `N8N_WEBHOOK_SOCIAL_ADS=https://your-n8n.com/webhook/social-ads`
3. Restart your Django application

### 3. Test the Workflow
```bash
# Test via Django application
python manage.py test_webhook social_ads_generator

# Or test directly via curl
curl -X POST https://your-n8n.com/webhook/social-ads \
  -H "Content-Type: application/json" \
  -d '{"platform":"instagram","product":"Coffee Shop","audience":"coffee lovers","tone":"casual"}'
```

## Workflow Components
- **Webhook Node**: Receives requests from Django application
- **AI Processing**: Uses OpenAI GPT-4 for ad content generation
- **Platform Optimization**: Tailors content for specific social media platforms
- **Response Node**: Returns structured ad content
- **Error Handling**: Manages failures and content generation issues

## Expected Response Format
```json
{
  "success": true,
  "ad_content": {
    "headline": "Transform Your Business with AI",
    "body": "Discover how AI can revolutionize your marketing...",
    "call_to_action": "Start Free Trial",
    "hashtags": ["#AI", "#Marketing", "#Business"],
    "image_suggestions": ["professional team", "modern office"],
    "target_audience": "business professionals aged 25-45"
  },
  "platform_specs": {
    "character_limit": 280,
    "recommended_format": "image_post"
  }
}
```

## Supported Platforms
- Facebook/Meta
- Instagram
- Twitter/X
- LinkedIn
- Google Ads
- TikTok
- Pinterest

## Troubleshooting
- **Content not platform-optimized**: Check platform parameter is correct
- **Generic content**: Provide more specific product/audience details
- **API rate limits**: Monitor OpenAI usage and implement queuing
- **Webhook timeouts**: Optimize prompts for faster generation

## Best Practices
- Provide detailed product descriptions for better results
- Specify target audience demographics clearly
- Test generated content before publishing
- A/B test different tone variations
- Monitor ad performance and adjust prompts accordingly