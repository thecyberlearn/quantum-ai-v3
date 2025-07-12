from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a user with wallet balance'
    
    def add_arguments(self, parser):
        parser.add_argument('email', help='User email address')
        parser.add_argument('password', help='User password')
        parser.add_argument(
            '--username',
            help='Username (defaults to email prefix)',
        )
        parser.add_argument(
            '--first-name',
            default='',
            help='First name',
        )
        parser.add_argument(
            '--last-name', 
            default='',
            help='Last name',
        )
        parser.add_argument(
            '--balance',
            type=float,
            default=0.0,
            help='Initial wallet balance',
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Create as superuser',
        )
    
    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options.get('username') or email.split('@')[0]
        first_name = options['first_name']
        last_name = options['last_name']
        balance = Decimal(str(options['balance']))
        is_superuser = options['superuser']
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f"User with email {email} already exists")
            )
            return
        
        # Create user
        if is_superuser:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user_type = "superuser"
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            user_type = "user"
        
        # Set wallet balance if provided
        if balance > 0:
            user.add_balance(balance, "Initial balance from admin")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {user_type}: {email} with balance {balance} AED"
            )
        )
        
        # Show login instructions
        self.stdout.write("\\nLogin credentials:")
        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Password: {password}")
        if is_superuser:
            self.stdout.write("Admin URL: /admin/")