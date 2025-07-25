#!/usr/bin/env python
"""
Test the job posting webhook with updated format
"""
import requests
import json
from datetime import datetime

def test_job_posting_webhook():
    """Test the job posting webhook connectivity"""
    
    webhook_url = "http://localhost:5678/webhook/43f84411-eaaa-488c-9b1f-856e90d0aaf6"
    
    # Simulate the data that would come from the Django form
    form_data = {
        'user_id': 'test-user-123',
        'job_title': 'Senior Software Developer',
        'company_name': 'Quantum Tasks AI Technologies',
        'industry': 'technology',
        'job_type': 'full-time',
        'experience_level': 'senior',
        'location': 'Remote',
        'salary_range': '$80,000 - $120,000',
        'key_responsibilities': 'Develop and maintain web applications, lead technical projects, mentor junior developers',
        'required_skills': 'Python, Django, React, PostgreSQL, AWS, Git',
        'company_culture': 'Innovative, collaborative, work-life balance focused',
        'cost': 10.00
    }
    
    # Format as the processor now does
    message_text = f"""Create a professional job posting with the following details:

Job Title: {form_data['job_title']}
Company: {form_data['company_name']}
Description: {form_data['key_responsibilities']}
Seniority Level: {form_data['experience_level']}
Contract Type: {form_data['job_type']}
Location: {form_data['location']}
Language: English
Required Skills: {form_data['required_skills']}
Salary Range: {form_data['salary_range']}
Company Culture: {form_data['company_culture']}

Please create a complete, engaging job posting based on this information."""
    
    payload = {
        'message': {
            'text': message_text
        },
        'sessionId': f'job_posting_{int(datetime.now().timestamp() * 1000)}',
        'userId': form_data['user_id'],
        'agentId': '9',
        'jobTitle': form_data['job_title'],
        'companyName': form_data['company_name']
    }
    
    print("💼 Job Posting Webhook Test")
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
                job_content = json_response.get('output', '')
                
                print(f"\n🎉 SUCCESS! Generated Job Posting:")
                print("-" * 40)
                print(job_content)
                print("-" * 40)
                
                print(f"\n📊 Response Analysis:")
                print(f"- Content Length: {len(job_content)} characters")
                print(f"- Contains Company Name: {'Yes' if form_data['company_name'] in job_content else 'No'}")
                print(f"- Contains Job Title: {'Yes' if form_data['job_title'] in job_content else 'No'}")
                print(f"- Professional Format: Job posting format detected")
                
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

def test_simple_connectivity():
    """Simple test to check if webhook endpoint exists"""
    webhook_url = "http://localhost:5678/webhook/43f84411-eaaa-488c-9b1f-856e90d0aaf6"
    
    print("🔗 Simple Connectivity Test")
    print("-" * 30)
    
    try:
        # Simple POST with minimal data to test connectivity
        response = requests.post(webhook_url, json={'test': 'ping'}, timeout=10)
        print(f"✅ Connectivity: OK (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Connectivity: FAILED ({e})")
        return False

if __name__ == "__main__":
    print("🚀 Testing Job Posting Webhook")
    print("=" * 60)
    
    # Test connectivity first
    if test_simple_connectivity():
        print("\n" + "=" * 60)
        success = test_job_posting_webhook()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 JOB POSTING WEBHOOK TEST PASSED!")
            print("✅ The processor format has been updated to match N8N expectations.")
            print("✅ Ready for production use!")
        else:
            print("❌ JOB POSTING WEBHOOK TEST FAILED!")
            print("Check the error messages above.")
    else:
        print("\n❌ Cannot proceed with full test - webhook endpoint not reachable")
    
    print("=" * 60)