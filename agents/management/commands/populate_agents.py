from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Populate all agents in the database - calls all individual agent creation commands'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of agents even if they exist',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip agents that already exist (default behavior)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🤖 Starting agent population process...")
        
        # List of all agent creation commands
        agent_commands = [
            'create_social_ads_agent',
            'create_job_posting_agent', 
            'create_pdf_summarizer_agent',
            'create_five_whys_agent',
            'create_cybersec_career_agent',
        ]
        
        success_count = 0
        error_count = 0
        
        for command_name in agent_commands:
            try:
                self.stdout.write(f"\n📦 Running {command_name}...")
                
                # Pass through options to individual commands
                command_options = {}
                if options.get('force'):
                    command_options['force'] = True
                
                # Call the individual agent creation command
                call_command(command_name, **command_options)
                
                success_count += 1
                self.stdout.write(f"✅ {command_name} completed successfully")
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ {command_name} failed: {str(e)}")
                )
                
                # Continue with other commands even if one fails
                continue
        
        self.stdout.write(f"\n🎯 Agent population summary:")
        self.stdout.write(f"✅ Successful: {success_count}")
        self.stdout.write(f"❌ Failed: {error_count}")
        self.stdout.write(f"📊 Total commands: {len(agent_commands)}")
        
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS("\n🎉 All agents populated successfully!"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠️  {error_count} commands failed. Check logs above."))
        
        # Show final agent count
        try:
            from agents.models import Agent, AgentCategory
            
            total_categories = AgentCategory.objects.count()
            total_agents = Agent.objects.count()
            active_agents = Agent.objects.filter(is_active=True).count()
            
            self.stdout.write(f"\n📈 Database Summary:")
            self.stdout.write(f"🏷️  Categories: {total_categories}")
            self.stdout.write(f"🤖 Total Agents: {total_agents}")
            self.stdout.write(f"⚡ Active Agents: {active_agents}")
            
            if active_agents > 0:
                self.stdout.write(f"\n🔗 Agents by category:")
                categories = AgentCategory.objects.all()
                for category in categories:
                    agent_count = Agent.objects.filter(category=category, is_active=True).count()
                    if agent_count > 0:
                        self.stdout.write(f"  {category.icon} {category.name}: {agent_count} agents")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Could not generate database summary: {str(e)}")
        
        # Environment-specific notes
        deployment_env = os.environ.get('DEPLOYMENT_ENVIRONMENT', 'development')
        self.stdout.write(f"\n🌍 Environment: {deployment_env}")
        
        if deployment_env == 'production':
            self.stdout.write("💡 Production notes:")
            self.stdout.write("   - Webhook URLs should point to production N8N instance")
            self.stdout.write("   - Verify agent pricing and configurations")
            self.stdout.write("   - Test agent execution after deployment")
        else:
            self.stdout.write("💡 Development notes:")
            self.stdout.write("   - Webhook URLs point to localhost:5678")
            self.stdout.write("   - Use ngrok for testing webhooks externally")