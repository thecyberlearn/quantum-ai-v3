from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create AI Brand Strategist agent with JotForm integration'

    def handle(self, *args, **options):
        # Create Marketing & Advertising category
        marketing_category, created = AgentCategory.objects.get_or_create(
            slug='marketing',
            defaults={
                'name': 'Marketing & Advertising',
                'description': 'AI-powered marketing tools and advertising solutions',
                'icon': '📢'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {marketing_category.name}'))
        else:
            self.stdout.write(f'Category already exists: {marketing_category.name}')
        
        # Create AI Brand Strategist agent
        brand_agent, created = Agent.objects.get_or_create(
            slug='ai-brand-strategist',
            defaults={
                'name': 'AI Brand Strategist',
                'short_description': 'Get AI-powered brand strategy insights and recommendations for your business',
                'description': 'Transform your brand with AI-driven strategic insights. Our AI Brand Strategist analyzes your business goals, target audience, and market positioning to provide comprehensive brand strategy recommendations. Get expert guidance on brand positioning, messaging, visual identity, and competitive differentiation to elevate your brand presence.',
                'category': marketing_category,
                'price': 0.0,
                'agent_type': 'form',
                'form_schema': {
                    'fields': []  # Empty since we're using JotForm directly
                },
                'webhook_url': 'https://agent.jotform.com/01986502acd276b48e3d5f39337046c8d9b6',
                'access_url_name': 'agents:direct_access_handler',
                'display_url_name': 'agents:direct_access_display'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created agent: {brand_agent.name}'))
            self.stdout.write(f'   📝 Description: {brand_agent.short_description}')
            self.stdout.write(f'   💰 Price: {brand_agent.price} AED')
            self.stdout.write(f'   🔗 JotForm URL: {brand_agent.webhook_url}')
            self.stdout.write(f'   📂 Category: {brand_agent.category.name}')
        else:
            self.stdout.write(f'Agent already exists: {brand_agent.name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ AI Brand Strategist setup completed successfully'))
        self.stdout.write('')
        self.stdout.write('🚀 Next steps:')
        self.stdout.write('   1. Agent will appear in the Marketing & Advertising category')
        self.stdout.write('   2. Users get free access to JotForm brand strategy consultation')
        self.stdout.write('   3. Visit /agents/ai-brand-strategist/ to test the interface')
        self.stdout.write('')
        self.stdout.write(f'Agent ID: {brand_agent.id}')
        self.stdout.write(f'Agent Slug: {brand_agent.slug}')