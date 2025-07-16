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

def test_gmail_reset():
    print("🔍 Testing forgot password with Gmail address")
    print("=" * 50)
    
    gmail_address = settings.EMAIL_HOST_USER  # thecyberlearn@gmail.com
    
    # Create or update user with Gmail address
    user, created = User.objects.update_or_create(
        email=gmail_address,
        defaults={
            'username': 'gmail_user',
            'is_active': True,
        }
    )
    
    if created:
        print(f"✅ Created new user: {user.email}")
        user.set_password('temppassword123')
        user.save()
    else:
        print(f"✅ Using existing user: {user.email}")
    
    # Create password reset token
    reset_token = PasswordResetToken.objects.create(user=user)
    
    # Build reset URL
    reset_url = f"http://localhost:8000/auth/reset-password/{reset_token.token}/"
    
    # Send reset email
    subject = 'NetCop Password Reset Request'
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
        
        print(f"✅ Password reset email sent to: {user.email}")
        print(f"🔗 Reset URL: {reset_url}")
        print("\n📧 CHECK YOUR GMAIL INBOX!")
        print("Note: Check spam folder if not in inbox")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print(f"Error details: {traceback.format_exc()}")

if __name__ == "__main__":
    test_gmail_reset()