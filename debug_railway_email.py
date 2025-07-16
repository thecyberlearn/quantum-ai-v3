#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.settings')
django.setup()

def debug_railway_email():
    print("🔍 RAILWAY EMAIL CONFIGURATION DEBUG")
    print("=" * 50)
    
    # Check environment
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')
    print(f"RAILWAY_ENVIRONMENT: {railway_env}")
    
    # Check email settings
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'Not set'}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    print(f"SITE_URL: {getattr(settings, 'SITE_URL', 'Not set')}")
    
    print("\n" + "=" * 50)
    
    # Check if email is configured properly
    if not getattr(settings, 'EMAIL_HOST_USER', '') or not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
        print("❌ EMAIL CONFIGURATION INCOMPLETE")
        print("Missing EMAIL_HOST_USER or EMAIL_HOST_PASSWORD")
        print("\nTo fix this, add these environment variables to Railway:")
        print("EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
        print("EMAIL_HOST=smtp.gmail.com")
        print("EMAIL_PORT=587")
        print("EMAIL_USE_TLS=True")
        print("EMAIL_HOST_USER=thecyberlearn@gmail.com")
        print("EMAIL_HOST_PASSWORD=ueqd ulan xcwl cfrr")
        print("DEFAULT_FROM_EMAIL=NetCop <thecyberlearn@gmail.com>")
        return False
    
    # Test email sending
    print("📧 Testing email sending...")
    try:
        from django.core.mail import send_mail
        
        send_mail(
            'Railway Email Test',
            'This is a test email from Railway deployment.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

if __name__ == "__main__":
    debug_railway_email()