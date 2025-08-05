# Agent Configuration System

This directory contains JSON configuration files for dynamically creating agents and categories in the Quantum Tasks AI platform.

## Directory Structure

```
agents/configs/
├── categories/
│   └── categories.json          # All agent categories
├── agents/
│   ├── ai-brand-strategist.json        # Direct access agent
│   ├── cybersec-career-navigator.json  # Direct access agent
│   ├── five-whys-analysis.json         # Chat webhook agent
│   ├── job-posting-generator.json      # Form webhook agent
│   ├── pdf-summarizer.json             # File upload webhook agent
│   └── social-ads-generator.json       # Form webhook agent
└── README.md                    # This file
```

## How It Works

1. **Categories** are defined in `categories/categories.json`
2. **Agents** are defined in individual JSON files in `agents/`
3. Run `python manage.py populate_agents` to create all agents from configs
4. **Adding new agents** is as simple as creating a new JSON file

## Adding New Agents

### Step 1: Create JSON Configuration File

Create a new file in `agents/` directory, e.g., `email-writer.json`:

```json
{
  "slug": "email-writer",
  "name": "Email Writer",
  "short_description": "AI-powered professional email writing assistant",
  "description": "Generate professional emails for any purpose with AI assistance.",
  "category": "marketing",
  "price": 3.0,
  "agent_type": "form",
  "system_type": "webhook",
  "form_schema": {
    "fields": [
      {
        "name": "email_type",
        "type": "select",
        "label": "Email Type",
        "required": true,
        "options": [
          {"value": "business", "label": "Business Email"},
          {"value": "marketing", "label": "Marketing Email"}
        ]
      }
    ]
  },
  "webhook_url": "http://localhost:5678/webhook/email-writer",
  "access_url_name": "",
  "display_url_name": ""
}
```

### Step 2: Run Population Command

```bash
python manage.py populate_agents
```

### Step 3: Agent Appears Automatically

The agent will now appear in the marketplace with the configured settings.

## Agent Types

### Webhook Agents (N8N Integration)
- Set `system_type`: `"webhook"`
- Include detailed `form_schema` with fields
- Set `webhook_url` to N8N endpoint
- Leave `access_url_name` and `display_url_name` empty

### Direct Access Agents (External Forms)
- Set `system_type`: `"direct_access"`
- Set `form_schema`: `{"fields": []}`
- Set `webhook_url` to external form URL (JotForm, etc.)
- Set `access_url_name`: `"agents:direct_access_handler"`
- Set `display_url_name`: `"agents:direct_access_display"`

## Field Types for Webhook Agents

- `text`: Single-line text input
- `textarea`: Multi-line text input  
- `select`: Dropdown with options array
- `file`: File upload with drag-and-drop
- `url`: URL input with validation
- `checkbox`: Boolean checkbox

## Benefits

✅ **Scalable**: Add 100+ agents without code changes
✅ **Version Controlled**: All agent definitions in git
✅ **Consistent**: Ensures local and Railway databases match
✅ **Simple**: Just create JSON file and run command
✅ **Validated**: Built-in validation and error handling

## Railway Deployment

On Railway, just run:
```bash
python manage.py populate_agents
```

All agents defined in JSON files will be created automatically, ensuring Railway marketplace shows all agents consistently.