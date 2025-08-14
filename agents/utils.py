"""
Utility functions for the agents app.
Contains webhook validation, message formatting, and other helper functions.
"""

import ipaddress
from urllib.parse import urlparse


def validate_webhook_url(url):
    """
    Validate webhook URL to prevent SSRF attacks.
    Only allows HTTPS URLs to external, non-private networks.
    """
    try:
        parsed = urlparse(url)
        
        # Only allow HTTP/HTTPS protocols
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS URLs are allowed")
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid hostname in URL")
        
        # For localhost development, allow localhost URLs first
        if hostname in ['localhost', '127.0.0.1'] and parsed.port in [5678, 8000, 8080]:
            return True  # Allow N8N development server
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private, loopback, and reserved IP ranges
            if (ip.is_private or ip.is_loopback or ip.is_reserved or 
                ip.is_link_local or ip.is_multicast):
                raise ValueError("Internal/private IP addresses are not allowed")
        except ValueError as e:
            if "does not appear to be an IPv4 or IPv6 address" not in str(e):
                raise  # Re-raise if it's not just a "not an IP" error
            # If it's not an IP, it's a domain name - that's fine
            
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid webhook URL: {str(e)}")


def format_agent_message(agent_slug, input_data):
    """Format input data into a message for N8N webhook based on agent type"""
    if agent_slug == 'social-ads-generator':
        description = input_data.get('description', '')
        platform = input_data.get('social_platform', '')
        emoji = input_data.get('include_emoji', 'yes')
        language = input_data.get('language', 'English')
        
        return f"Execute Social Media Ad Creator with the following parameters:. Describe what you'd like to generate: {description}. Include Emoji: {emoji.title()}. For Social Media Platform: {platform.title()}. Language: {language}."
    
    elif agent_slug == 'job-posting-generator':
        job_title = input_data.get('job_title', '')
        company_name = input_data.get('company_name', '')
        description = input_data.get('job_description', '')
        seniority = input_data.get('seniority_level', '')
        contract = input_data.get('contract_type', '')
        location = input_data.get('location', '')
        language = input_data.get('language', 'English')
        
        return f"Create a professional job posting for: {job_title} at {company_name}. Description: {description}. Seniority: {seniority}. Contract: {contract}. Location: {location}. Language: {language}. Make it comprehensive and attractive to candidates."
    
    # Default formatting for other agents
    params = [f"{key}: {value}" for key, value in input_data.items() if value]
    return f"Execute {agent_slug.replace('-', ' ').title()} with parameters: {'. '.join(params)}."


class AgentCompat:
    """
    Compatibility class to convert file-based agent data to object format
    for templates and views that expect object attributes.
    """
    def __init__(self, data):
        self.slug = data['slug']
        self.name = data['name']
        self.price = float(data['price'])
        self.webhook_url = data['webhook_url']
        self.access_url_name = data.get('access_url_name', '')
        self.display_url_name = data.get('display_url_name', '')
        self.id = data['slug']  # Use slug as ID for file-based agents
        self.message_limit = data.get('message_limit', 50)