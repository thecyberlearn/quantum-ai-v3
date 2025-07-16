#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netcop_hub.settings')
django.setup()

from django.core.mail import send_mail
from authentication.models import User, PasswordResetToken
import traceback

def debug_email_sending():
    print("=" * 60)
    print("🔍 DEBUGGING EMAIL CONFIGURATION")
    print("=" * 60)
    
    # Check Django settings
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Test basic email sending
    print("📧 Testing basic email sending...")
    try:
        send_mail(
            'Test Email from NetCop',
            'This is a test email to verify email configuration.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        print("✅ Basic email test PASSED")
    except Exception as e:
        print(f"❌ Basic email test FAILED: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    # Test forgot password flow
    print("\n🔑 Testing forgot password flow...")
    try:
        # Get a test user
        user = User.objects.filter(email=settings.EMAIL_HOST_USER).first()
        if not user:
            user = User.objects.first()
        
        if not user:
            print("❌ No users found in database")
            return False
            
        print(f"Using test user: {user.email}")
        
        # Create password reset token
        reset_token = PasswordResetToken.objects.create(user=user)
        print(f"✅ Password reset token created: {reset_token.token}")
        
        # Build reset URL
        reset_url = f"http://localhost:8000/auth/reset-password/{reset_token.token}/"
        
        # Send reset email
        subject = 'Password Reset Request - DEBUG TEST'
        message = f'''
Hello {user.username},

This is a DEBUG TEST of the password reset functionality.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
NetCop Team (DEBUG MODE)
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        print("✅ Password reset email sent successfully!")
        print(f"📧 Email sent to: {user.email}")
        print(f"🔗 Reset URL: {reset_url}")
        
    except Exception as e:
        print(f"❌ Password reset test FAILED: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Check your Gmail inbox!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    debug_email_sending()