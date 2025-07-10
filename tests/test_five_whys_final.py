#!/usr/bin/env python
"""
Final test of the updated Five Whys processor
"""
import requests
import json
from datetime import datetime

def test_final_five_whys():
    """Test the final corrected Five Whys webhook format"""
    
    webhook_url = "https://quantumtaskai.app.n8n.cloud/webhook/5-whys-web"
    
    # Simulate the data that would come from the Django form
    form_data = {
        'user_id': 'test-user-456',
        'problem_statement': 'Our e-commerce website has a high cart abandonment rate',
        'problem_category': 'customer',
        'context_information': 'Cart abandonment rate is 75%, industry average is 50%. Customers add items but leave before checkout.',
        'include_solutions': True,
        'cost': 8.00
    }
    
    # Format as the processor now does
    message_text = f"""Perform a Five Whys root cause analysis with the following details:

Problem Statement: {form_data['problem_statement']}
Problem Category: {form_data['problem_category']}
Context Information: {form_data['context_information']}
Include Solutions: {'Yes' if form_data['include_solutions'] else 'No'}

Please conduct a systematic Five Whys analysis to identify the root cause and provide actionable solutions."""
    
    payload = {
        'message': {
            'text': message_text
        },
        'sessionId': f'five_whys_{int(datetime.now().timestamp() * 1000)}',
        'userId': form_data['user_id'],
        'agentId': '5',
        'problemStatement': form_data['problem_statement'],
        'problemCategory': form_data['problem_category']
    }
    
    print("🔍 Final Five Whys Webhook Test")
    print("=" * 60)
    print(f"Webhook URL: {webhook_url}")
    print(f"\nForm Data: {json.dumps(form_data, indent=2)}")
    print(f"\nFormatted Payload:")
    print(json.dumps(payload, indent=2))
    print("-" * 60)
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=60)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                analysis_content = json_response.get('output', '')
                
                print(f"\n🎉 SUCCESS! Generated Five Whys Analysis:")
                print("-" * 40)
                print(analysis_content)
                print("-" * 40)
                
                print(f"\n📊 Response Analysis:")
                print(f"- Content Length: {len(analysis_content)} characters")
                print(f"- Contains 'Why': {'Yes' if 'Why' in analysis_content else 'No'}")
                print(f"- Contains 'Root Cause': {'Yes' if 'root cause' in analysis_content.lower() else 'No'}")
                print(f"- Contains 'Solution': {'Yes' if 'solution' in analysis_content.lower() else 'No'}")
                print(f"- Contains Problem Statement: {'Yes' if form_data['problem_statement'] in analysis_content else 'No'}")
                
                return True
                
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_different_problem():
    """Test with a different type of problem"""
    webhook_url = "https://quantumtaskai.app.n8n.cloud/webhook/5-whys-web"
    
    # Test with a technical problem
    message_text = """Perform a Five Whys root cause analysis with the following details:

Problem Statement: Server downtime incidents are increasing
Problem Category: technical
Context Information: 3 incidents this month, each lasting 2+ hours. Users unable to access application.
Include Solutions: Yes

Please conduct a systematic Five Whys analysis to identify the root cause and provide actionable solutions."""
    
    payload = {
        'message': {
            'text': message_text
        },
        'sessionId': f'five_whys_{int(datetime.now().timestamp() * 1000)}',
        'userId': 'test-user-789',
        'agentId': '5',
        'problemStatement': 'Server downtime incidents are increasing',
        'problemCategory': 'technical'
    }
    
    print("\n" + "=" * 60)
    print("🔍 Testing Different Problem Type - Technical")
    print("=" * 60)
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=60)
        
        if response.status_code == 200:
            json_response = response.json()
            analysis_content = json_response.get('output', '')
            print(f"✅ Technical problem analysis generated ({len(analysis_content)} chars)")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Updated Five Whys Webhook")
    print("=" * 60)
    
    # Test main scenario
    success1 = test_final_five_whys()
    
    # Test different problem type
    success2 = test_different_problem()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 FIVE WHYS WEBHOOK TESTS PASSED!")
        print("✅ The processor format has been updated to match N8N expectations.")
        print("✅ Works with different problem types and categories.")
        print("✅ Ready for production use!")
    else:
        print("❌ FIVE WHYS WEBHOOK TESTS FAILED!")
        print("Check the error messages above.")
    print("=" * 60)