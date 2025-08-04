from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create CyberSec Career Navigator agent with JotForm integration'

    def handle(self, *args, **options):
        # Create Career & Education category
        career_category, created = AgentCategory.objects.get_or_create(
            slug='career-education',
            defaults={
                'name': 'Career & Education',
                'description': 'Professional career guidance and educational resources',
                'icon': '🎓'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {career_category.name}'))
        else:
            self.stdout.write(f'Category already exists: {career_category.name}')
        
        # Create CyberSec Career Navigator agent
        cybersec_agent, created = Agent.objects.get_or_create(
            slug='cybersec-career-navigator',
            defaults={
                'name': 'CyberSec Career Navigator',
                'short_description': 'Get personalized cybersecurity career guidance from AI expert Jessica',
                'description': 'Navigate your cybersecurity career path with expert AI guidance. Whether you\'re starting out, changing careers, or advancing in cybersecurity, get personalized advice on certifications, job roles, skills development, and career progression. Jessica, your AI career consultant, provides tailored recommendations based on your experience level and goals.',
                'category': career_category,
                'price': 12.0,
                'agent_type': 'form',
                'form_schema': {
                    'fields': []  # Empty since we're using JotForm directly
                },
                'webhook_url': 'https://agent.jotform.com/019865a942ab7fa5b5b743a5fd2abe09e345',
                'access_url_name': '',
                'display_url_name': ''
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created agent: {cybersec_agent.name}'))
            self.stdout.write(f'   📝 Description: {cybersec_agent.short_description}')
            self.stdout.write(f'   💰 Price: {cybersec_agent.price} AED')
            self.stdout.write(f'   🔗 JotForm URL: {cybersec_agent.webhook_url}')
            self.stdout.write(f'   📂 Category: {cybersec_agent.category.name}')
        else:
            self.stdout.write(f'Agent already exists: {cybersec_agent.name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ CyberSec Career Navigator setup completed successfully'))
        self.stdout.write('')
        self.stdout.write('🚀 Next steps:')
        self.stdout.write('   1. Agent will appear in the Career & Education category')
        self.stdout.write('   2. Users will pay 12 AED and get direct access to JotForm interface')
        self.stdout.write('   3. Visit /agents/cybersec-career-navigator/ to test the interface')
        self.stdout.write('')
        self.stdout.write(f'Agent ID: {cybersec_agent.id}')
        self.stdout.write(f'Agent Slug: {cybersec_agent.slug}')