from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Check and fix admin user status'
    
    def handle(self, *args, **options):
        # Check both possible admin emails (preferred email first)
        possible_emails = ['admin@quantumtaskai.com', 'admin@netcop.ai']
        username = 'admin'
        password = 'P9cKE9G$R%ni#p'
        
        user = None
        found_email = None
        
        # Try to find existing admin user
        for email in possible_emails:
            try:
                user = User.objects.get(email=email)
                found_email = email
                break
            except User.DoesNotExist:
                continue
        
        if user:
            # User found with one of the emails
            self.stdout.write(f"✅ User found: {user.email}")
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Is superuser: {user.is_superuser}")
            self.stdout.write(f"Is staff: {user.is_staff}")
            self.stdout.write(f"Is active: {user.is_active}")
            self.stdout.write(f"Email verified: {user.email_verified}")
            
            # Fix user permissions if needed
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.save()
                self.stdout.write("🔧 Fixed user permissions")
            
            # Reset password to ensure it's correct
            user.set_password(password)
            user.save()
            self.stdout.write("🔑 Password reset successfully")
            
            # Show login instructions
            self.stdout.write("\n📝 Login Instructions:")
            self.stdout.write(f"URL: https://www.quantumtaskai.com/admin/")
            self.stdout.write(f"Email: {found_email}")
            self.stdout.write(f"Username: {username}")
            self.stdout.write(f"Password: {password}")
            
        else:
            self.stdout.write("❌ Admin user not found! Creating new admin user...")
            
            # Create new admin user with preferred email
            preferred_email = 'admin@quantumtaskai.com'
            user = User.objects.create_superuser(
                username=username,
                email=preferred_email,
                password=password,
            )
            user.add_balance(100, "Initial admin balance")
            
            self.stdout.write("✅ New admin user created successfully!")
            self.stdout.write(f"Email: {preferred_email}")
            self.stdout.write(f"Username: {username}")
            self.stdout.write(f"Password: {password}")
            self.stdout.write(f"Balance: {user.wallet_balance} AED")