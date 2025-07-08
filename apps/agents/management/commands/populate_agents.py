from django.core.management.base import BaseCommand
from agents.models import Agent
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with default agents'

    def handle(self, *args, **options):
        agents = [
            {
                'name': '5 Whys Analysis Agent',
                'slug': 'five-whys',
                'description': 'Systematic root cause analysis using the proven 5 Whys methodology to identify and solve business problems effectively.',
                'category': 'analytics',
                'price': Decimal('8.00'),
                'icon': '🔍',
                'rating': Decimal('4.8'),
                'review_count': 850,
            },
            {
                'name': 'Data Analysis Agent',
                'slug': 'data-analyzer',
                'description': 'Processes complex datasets and generates actionable insights with automated reporting and visualization capabilities.',
                'category': 'analytics',
                'price': Decimal('5.00'),
                'icon': '📊',
                'rating': Decimal('4.8'),
                'review_count': 1800,
            },
            {
                'name': 'Weather Reporter Agent',
                'slug': 'weather-reporter',
                'description': 'Get detailed weather reports for any location worldwide with current conditions, forecasts, and weather alerts.',
                'category': 'utilities',
                'price': Decimal('2.00'),
                'icon': '🌤️',
                'rating': Decimal('4.9'),
                'review_count': 1650,
            },
            {
                'name': 'Job Posting Generator Agent',
                'slug': 'job-posting-generator',
                'description': 'Create compelling, professional job postings with AI-powered content generation.',
                'category': 'content',
                'price': Decimal('3.00'),
                'icon': '📝',
                'rating': Decimal('4.7'),
                'review_count': 1200,
            },
            {
                'name': 'Social Ads Generator Agent',
                'slug': 'social-ads-generator',
                'description': 'Create engaging social media advertisements optimized for different platforms.',
                'category': 'marketing',
                'price': Decimal('4.00'),
                'icon': '📱',
                'rating': Decimal('4.8'),
                'review_count': 950,
            },
            {
                'name': 'FAQ Generator Agent',
                'slug': 'faq-generator',
                'description': 'Generate comprehensive FAQs from uploaded files or website URLs.',
                'category': 'content',
                'price': Decimal('3.00'),
                'icon': '❓',
                'rating': Decimal('4.7'),
                'review_count': 750,
            },
        ]

        for agent_data in agents:
            agent, created = Agent.objects.get_or_create(
                slug=agent_data['slug'],
                defaults=agent_data
            )
            if created:
                self.stdout.write(f'Created agent: {agent.name}')
            else:
                self.stdout.write(f'Agent already exists: {agent.name}')