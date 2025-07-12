from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agent_base.models import BaseAgent

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with default agents and create admin user'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Force create admin user even if superusers exist',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("Checking admin user...")
        
        # Only create admin if explicitly requested or no superusers exist
        should_create_admin = options.get('create_admin', False) or not User.objects.filter(is_superuser=True).exists()
        
        if should_create_admin:
            # Check if admin email already exists
            admin_email = 'admin@netcop.ai'
            if User.objects.filter(email=admin_email).exists():
                self.stdout.write(f"Admin user with email {admin_email} already exists - skipping creation")
            else:
                User.objects.create_superuser(
                    username='admin',
                    email=admin_email,
                    password='admin123',
                    first_name='Admin',
                    last_name='User'
                )
                self.stdout.write("Created superuser: admin@netcop.ai / admin123")
        else:
            superuser_count = User.objects.filter(is_superuser=True).count()
            self.stdout.write(f"Superuser(s) already exist ({superuser_count} found) - skipping admin creation")
        
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