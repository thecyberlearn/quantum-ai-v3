#!/usr/bin/env python
"""
Simple webhook connectivity test for social ads generator
"""
import requests
import json
from datetime import datetime

def test_social_ads_webhook():
    """Test the social ads webhook connectivity"""
    
    webhook_url = "http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d"
    
    # Test payload using the correct format expected by N8N
    message_text = """Create a social media advertisement with the following details:

Description: Amazing smartphone with cutting-edge features
Include Emoji: Yes
Social Media Platform: Facebook
Language: English

Please create an engaging, platform-optimized social media ad based on this information."""
    
    test_payload = {
        'message': {
            'text': message_text
        },
        'sessionId': f'social_ad_test_{int(datetime.now().timestamp() * 1000)}'
    }
    
    print(f"Testing webhook: {webhook_url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Send POST request to webhook
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        print(f"✅ Response Content: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS: Webhook is reachable and responding!")
            
            # Try to parse JSON response
            try:
                json_response = response.json()
                print(f"📄 JSON Response: {json.dumps(json_response, indent=2)}")
            except:
                print("📄 Response is not JSON format")
                
        else:
            print(f"\n⚠️  WARNING: Webhook returned status code {response.status_code}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: Cannot reach webhook")
        print(f"Details: {e}")
        print("\nPossible causes:")
        print("1. N8N server is not running on localhost:5678")
        print("2. Webhook ID is incorrect")
        print("3. Firewall blocking the connection")
        
    except requests.exceptions.Timeout as e:
        print(f"\n⏰ TIMEOUT ERROR: Webhook took too long to respond")
        print(f"Details: {e}")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")

def test_webhook_simple():
    """Simple ping test to check if webhook endpoint exists"""
    
    webhook_url = "http://localhost:5678/webhook/2dc234d8-7217-454a-83e9-81afe5b4fe2d"
    
    print(f"Simple connectivity test for: {webhook_url}")
    print("-" * 50)
    
    try:
        # Simple GET request to see if endpoint exists
        response = requests.get(webhook_url, timeout=10)
        print(f"GET Response Status: {response.status_code}")
        print(f"GET Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"GET request failed: {e}")
    
    try:
        # Simple POST with minimal data
        response = requests.post(webhook_url, json={'test': 'ping'}, timeout=10)
        print(f"POST Response Status: {response.status_code}")
        print(f"POST Response: {response.text[:200]}...")
        
    except Exception as e:
        print(f"POST request failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Social Ads Webhook Connectivity")
    print("=" * 60)
    
    # Run simple test first
    test_webhook_simple()
    
    print("\n" + "=" * 60)
    
    # Run full test
    test_social_ads_webhook()
    
    print("\n" + "=" * 60)
    print("Test completed!")