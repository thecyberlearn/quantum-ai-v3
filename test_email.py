#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.settings')
django.setup()

from django.core.mail import send_mail
from authentication.models import User

# Test email sending
def test_email():
    print("Testing email configuration...")
    
    # Check settings
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_FILE_PATH: {getattr(settings, 'EMAIL_FILE_PATH', 'Not set')}")
    
    # Send test email
    try:
        send_mail(
            'Test Email',
            'This is a test email from Django.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        print("📁 Check /tmp/app-messages/ for the email file")
        
        # List files in email directory
        import glob
        files = glob.glob('/tmp/app-messages/*')
        if files:
            print(f"📧 Email files: {files}")
        else:
            print("⚠️  No email files found")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    test_email()