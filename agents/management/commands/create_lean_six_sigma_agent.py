from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create Lean Six Sigma Expert agent with JotForm integration'

    def handle(self, *args, **options):
        # Create Business Consulting category
        consulting_category, created = AgentCategory.objects.get_or_create(
            slug='consulting',
            defaults={
                'name': 'Business Consulting',
                'description': 'Professional business consultation and strategy services',
                'icon': '💼'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {consulting_category.name}'))
        else:
            self.stdout.write(f'Category already exists: {consulting_category.name}')
        
        # Create Lean Six Sigma Expert agent
        lean_six_sigma_agent, created = Agent.objects.get_or_create(
            slug='lean-six-sigma-expert',
            defaults={
                'name': 'Lean Six Sigma Expert',
                'short_description': 'Get expert guidance on Lean Six Sigma methodologies and process improvement strategies',
                'description': 'Optimize your business processes with expert Lean Six Sigma consultation. Our AI-powered expert provides comprehensive guidance on process improvement, waste reduction, quality enhancement, and operational excellence. Get personalized recommendations for implementing Lean Six Sigma methodologies in your organization.',
                'category': consulting_category,
                'price': 0.0,
                'agent_type': 'form',
                'form_schema': {
                    'fields': []  # Empty since we're using JotForm directly
                },
                'webhook_url': 'https://agent.jotform.com/01987b8843ae71129342f62a93d2c605efad',
                'access_url_name': 'agents:direct_access_handler',
                'display_url_name': 'agents:direct_access_display'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created agent: {lean_six_sigma_agent.name}'))
            self.stdout.write(f'   📝 Description: {lean_six_sigma_agent.short_description}')
            self.stdout.write(f'   💰 Price: {lean_six_sigma_agent.price} AED')
            self.stdout.write(f'   🔗 JotForm URL: {lean_six_sigma_agent.webhook_url}')
            self.stdout.write(f'   📂 Category: {lean_six_sigma_agent.category.name}')
        else:
            self.stdout.write(f'Agent already exists: {lean_six_sigma_agent.name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Lean Six Sigma Expert setup completed successfully'))
        self.stdout.write('')
        self.stdout.write('🚀 Next steps:')
        self.stdout.write('   1. Agent will appear in the Business Consulting category')
        self.stdout.write('   2. Users get free access to JotForm Lean Six Sigma consultation')
        self.stdout.write('   3. Visit /agents/lean-six-sigma-expert/ to test the interface')
        self.stdout.write('')
        self.stdout.write(f'Agent ID: {lean_six_sigma_agent.id}')
        self.stdout.write(f'Agent Slug: {lean_six_sigma_agent.slug}')