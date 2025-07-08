#!/usr/bin/env python
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.views import homepage_view

# Create a test request
factory = RequestFactory()
request = factory.get('/')

# Create a mock user
from django.contrib.auth.models import AnonymousUser
request.user = AnonymousUser()

try:
    # Test homepage view
    response = homepage_view(request)
    print(f"Homepage view status: {response.status_code}")
    print("Homepage view working correctly!")
    
except Exception as e:
    print(f"Error in homepage view: {e}")
    import traceback
    traceback.print_exc()