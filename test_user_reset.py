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

def test_user_reset():
    print("🔍 Testing forgot password with user: amitrana01@gmail.com")
    print("=" * 60)
    
    target_email = "amitrana01@gmail.com"
    
    # Check if user exists
    try:
        user = User.objects.get(email=target_email)
        print(f"✅ Found user: {user.username} ({user.email})")
    except User.DoesNotExist:
        print(f"❌ User with email {target_email} not found")
        return False
    
    # Create password reset token
    reset_token = PasswordResetToken.objects.create(user=user)
    print(f"✅ Password reset token created: {reset_token.token}")
    
    # Build reset URL
    reset_url = f"http://localhost:8000/auth/reset-password/{reset_token.token}/"
    
    # Send reset email (same as in the actual view)
    subject = 'Password Reset Request'
    message = f'''
Hello {user.username},

You requested a password reset for your NetCop account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this reset, please ignore this email.

Best regards,
NetCop Team
    '''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        print(f"✅ Password reset email sent successfully!")
        print(f"📧 Email sent to: {user.email}")
        print(f"🔗 Reset URL: {reset_url}")
        print(f"⏰ Token expires in: 1 hour")
        print("\n📧 CHECK THE INBOX FOR: amitrana01@gmail.com")
        print("Note: Check spam folder if not in inbox")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_user_reset()