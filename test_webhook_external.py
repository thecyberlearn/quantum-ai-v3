#!/usr/bin/env python3
"""
Test external webhook accessibility
"""
import requests
import json
from datetime import datetime

def test_webhook_accessibility():
    """Test if Railway webhook endpoints are accessible externally"""
    
    base_url = "https://netcop.up.railway.app"
    
    endpoints = [
        "/simple-webhook-test/",
        "/stripe/webhook/",
    ]
    
    print("🧪 Testing Railway webhook endpoint accessibility...")
    print(f"📍 Base URL: {base_url}")
    print("-" * 60)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        
        try:
            print(f"\n🔍 Testing: {url}")
            
            # Test with POST request
            response = requests.post(
                url,
                json={
                    "test": True,
                    "source": "external_test_script",
                    "timestamp": datetime.now().isoformat()
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "WebhookTester/1.0",
                    "X-Test-Source": "external"
                },
                timeout=10
            )
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Response: {response.text[:200]}")
            
            if response.status_code < 400:
                print(f"✅ SUCCESS: {endpoint} is accessible")
            else:
                print(f"❌ FAILED: {endpoint} returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 External accessibility test completed")

if __name__ == "__main__":
    test_webhook_accessibility()