from django.core.management.base import BaseCommand
from agents.models import Agent
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate the database with sample agent data'

    def handle(self, *args, **options):
        # Clear existing agents
        Agent.objects.all().delete()
        
        # Create sample agents
        agents_data = [
            {
                'name': 'Data Analyzer',
                'slug': 'data-analyzer',
                'description': 'Upload your data files and get comprehensive analysis with insights, trends, and visualizations.',
                'category': 'analytics',
                'price': Decimal('15.00'),
                'icon': '📊',
                'rating': Decimal('4.7'),
                'review_count': 324,
                'n8n_webhook_url': 'https://n8n.example.com/webhook/data-analyzer',
            },
            {
                'name': 'Weather Reporter',
                'slug': 'weather-reporter',
                'description': 'Get current weather conditions, forecasts, and detailed meteorological data for any location.',
                'category': 'utilities',
                'price': Decimal('5.00'),
                'icon': '🌤️',
                'rating': Decimal('4.5'),
                'review_count': 892,
                'n8n_webhook_url': '',  # Uses OpenWeather API directly
            },
            {
                'name': '5 Whys Analysis',
                'slug': 'five-whys',
                'description': 'Perform root cause analysis using the 5 Whys technique to identify the underlying cause of problems.',
                'category': 'analytics',
                'price': Decimal('12.00'),
                'icon': '❓',
                'rating': Decimal('4.6'),
                'review_count': 156,
                'n8n_webhook_url': 'https://n8n.example.com/webhook/five-whys',
            },
            {
                'name': 'FAQ Generator',
                'slug': 'faq-generator',
                'description': 'Generate comprehensive FAQ sections from your content, documentation, or product information.',
                'category': 'content',
                'price': Decimal('10.00'),
                'icon': '❔',
                'rating': Decimal('4.4'),
                'review_count': 287,
                'n8n_webhook_url': 'https://n8n.example.com/webhook/faq-generator',
            },
            {
                'name': 'Social Ads Generator',
                'slug': 'social-ads-generator',
                'description': 'Create compelling social media advertisements with copy, targeting suggestions, and campaign ideas.',
                'category': 'marketing',
                'price': Decimal('20.00'),
                'icon': '📢',
                'rating': Decimal('4.8'),
                'review_count': 543,
                'n8n_webhook_url': 'https://n8n.example.com/webhook/social-ads',
            },
            {
                'name': 'Job Posting Generator',
                'slug': 'job-posting-generator',
                'description': 'Generate professional job postings with requirements, responsibilities, and compelling descriptions.',
                'category': 'content',
                'price': Decimal('8.00'),
                'icon': '💼',
                'rating': Decimal('4.3'),
                'review_count': 198,
                'n8n_webhook_url': 'https://n8n.example.com/webhook/job-posting',
            },
        ]
        
        for agent_data in agents_data:
            agent = Agent.objects.create(**agent_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created agent: {agent.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {len(agents_data)} agents')
        )