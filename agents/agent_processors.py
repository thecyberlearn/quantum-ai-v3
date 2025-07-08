import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os


class AgentProcessor:
    def __init__(self, agent_slug):
        self.agent_slug = agent_slug
        self.webhook_urls = {
            'data-analyzer': settings.N8N_WEBHOOK_DATA_ANALYZER,
            'five-whys': settings.N8N_WEBHOOK_FIVE_WHYS,
            'job-posting-generator': settings.N8N_WEBHOOK_JOB_POSTING,
            'faq-generator': settings.N8N_WEBHOOK_FAQ_GENERATOR,
            'social-ads-generator': settings.N8N_WEBHOOK_SOCIAL_ADS,
            'weather-reporter': settings.OPENWEATHER_API_KEY,
        }
    
    def process_data_analyzer(self, file_obj, user_id):
        """Process file through N8N data analyzer webhook"""
        webhook_url = self.webhook_urls.get('data-analyzer')
        if not webhook_url:
            raise ValueError("Data analyzer webhook URL not configured")
        
        files = {'file': file_obj}
        data = {'userId': user_id}
        
        response = requests.post(webhook_url, files=files, data=data, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def process_five_whys(self, problem_description, user_id):
        """Process 5 whys analysis through N8N"""
        webhook_url = self.webhook_urls.get('five-whys')
        if not webhook_url:
            raise ValueError("Five whys webhook URL not configured")
        
        data = {
            'problem': problem_description,
            'userId': user_id
        }
        
        response = requests.post(webhook_url, json=data, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def process_weather_reporter(self, location):
        """Get weather data using OpenWeather API"""
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            raise ValueError("OpenWeather API key not configured")
        
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def process_job_posting(self, job_details, user_id):
        """Generate job posting through N8N"""
        webhook_url = self.webhook_urls.get('job-posting-generator')
        if not webhook_url:
            raise ValueError("Job posting webhook URL not configured")
        
        data = {
            'jobDetails': job_details,
            'userId': user_id
        }
        
        response = requests.post(webhook_url, json=data, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def process_social_ads(self, ad_requirements, user_id):
        """Generate social ads through N8N"""
        webhook_url = self.webhook_urls.get('social-ads-generator')
        if not webhook_url:
            raise ValueError("Social ads webhook URL not configured")
        
        data = {
            'adRequirements': ad_requirements,
            'userId': user_id
        }
        
        response = requests.post(webhook_url, json=data, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def process_faq_generator(self, content_source, user_id):
        """Generate FAQ through N8N"""
        webhook_url = self.webhook_urls.get('faq-generator')
        if not webhook_url:
            raise ValueError("FAQ generator webhook URL not configured")
        
        data = {
            'contentSource': content_source,
            'userId': user_id
        }
        
        response = requests.post(webhook_url, json=data, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def process_agent(self, **kwargs):
        """Main processing method - routes to appropriate processor"""
        processor_map = {
            'data-analyzer': self.process_data_analyzer,
            'five-whys': self.process_five_whys,
            'weather-reporter': self.process_weather_reporter,
            'job-posting-generator': self.process_job_posting,
            'social-ads-generator': self.process_social_ads,
            'faq-generator': self.process_faq_generator,
        }
        
        processor = processor_map.get(self.agent_slug)
        if not processor:
            raise ValueError(f"No processor found for agent: {self.agent_slug}")
        
        return processor(**kwargs)