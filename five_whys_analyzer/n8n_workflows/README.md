# Five Whys Analyzer Agent - N8N Workflow

## Overview
This directory contains the N8N workflow configuration for the Five Whys Analyzer Agent, which conducts systematic root cause analysis using the proven Five Whys methodology.

## Workflow Files
- `workflow.json` - Production workflow for N8N import
- `workflow_dev.json` - Development/testing version (optional)
- `workflow_backup.json` - Backup version for disaster recovery

## Webhook Configuration
- **Webhook URL**: Configured via `N8N_WEBHOOK_FIVE_WHYS` environment variable
- **HTTP Method**: POST
- **Expected Data Format**:
  ```json
  {
    "problem": "Website conversion rate dropped by 30%",
    "context": "E-commerce site, occurred after recent update",
    "industry": "retail",
    "stakeholders": ["marketing team", "dev team", "customers"],
    "additional_info": "Peak season, mobile traffic increased"
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
2. Set environment variable: `N8N_WEBHOOK_FIVE_WHYS=https://your-n8n.com/webhook/five-whys`
3. Restart your Django application

### 3. Test the Workflow
```bash
# Test via Django application
python manage.py test_webhook five_whys_analyzer

# Or test directly via curl
curl -X POST https://your-n8n.com/webhook/five-whys \
  -H "Content-Type: application/json" \
  -d '{"problem":"Customer complaints increased","context":"After product launch","industry":"saas"}'
```

## Workflow Components
- **Webhook Node**: Receives requests from Django application
- **Problem Analysis**: Systematic Five Whys questioning process
- **AI Processing**: Uses OpenAI GPT-4 for intelligent analysis
- **Root Cause Identification**: Identifies underlying causes
- **Action Planning**: Generates actionable recommendations
- **Response Node**: Returns structured analysis results
- **Error Handling**: Manages analysis failures and edge cases

## Expected Response Format
```json
{
  "success": true,
  "analysis": {
    "problem_statement": "Website conversion rate dropped by 30%",
    "five_whys_sequence": [
      {
        "question": "Why did the conversion rate drop?",
        "answer": "Users are abandoning checkout process"
      },
      {
        "question": "Why are users abandoning checkout?",
        "answer": "Page loading times increased significantly"
      },
      {
        "question": "Why did loading times increase?",
        "answer": "New payment integration is slow"
      },
      {
        "question": "Why is the payment integration slow?",
        "answer": "Third-party API has latency issues"
      },
      {
        "question": "Why wasn't this tested before deployment?",
        "answer": "Load testing didn't include payment flow"
      }
    ],
    "root_causes": [
      "Inadequate load testing procedures",
      "Third-party API performance issues",
      "Missing performance monitoring for payment flow"
    ],
    "immediate_actions": [
      "Switch to backup payment provider",
      "Optimize payment integration code",
      "Add performance monitoring"
    ],
    "long_term_solutions": [
      "Implement comprehensive load testing",
      "Establish SLA requirements for third parties",
      "Create performance regression testing"
    ],
    "prevention_strategies": [
      "Include all critical paths in testing",
      "Monitor third-party dependencies",
      "Establish performance baselines"
    ]
  },
  "confidence_level": "high",
  "recommended_timeline": "immediate: 1-2 days, long-term: 2-4 weeks"
}
```

## Analysis Categories
- **Technical Issues**: Software bugs, performance problems
- **Process Problems**: Workflow inefficiencies, communication gaps
- **Human Factors**: Training gaps, resource constraints
- **External Factors**: Market changes, supplier issues
- **System Issues**: Infrastructure, tools, technology stack

## Industry Applications
- Software Development (bugs, performance)
- Manufacturing (quality issues, downtime)
- Customer Service (complaint resolution)
- Marketing (campaign performance)
- Operations (process inefficiencies)
- Sales (conversion problems)

## Troubleshooting
- **Shallow analysis**: Provide more context and stakeholder info
- **Generic recommendations**: Include industry-specific details
- **Missing root causes**: Ensure problem description is comprehensive
- **Incomplete action items**: Specify timeline and resource constraints

## Best Practices
- Provide comprehensive problem context
- Include all relevant stakeholders
- Specify industry for targeted analysis
- Be specific about problem symptoms
- Include timeline and impact information
- Follow up on recommended actions
- Document lessons learned for future reference