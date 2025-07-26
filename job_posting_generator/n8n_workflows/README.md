# Job Posting Generator Agent - N8N Workflow

## Overview
This directory contains the N8N workflow configuration for the Job Posting Generator Agent, which creates comprehensive, professional job postings that attract qualified candidates.

## Workflow Files
- `workflow.json` - Production workflow for N8N import
- `workflow_dev.json` - Development/testing version (optional)
- `workflow_backup.json` - Backup version for disaster recovery

## Webhook Configuration
- **Webhook URL**: Configured via `N8N_WEBHOOK_JOB_POSTING` environment variable
- **HTTP Method**: POST
- **Expected Data Format**:
  ```json
  {
    "position": "Senior Python Developer",
    "company": "Tech Startup Inc",
    "location": "New York, NY",
    "experience_level": "senior",
    "salary_range": "$120,000 - $150,000",
    "responsibilities": ["API development", "Team leadership"],
    "skills": ["Python", "Django", "PostgreSQL"],
    "industry": "fintech"
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
2. Set environment variable: `N8N_WEBHOOK_JOB_POSTING=https://your-n8n.com/webhook/job-posting`
3. Restart your Django application

### 3. Test the Workflow
```bash
# Test via Django application
python manage.py test_webhook job_posting_generator

# Or test directly via curl
curl -X POST https://your-n8n.com/webhook/job-posting \
  -H "Content-Type: application/json" \
  -d '{"position":"Software Engineer","company":"Acme Corp","location":"Remote","experience_level":"mid"}'
```

## Workflow Components
- **Webhook Node**: Receives requests from Django application
- **AI Processing**: Uses OpenAI GPT-4 for job posting generation
- **Industry Optimization**: Tailors language for specific industries
- **Compliance Check**: Ensures legal compliance and inclusive language
- **Response Node**: Returns structured job posting content
- **Error Handling**: Manages generation failures and validation errors

## Expected Response Format
```json
{
  "success": true,
  "job_posting": {
    "title": "Senior Python Developer",
    "company_overview": "Join our innovative fintech startup...",
    "job_description": "We are seeking an experienced Python developer...",
    "key_responsibilities": [
      "Design and implement scalable APIs",
      "Lead technical discussions and code reviews",
      "Mentor junior developers"
    ],
    "requirements": {
      "required": ["5+ years Python experience", "Django framework"],
      "preferred": ["PostgreSQL", "AWS experience", "Team leadership"]
    },
    "benefits": [
      "Competitive salary and equity",
      "Health, dental, vision insurance",
      "Flexible work arrangements"
    ],
    "application_instructions": "Send resume and cover letter to...",
    "equal_opportunity_statement": "We are an equal opportunity employer..."
  },
  "seo_keywords": ["python developer", "django", "fintech"],
  "posting_platforms": ["linkedin", "indeed", "glassdoor"]
}
```

## Industry Specializations
- Technology/Software
- Healthcare
- Finance/Fintech
- Marketing/Advertising
- Manufacturing
- Education
- Non-profit
- Government

## Compliance Features
- Equal opportunity language
- ADA compliance considerations
- Salary transparency requirements
- Location-specific labor law compliance
- Inclusive language recommendations

## Troubleshooting
- **Generic postings**: Provide more company and role specifics
- **Compliance warnings**: Review generated content for bias
- **Missing requirements**: Ensure all mandatory fields are provided
- **Industry mismatch**: Verify industry parameter is correct

## Best Practices
- Provide detailed company culture information
- Specify exact technical requirements
- Include growth opportunities and career path
- Use inclusive, welcoming language
- Optimize for relevant job board algorithms
- A/B test different posting variations