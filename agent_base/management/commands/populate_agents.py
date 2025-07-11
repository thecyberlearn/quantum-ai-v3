from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agent_base.models import BaseAgent

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with default agents and create admin user'
    
    def handle(self, *args, **options):
        self.stdout.write("Creating admin user...")
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email='admin@netcop.ai',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write("Created superuser: admin@netcop.ai / admin123")
        else:
            self.stdout.write("Superuser already exists")
        
        self.stdout.write("Creating default agents...")
        
        agents_data = [
            {
                'name': 'Weather Reporter',
                'slug': 'weather-reporter',
                'description': 'Get real-time weather information for any location worldwide. Provides current conditions, forecasts, and detailed weather reports.',
                'category': 'utilities',
                'price': 2.0,
                'icon': '🌤️',
                'agent_type': 'api',
            },
            {
                'name': 'Data Analyzer', 
                'slug': 'data-analyzer',
                'description': 'Analyze and extract insights from your data files. Supports PDF, CSV, and text analysis with AI-powered insights.',
                'category': 'analytics',
                'price': 5.0,
                'icon': '📊',
                'agent_type': 'webhook',
            },
            {
                'name': 'Job Posting Generator',
                'slug': 'job-posting-generator', 
                'description': 'Create professional job postings with AI assistance. Generate compelling job descriptions that attract the right candidates.',
                'category': 'content',
                'price': 3.0,
                'icon': '💼',
                'agent_type': 'webhook',
            },
            {
                'name': 'Social Ads Generator',
                'slug': 'social-ads-generator',
                'description': 'Generate engaging social media advertisements. Create compelling ad copy for various platforms to boost your marketing campaigns.',
                'category': 'marketing', 
                'price': 4.0,
                'icon': '📱',
                'agent_type': 'webhook',
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for agent_data in agents_data:
            agent, created = BaseAgent.objects.get_or_create(
                slug=agent_data['slug'],
                defaults=agent_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created: {agent.name}")
            else:
                # Update existing agent
                for key, value in agent_data.items():
                    if key != 'slug':
                        setattr(agent, key, value)
                agent.save()
                updated_count += 1
                self.stdout.write(f"Updated: {agent.name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {len(agents_data)} agents: "
                f"{created_count} created, {updated_count} updated"
            )
        )