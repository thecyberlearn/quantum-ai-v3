from django.core.management.base import BaseCommand
from agents.models import Agent

class Command(BaseCommand):
    help = 'Fix agent prices and message limits'

    def handle(self, *args, **options):
        # Fix CyberSec Career Navigator
        Agent.objects.filter(slug='cybersec-career-navigator').update(price=0.0)
        
        # Fix 5 Whys agent  
        Agent.objects.filter(slug='5-whys-analyzer').update(price=15.0, message_limit=20)
        
        self.stdout.write(self.style.SUCCESS('✅ Agents fixed!'))