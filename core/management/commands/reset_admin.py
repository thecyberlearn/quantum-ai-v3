from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Reset admin user - delete existing and create fresh'
    
    def handle(self, *args, **options):
        email = 'admin@quantumtaskai.com'
        username = 'admin'
        password = 'QuantumAI2024!'
        
        self.stdout.write("🔄 Resetting admin user...")
        
        # Delete ANY existing admin users (all possible emails/usernames)
        deleted_count = 0
        
        # Check for users with admin emails
        admin_emails = ['admin@quantumtaskai.com', 'admin@netcop.ai']
        for admin_email in admin_emails:
            try:
                user = User.objects.get(email=admin_email)
                user.delete()
                deleted_count += 1
                self.stdout.write(f"❌ Deleted user with email: {admin_email}")
            except User.DoesNotExist:
                pass
        
        # Check for users with admin username
        try:
            user = User.objects.get(username=username)
            if user.email not in admin_emails:  # Don't double-delete
                user.delete()
                deleted_count += 1
                self.stdout.write(f"❌ Deleted user with username: {username}")
        except User.DoesNotExist:
            pass
        
        self.stdout.write(f"🗑️  Deleted {deleted_count} existing admin user(s)")
        
        # Create fresh admin user
        self.stdout.write("🆕 Creating fresh admin user...")
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        
        # Add initial balance
        user.add_balance(100, "Initial admin balance")
        
        # Verify user was created correctly
        user.refresh_from_db()
        
        self.stdout.write("✅ Fresh admin user created successfully!")
        self.stdout.write(f"📧 Email: {user.email}")
        self.stdout.write(f"👤 Username: {user.username}")
        self.stdout.write(f"🔐 Password: {password}")
        self.stdout.write(f"⚡ Is superuser: {user.is_superuser}")
        self.stdout.write(f"👥 Is staff: {user.is_staff}")
        self.stdout.write(f"✅ Is active: {user.is_active}")
        self.stdout.write(f"💰 Balance: {user.wallet_balance} AED")
        
        self.stdout.write("\n🎯 Login Instructions:")
        self.stdout.write("URL: https://quantum-ai.up.railway.app/admin/")
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Password: {password}")
        
        self.stdout.write("\n🔍 Authentication Test:")
        # Test authentication
        from django.contrib.auth import authenticate
        auth_user = authenticate(username=email, password=password)
        if auth_user:
            self.stdout.write("✅ Email authentication: WORKING")
        else:
            self.stdout.write("❌ Email authentication: FAILED")
            
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            self.stdout.write("✅ Username authentication: WORKING")
        else:
            self.stdout.write("❌ Username authentication: FAILED")