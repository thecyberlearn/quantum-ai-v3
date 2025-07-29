"""
Simplified agent configuration system for unified workflows app.
Each agent is defined by essential metadata only - forms are handled in individual templates.
"""

AGENT_CONFIGS = {
    'social-ads-generator': {
        'name': 'Social Ads Generator',
        'description': 'Create engaging social media advertisements with AI-powered content generation',
        'price': 6.0,
        'icon': '📱',
        'webhook_url': 'http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d',
    },
    
    'job-posting-generator': {
        'name': 'Job Posting Generator',
        'description': 'Create professional job postings that attract top talent',
        'price': 10.0,
        'icon': '💼',
        'webhook_url': 'http://localhost:5678/webhook/43f84411-eaaa-488c-9b1f-856e90d0aaf6',
    },
    
    'data-analyzer': {
        'name': 'Data Analyzer',
        'description': 'AI-powered analysis of your data files with comprehensive insights',
        'price': 8.0,
        'icon': '📊',
        'webhook_url': 'http://localhost:5678/webhook/simple-pdf-processor',
    },
}


def get_agent_config(agent_slug):
    """Get agent configuration by slug"""
    return AGENT_CONFIGS.get(agent_slug)


def get_all_agents():
    """Get all available agent configurations"""
    return AGENT_CONFIGS


def get_available_agents():
    """Get all agents formatted for navigation components"""
    return {
        slug: {
            'name': config['name'],
            'icon': config['icon'],
            'description': config['description']
        }
        for slug, config in AGENT_CONFIGS.items()
    }


def format_message_for_n8n(agent_slug, form_data):
    """Format form data into message for N8N webhook"""
    config = get_agent_config(agent_slug)
    if not config:
        return None
    
    # Simple format - just send the form data as is
    return f"Process {config['name']} request: {str(form_data)}"