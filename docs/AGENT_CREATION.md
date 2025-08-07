# Agent Creation Guide

This guide provides comprehensive instructions for adding new agents to the Quantum Tasks AI platform.

## Overview

Quantum Tasks AI supports **TWO DISTINCT AGENT SYSTEMS**:

- **Webhook Agents** - N8N integrations for complex processing with dynamic forms
- **Direct Access Agents** - External form services (JotForm, Google Forms) with embedded interfaces

**⚡ RECOMMENDED APPROACH:** Use JSON configuration + `populate_agents` command for error-free, Railway-ready agent creation.

---

## Current Agent Status

**Total Agents: 8** (4 webhook + 4 direct access)  
**Total Categories: 6**

### Webhook Agents (N8N Integration)
1. **Social Ads Generator** - 6.00 AED - Creates social media advertisements
2. **Job Posting Generator** - 10.00 AED - Creates professional job postings  
3. **PDF Summarizer** - 8.00 AED - Analyzes and summarizes PDF documents
4. **5 Whys Analyzer** - 15.00 AED - Interactive chat-based root cause analysis

### Direct Access Agents (External Forms)
1. **CyberSec Career Navigator** - FREE - Career guidance consultation
2. **AI Brand Strategist** - FREE - Brand strategy consultation  
3. **Lean Six Sigma Expert** - FREE - Process improvement consultation
4. **SWOT Analysis Expert** - FREE - Strategic business analysis

---

## 🏷️ Choose Existing Category First

**IMPORTANT:** Always use existing categories before creating new ones to avoid category proliferation.

### Available Categories:
- 🧠 **`analysis`** - Problem-solving, SWOT analysis, strategic analysis tools
- 🎓 **`career-education`** - Career guidance, educational resources, professional development
- 📄 **`document-processing`** - PDF analysis, file processing, document tools
- 💼 **`human-resources`** - Job postings, HR automation, talent management
- 📢 **`marketing`** - Social ads, branding, content marketing, advertising
- 💼 **`consulting`** - Business consultation, strategy services, expert advice

**Only create new categories when absolutely necessary and logically distinct.**

---

## 🚀 Agent Creation Workflow

### System 1: Webhook Agents (N8N Integration)
- **Use for:** Dynamic forms, server-side processing, file uploads, complex workflows
- **Examples:** Social Ads Generator, PDF Summarizer, Job Posting Generator
- **Flow:** Marketplace → Agent detail page → Dynamic form → N8N webhook → Results

### System 2: Direct Access Agents (External Forms)
- **Use for:** External form services (JotForm, Google Forms), consultation interfaces
- **Examples:** SWOT Analysis Expert, CyberSec Career Navigator, AI Brand Strategist
- **Flow:** Marketplace → Payment processing → Quantum Tasks header + embedded external form

---

## 📝 Implementation Steps

### Step 1: Create JSON Configuration

Create a new file in `agents/configs/agents/your-agent-name.json`:

#### Webhook Agent Example:
```json
{
  "slug": "content-optimizer",
  "name": "Content Optimizer",
  "short_description": "AI-powered content optimization and enhancement",
  "description": "Enhance your content for better engagement with AI-powered optimization suggestions, tone analysis, and improvement recommendations.",
  "category": "marketing",
  "price": 5.0,
  "agent_type": "form",
  "system_type": "webhook",
  "form_schema": {
    "fields": [
      {
        "name": "content",
        "type": "textarea",
        "label": "Content to Optimize",
        "required": true
      },
      {
        "name": "content_type",
        "type": "select",
        "label": "Content Type",
        "required": true,
        "options": [
          {"value": "blog", "label": "Blog Post"},
          {"value": "social", "label": "Social Media"},
          {"value": "email", "label": "Email Marketing"}
        ]
      }
    ]
  },
  "webhook_url": "http://localhost:5678/webhook/content-optimizer",
  "access_url_name": "",
  "display_url_name": ""
}
```

#### Direct Access Agent Example:
```json
{
  "slug": "business-strategist",
  "name": "Business Strategist",
  "short_description": "Expert business strategy consultation",
  "description": "Get professional business strategy insights and recommendations from experienced consultants to grow your business effectively.",
  "category": "consulting",
  "price": 0.0,
  "agent_type": "form",
  "system_type": "direct_access",
  "form_schema": {
    "fields": []
  },
  "webhook_url": "https://agent.jotform.com/your-form-id",
  "access_url_name": "agents:direct_access_handler",
  "display_url_name": "agents:direct_access_display"
}
```

### Step 2: Run populate_agents Command

```bash
# Development
source venv/bin/activate
python manage.py populate_agents

# Production (Railway)
python manage.py populate_agents  # Runs automatically on deployment
```

### Step 3: Additional Setup (Direct Access Agents Only)

For direct access agents that need custom templates or marketplace integration:

#### 3a. Create Custom Template (optional):
```html
<!-- templates/your_agent_name.html -->
{% extends 'base.html' %}
{% load static %}

{% block title %}Your Agent Name - Quantum Tasks AI{% endblock %}

{% block extra_css %}
<style>
.main-container { max-width: none; padding: 0; height: calc(100vh - 80px); }
.iframe-container { width: 100%; height: 100%; }
.iframe-container iframe { width: 100%; height: 100%; border: none; display: block; }
.footer { display: none !important; }
</style>
{% endblock %}

{% block content %}
<div class="iframe-container">
    <iframe src="{{ form_url }}" frameborder="0" scrolling="auto" title="Your Agent Name"></iframe>
</div>
{% endblock %}
```

#### 3b. Add Custom Views (if needed):
Add view functions to `agents/views.py` following the pattern of existing direct access agents.

#### 3c. Add URL Routes (if needed):
Add routes to `agents/urls.py` following the pattern of existing direct access agents.

#### 3d. Update Marketplace Template (if needed):
Add button logic to `agents/templates/agents/marketplace.html` for custom marketplace behavior.

**⚠️ Important**: Keep all "Try Now" buttons consistent with the format `Try Now →` (no icons or emojis).

### Step 4: Setup External Services

#### For Webhook Agents:
- Create N8N workflow at the webhook URL
- Configure webhook to accept JSON payload with `sessionId`, `message`, etc.

#### For Direct Access Agents:
- Create external form (JotForm, Google Forms, etc.)
- Ensure form URL is accessible and properly configured

---

## ✅ Benefits of This Approach

- ✅ **Single source of truth** - JSON configs define everything
- ✅ **Railway-ready immediately** - No manual database setup needed
- ✅ **Error-free** - No category creation mistakes or typos
- ✅ **Consistent** - All agents use same reliable creation process
- ✅ **Scalable** - Easy to add 100+ agents
- ✅ **Version controlled** - Configs are tracked in git

---

## 🔧 Supported Form Field Types (Webhook Agents)

- `text` - Single-line text input
- `textarea` - Multi-line text input  
- `select` - Dropdown with options array
- `file` - File upload with drag-and-drop
- `url` - URL input with validation
- `checkbox` - Boolean checkbox

---

## ⚠️ Common Mistakes to Avoid

1. **Creating unnecessary categories** - Use existing ones first
2. **Missing system_type** - Include "webhook" or "direct_access" 
3. **Wrong access_url_name** - Empty for webhook agents, populated for direct access
4. **Forgetting populate_agents** - Run after creating JSON config
5. **Complex custom commands** - Use JSON + populate_agents instead
6. **Adding icons to Try Now buttons** - Keep all marketplace buttons consistent with "Try Now →" format

---

## 🔄 Agent Management Commands

### Essential Commands:
```bash
# Populate all agents from JSON configs (main command)
python manage.py populate_agents

# Clean up expired chat sessions
python manage.py cleanup_expired_sessions
```

### Development Workflow:
1. Create JSON config file
2. Run `populate_agents` 
3. Test agent functionality
4. Commit changes to git
5. Deploy to Railway (auto-runs populate_agents)

---

## 📊 Agent Configuration Reference

### Required JSON Fields:
- `slug` - URL-friendly identifier (kebab-case)
- `name` - Display name  
- `short_description` - Brief description for marketplace
- `description` - Full description with details
- `category` - Must match existing category slug
- `price` - Price in AED (0.0 for free agents)
- `agent_type` - Always "form" 
- `system_type` - "webhook" or "direct_access"

### System-Specific Fields:

#### Webhook Agents:
- `form_schema` - JSON schema defining form fields
- `webhook_url` - N8N webhook endpoint
- `access_url_name` - Empty string ""
- `display_url_name` - Empty string ""

#### Direct Access Agents:
- `form_schema` - Usually `{"fields": []}`
- `webhook_url` - External form URL (JotForm, etc.)
- `access_url_name` - "agents:direct_access_handler" 
- `display_url_name` - "agents:direct_access_display"

---

## 🚀 Railway Deployment

When you commit changes to the repository:

1. ✅ **Railway auto-deploys** new code
2. ✅ **populate_agents runs automatically** on deployment
3. ✅ **New agents appear** in production marketplace
4. ✅ **Categories are created** if needed (but use existing ones first!)
5. ✅ **No manual database work** required

---

## 📞 Support & Documentation

- **Main Documentation**: See `CLAUDE.md` for project overview
- **Agent Issues**: Check Railway logs and database for agent status
- **Form Problems**: Verify external form URLs are accessible
- **Category Issues**: Use existing categories from the list above

---

*Last updated: 2025-01-08*