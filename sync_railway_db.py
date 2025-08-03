#!/usr/bin/env python
"""
Script to sync Railway database with local database values.
This will update Railway with the correct agent prices and message limits.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.settings')
django.setup()

from agents.models import Agent, AgentCategory

def update_railway_agents():
    """Update Railway agents with correct local values."""
    
    print("🔄 Updating Railway database with local agent values...")
    
    # Update 5 Whys agent
    try:
        five_whys = Agent.objects.get(slug='5-whys-analyzer')
        five_whys.price = 15.0
        five_whys.message_limit = 20
        five_whys.save()
        print(f"✅ Updated 5 Whys: {five_whys.price} AED, {five_whys.message_limit} messages")
    except Agent.DoesNotExist:
        print("❌ 5 Whys agent not found")
    
    # Update CyberSec Career Navigator
    try:
        career_agent = Agent.objects.get(slug='cybersec-career-navigator')
        career_agent.price = 0.0
        career_agent.message_limit = 50
        career_agent.save()
        print(f"✅ Updated CyberSec Career: {career_agent.price} AED, {career_agent.message_limit} messages")
    except Agent.DoesNotExist:
        print("❌ CyberSec Career agent not found")
    
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
            print(f"✅ Updated {agent.name}: {agent.price} AED, {agent.message_limit} messages")
        except Agent.DoesNotExist:
            print(f"❌ Agent {slug} not found")
    
    print("\n📊 Final agent summary:")
    for agent in Agent.objects.all():
        print(f"  {agent.name}: {agent.price} AED, {agent.message_limit} messages")
    
    print("\n🎉 Railway database sync completed!")

if __name__ == "__main__":
    update_railway_agents()