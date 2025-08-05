import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from agents.models import AgentCategory, Agent

class Command(BaseCommand):
    help = 'Dynamically populate all agents and categories from JSON configuration files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Dynamically populating agents from configuration files...'))
        self.stdout.write('')
        
        # Track creation statistics
        categories_created = 0
        agents_created = 0
        config_base_path = Path(__file__).parent.parent.parent / 'configs'
        
        # Load and create categories
        categories_file = config_base_path / 'categories' / 'categories.json'
        if not categories_file.exists():
            self.stdout.write(self.style.ERROR(f'❌ Categories file not found: {categories_file}'))
            return
        
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        
        categories = {}
        for category_data in categories_data:
            category, created = AgentCategory.objects.get_or_create(
                slug=category_data['slug'],
                defaults={
                    'name': category_data['name'],
                    'description': category_data['description'],
                    'icon': category_data['icon']
                }
            )
            categories[category_data['slug']] = category
            if created:
                categories_created += 1
                self.stdout.write(f'✅ Created category: {category.name}')
            else:
                self.stdout.write(f'   Category exists: {category.name}')
        
        self.stdout.write('')
        
        # Load and create agents from JSON files
        agents_dir = config_base_path / 'agents'
        if not agents_dir.exists():
            self.stdout.write(self.style.ERROR(f'❌ Agents directory not found: {agents_dir}'))
            return
        
        # Get all JSON files in agents directory
        agent_files = list(agents_dir.glob('*.json'))
        if not agent_files:
            self.stdout.write(self.style.WARNING('⚠️ No agent configuration files found'))
            return
        
        self.stdout.write(f'📁 Found {len(agent_files)} agent configuration files')
        self.stdout.write('')
        
        # Process each agent configuration file
        for agent_file in sorted(agent_files):
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                # Validate required fields
                required_fields = ['slug', 'name', 'category', 'price', 'agent_type']
                missing_fields = [field for field in required_fields if field not in agent_data]
                if missing_fields:
                    self.stdout.write(self.style.ERROR(f'❌ Missing fields in {agent_file.name}: {missing_fields}'))
                    continue
                
                # Get category
                category_slug = agent_data['category']
                if category_slug not in categories:
                    self.stdout.write(self.style.ERROR(f'❌ Unknown category "{category_slug}" in {agent_file.name}'))
                    continue
                
                category = categories[category_slug]
                
                # Create agent
                agent, created = Agent.objects.get_or_create(
                    slug=agent_data['slug'],
                    defaults={
                        'name': agent_data['name'],
                        'short_description': agent_data.get('short_description', ''),
                        'description': agent_data.get('description', ''),
                        'category': category,
                        'price': agent_data['price'],
                        'agent_type': agent_data['agent_type'],
                        'form_schema': agent_data.get('form_schema'),
                        'webhook_url': agent_data.get('webhook_url', ''),
                        'access_url_name': agent_data.get('access_url_name', ''),
                        'display_url_name': agent_data.get('display_url_name', '')
                    }
                )
                
                if created:
                    agents_created += 1
                    system_type = agent_data.get('system_type', 'webhook')  
                    self.stdout.write(f'✅ Created agent: {agent.name} ({system_type.title()})')
                    self.stdout.write(f'   💰 Price: {agent.price} AED')
                    self.stdout.write(f'   📁 Config: {agent_file.name}')
                else:
                    self.stdout.write(f'   Agent exists: {agent.name} (from {agent_file.name})')
            
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'❌ Invalid JSON in {agent_file.name}: {e}'))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error processing {agent_file.name}: {e}'))
                continue
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Dynamic population completed successfully!'))
        self.stdout.write('')
        self.stdout.write(f'📊 Summary:')
        self.stdout.write(f'   Categories created: {categories_created}')
        self.stdout.write(f'   Agents created: {agents_created}')
        self.stdout.write(f'   Configuration files processed: {len(agent_files)}')
        self.stdout.write('')
        
        # Final verification
        total_categories = AgentCategory.objects.filter(is_active=True).count()
        total_agents = Agent.objects.filter(is_active=True).count()
        webhook_agents = Agent.objects.filter(is_active=True, access_url_name='').count()
        direct_agents = Agent.objects.filter(is_active=True).exclude(access_url_name='').count()
        
        self.stdout.write(f'🔍 Final verification:')
        self.stdout.write(f'   Total categories: {total_categories}')
        self.stdout.write(f'   Total agents: {total_agents}')
        self.stdout.write(f'   Webhook agents: {webhook_agents}')
        self.stdout.write(f'   Direct access agents: {direct_agents}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Database is now consistent and ready!'))
        self.stdout.write('')
        self.stdout.write('🚀 To add new agents:')
        self.stdout.write('   1. Create new JSON file in agents/configs/agents/')
        self.stdout.write('   2. Run this command again')
        self.stdout.write('   3. Agent will automatically appear in marketplace!')