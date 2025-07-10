#!/usr/bin/env python
"""
Test the Five Whys webhook to understand expected format
"""
import requests
import json
from datetime import datetime

def test_current_format():
    """Test with our current format"""
    webhook_url = "https://quantumtaskai.app.n8n.cloud/webhook/5-whys-web"
    
    # Current format we're sending
    current_payload = {
        'user_id': 'test-user-123',
        'problem_statement': 'Our customer support response time is too slow',
        'problem_category': 'operational',
        'context_information': 'Average response time is 4 hours, customers complaining',
        'include_solutions': True,
        'agent_type': 'five_whys_analyzer',
        'cost': 8.00,
        'timestamp': datetime.now().isoformat() + 'Z'
    }
    
    print("🔍 Testing Five Whys Webhook - Current Format")
    print("=" * 60)
    print(f"Webhook URL: {webhook_url}")
    print(f"Current Payload: {json.dumps(current_payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(webhook_url, json=current_payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Current format working!")
            return True
        else:
            print("❌ Current format not working")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_message_format():
    """Test with message format like other agents"""
    webhook_url = "https://quantumtaskai.app.n8n.cloud/webhook/5-whys-web"
    
    # Format similar to social ads and job posting
    problem_statement = "Our customer support response time is too slow"
    problem_category = "operational"
    context_information = "Average response time is 4 hours, customers complaining"
    include_solutions = True
    
    message_text = f"""Perform a Five Whys root cause analysis with the following details:

Problem Statement: {problem_statement}
Problem Category: {problem_category}
Context Information: {context_information}
Include Solutions: {'Yes' if include_solutions else 'No'}

Please conduct a systematic Five Whys analysis to identify the root cause and provide actionable solutions."""
    
    message_payload = {
        'message': {
            'text': message_text
        },
        'sessionId': f'five_whys_{int(datetime.now().timestamp() * 1000)}',
        'userId': 'test-user-123',
        'agentId': '5',  # Five Whys agent ID
        'problemStatement': problem_statement,
        'problemCategory': problem_category
    }
    
    print("\n" + "=" * 60)
    print("🔍 Testing Five Whys Webhook - Message Format")
    print("=" * 60)
    print(f"Message Payload: {json.dumps(message_payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(webhook_url, json=message_payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Message format working!")
            return True
        else:
            print("❌ Message format not working")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_simple_connectivity():
    """Test basic connectivity"""
    webhook_url = "https://quantumtaskai.app.n8n.cloud/webhook/5-whys-web"
    
    print("🔗 Testing Basic Connectivity")
    print("-" * 30)
    
    try:
        response = requests.post(webhook_url, json={'test': 'ping'}, timeout=10)
        print(f"✅ Connectivity: OK (Status: {response.status_code})")
        print(f"Response: {response.text[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Connectivity: FAILED ({e})")
        return False

if __name__ == "__main__":
    print("🚀 Testing Five Whys Webhook Formats")
    print("=" * 60)
    
    # Test basic connectivity
    if test_simple_connectivity():
        print("\n" + "=" * 60)
        
        # Test current format
        current_works = test_current_format()
        
        # Test message format
        message_works = test_message_format()
        
        print("\n" + "=" * 60)
        print("📊 RESULTS SUMMARY:")
        print(f"Current Format: {'✅ WORKS' if current_works else '❌ FAILED'}")
        print(f"Message Format: {'✅ WORKS' if message_works else '❌ FAILED'}")
        
        if current_works:
            print("\n💡 Current format is working - no changes needed!")
        elif message_works:
            print("\n💡 Need to update to message format!")
        else:
            print("\n⚠️  Both formats failed - need to investigate webhook structure")
            
    else:
        print("\n❌ Cannot test formats - webhook not reachable")
    
    print("=" * 60)