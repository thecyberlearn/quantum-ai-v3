#!/usr/bin/env python
import requests
import re
from bs4 import BeautifulSoup

def test_web_form():
    print("🔍 Testing forgot password web form submission")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # Step 1: Get the forgot password page
    print("1. Getting forgot password page...")
    response = session.get(f"{base_url}/auth/forgot-password/")
    
    if response.status_code != 200:
        print(f"❌ Failed to load forgot password page: {response.status_code}")
        return False
    
    # Step 2: Extract CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ CSRF token not found")
        return False
    
    csrf_value = csrf_token.get('value')
    print(f"✅ CSRF token extracted: {csrf_value[:20]}...")
    
    # Step 3: Submit the form
    print("2. Submitting forgot password form...")
    form_data = {
        'csrfmiddlewaretoken': csrf_value,
        'email': 'amitrana01@gmail.com'
    }
    
    response = session.post(f"{base_url}/auth/forgot-password/", data=form_data)
    
    if response.status_code != 200:
        print(f"❌ Form submission failed: {response.status_code}")
        return False
    
    # Step 4: Check for success message
    soup = BeautifulSoup(response.text, 'html.parser')
    messages = soup.find_all('div', class_='message')
    
    if messages:
        for msg in messages:
            print(f"📧 Message: {msg.get_text().strip()}")
            if 'sent' in msg.get_text().lower() or 'instructions' in msg.get_text().lower():
                print("✅ Success message found!")
                return True
    
    print("⚠️ No success message found in response")
    
    # Check if there are any error messages
    error_messages = soup.find_all('div', class_='message error')
    if error_messages:
        for msg in error_messages:
            print(f"❌ Error: {msg.get_text().strip()}")
    
    return False

if __name__ == "__main__":
    try:
        test_web_form()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()