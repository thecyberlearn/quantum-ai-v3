"""
Simplified agent configuration system for unified workflows app.
Each agent is defined by essential metadata only - forms are handled in individual templates.
"""

AGENT_CONFIGS = {
    'social-ads-generator': {
        'name': 'Social Ads Generator',
        'description': 'Create engaging social media advertisements with AI-powered content generation',
        'category': 'marketing',
        'price': 5.0,
        'icon': '📱',
        'webhook_url': 'http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d',
    },
    
    'data-analyzer': {
        'name': 'Data Analyzer',
        'description': 'Upload and analyze data files with AI-powered insights and visualizations',
        'category': 'analytics',
        'price': 3.0,
        'icon': '📊',
        'webhook_url': 'http://localhost:5678/webhook/data-analyzer-webhook-id',
    },
    
    'job-posting-generator': {
        'name': 'Job Posting Generator',
        'description': 'Create professional job postings that attract top talent',
        'category': 'content',
        'price': 4.0,
        'icon': '💼',
        'webhook_url': 'http://localhost:5678/webhook/job-posting-webhook-id',
    },
    
    'five-whys-analyzer': {
        'name': 'Five Whys Analyzer',
        'description': 'Perform root cause analysis using the Five Whys methodology',
        'category': 'analytics',
        'price': 2.5,
        'icon': '🔍',
        'webhook_url': 'http://localhost:5678/webhook/five-whys-webhook-id',
    },
    
    'weather-reporter': {
        'name': 'Weather Reporter',
        'description': 'Get detailed weather reports and forecasts for any location',
        'category': 'utilities',
        'price': 1.0,
        'icon': '🌤️',
        'webhook_url': 'http://localhost:5678/webhook/weather-webhook-id',
    }
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