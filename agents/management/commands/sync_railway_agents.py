from django.core.management.base import BaseCommand
from agents.models import Agent

class Command(BaseCommand):
    help = 'Sync Railway agents with correct local values'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Updating Railway database with local agent values...")
        
        # Update 5 Whys agent
        try:
            five_whys = Agent.objects.get(slug='5-whys-analyzer')
            five_whys.price = 15.0
            five_whys.message_limit = 20
            five_whys.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Updated 5 Whys: {five_whys.price} AED, {five_whys.message_limit} messages"
                )
            )
        except Agent.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ 5 Whys agent not found"))
        
        # Update CyberSec Career Navigator
        try:
            career_agent = Agent.objects.get(slug='cybersec-career-navigator')
            career_agent.price = 0.0
            career_agent.message_limit = 50
            career_agent.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Updated CyberSec Career: {career_agent.price} AED, {career_agent.message_limit} messages"
                )
            )
        except Agent.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ CyberSec Career agent not found"))
        
        # Update other agents if needed
        agents_to_update = [
            ('social-ads-generator', 6.0, 50),
            ('job-posting-generator', 10.0, 50),
            ('pdf-summarizer', 8.0, 50),
        ]
        
        for slug, price, msg_limit in agents_to_update:
            try:
                agent = Agent.objects.get(slug=slug)
                agent.price = price
                agent.message_limit = msg_limit
                agent.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Updated {agent.name}: {agent.price} AED, {agent.message_limit} messages"
                    )
                )
            except Agent.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Agent {slug} not found"))
        
        self.stdout.write("\n📊 Final agent summary:")
        for agent in Agent.objects.all():
            self.stdout.write(f"  {agent.name}: {agent.price} AED, {agent.message_limit} messages")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Railway database sync completed!"))