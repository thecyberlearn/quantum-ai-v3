from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Create the 5 Whys chat-based analysis agent'

    def handle(self, *args, **options):
        # Create or get the Analysis category
        category, created = AgentCategory.objects.get_or_create(
            slug='analysis',
            defaults={
                'name': 'Analysis & Problem Solving',
                'description': 'Advanced analytical tools for problem-solving and decision making',
                'icon': '🧠',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(f'✅ Created category: {category.name}')
        else:
            self.stdout.write(f'📂 Using existing category: {category.name}')
        
        # Create the 5 Whys agent
        agent, created = Agent.objects.get_or_create(
            slug='five-whys-analysis',
            defaults={
                'name': '5 Whys Analysis',
                'short_description': 'Interactive problem-solving using the proven 5 Whys methodology',
                'description': '''Discover the root cause of any problem through guided conversation using the 5 Whys technique. 
                
This interactive agent helps you systematically drill down to the core issue by asking "why" five times. Perfect for:
• Troubleshooting operational problems
• Understanding process failures  
• Identifying systemic issues
• Improving quality and efficiency

The conversation-based approach ensures you think deeply about each layer of the problem, leading to more effective solutions.''',
                'category': category,
                'price': 15.00,
                'agent_type': 'chat',  # This is a chat-based agent
                'form_schema': None,  # Chat agents don't use form schemas
                'webhook_url': 'http://localhost:5678/webhook/5-whys-web',  # N8N webhook URL
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'🎉 Successfully created 5 Whys Analysis agent!')
            )
            self.stdout.write(f'   💬 Agent Type: {agent.agent_type}')
            self.stdout.write(f'   💰 Price: {agent.price} AED')
            self.stdout.write(f'   🔗 Webhook: {agent.webhook_url}')
            self.stdout.write(f'   📂 Category: {agent.category.name}')
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  5 Whys Analysis agent already exists')
            )
            
            # Update existing agent to ensure it's chat-based
            if agent.agent_type != 'chat':
                agent.agent_type = 'chat'
                agent.form_schema = None
                agent.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Updated existing agent to chat-based')
                )
        
        self.stdout.write('')
        self.stdout.write('🚀 Next steps:')
        self.stdout.write('   1. Ensure N8N webhook is running on localhost:5678')
        self.stdout.write('   2. Visit /agents/five-whys-analysis/ to test the chat interface')
        self.stdout.write('   3. Start a conversation to test the 5 Whys methodology')
        self.stdout.write('')
        self.stdout.write('💡 The agent is now ready for interactive problem-solving!')