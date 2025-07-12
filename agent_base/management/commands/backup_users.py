from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wallet.models import WalletTransaction
import json
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Backup and restore user data for Railway deployments'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['backup', 'restore', 'info'],
            default='info',
            help='Action to perform: backup, restore, or info',
        )
        parser.add_argument(
            '--file',
            default='users_backup.json',
            help='Backup file path',
        )
    
    def handle(self, *args, **options):
        action = options['action']
        backup_file = options['file']
        
        if action == 'info':
            self.show_database_info()
        elif action == 'backup':
            self.backup_users(backup_file)
        elif action == 'restore':
            self.restore_users(backup_file)
    
    def show_database_info(self):
        """Show current database state"""
        self.stdout.write("=== DATABASE INFO ===")
        
        # Database backend
        from django.conf import settings
        from django.db import connection
        db_config = settings.DATABASES['default']
        self.stdout.write(f"Database Engine: {db_config['ENGINE']}")
        if 'NAME' in db_config:
            self.stdout.write(f"Database Name: {db_config['NAME']}")
        
        # Check if tables exist
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                self.stdout.write(f"Database tables: {len(tables)} found")
                
                if 'authentication_user' not in tables:
                    self.stdout.write("⚠️  User table not found - database not yet migrated")
                    return
        except Exception as e:
            self.stdout.write(f"⚠️  Could not check database tables: {e}")
            return
        
        try:
            # User counts
            total_users = User.objects.count()
            superusers = User.objects.filter(is_superuser=True).count()
            regular_users = total_users - superusers
            
            self.stdout.write(f"Total Users: {total_users}")
            self.stdout.write(f"Superusers: {superusers}")
            self.stdout.write(f"Regular Users: {regular_users}")
            
            # List superusers
            if superusers > 0:
                self.stdout.write("\\nSuperusers:")
                for user in User.objects.filter(is_superuser=True):
                    self.stdout.write(f"  - {user.email} (username: {user.username})")
            
            # Wallet info
            total_transactions = WalletTransaction.objects.count()
            self.stdout.write(f"\\nWallet Transactions: {total_transactions}")
            
            # Users with positive balance
            users_with_balance = User.objects.filter(wallet_balance__gt=0).count()
            self.stdout.write(f"Users with balance: {users_with_balance}")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Could not read user data: {e}")
            self.stdout.write("Database may not be fully migrated yet")
    
    def backup_users(self, backup_file):
        """Backup all users and their wallet data"""
        self.stdout.write(f"Backing up users to {backup_file}...")
        
        backup_data = {
            'users': [],
            'transactions': []
        }
        
        # Backup users
        for user in User.objects.all():
            user_data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'wallet_balance': str(user.wallet_balance),
                'date_joined': user.date_joined.isoformat(),
            }
            backup_data['users'].append(user_data)
        
        # Backup transactions
        for transaction in WalletTransaction.objects.all():
            transaction_data = {
                'user_email': transaction.user.email,
                'amount': str(transaction.amount),
                'type': transaction.type,
                'description': transaction.description,
                'agent_slug': transaction.agent_slug,
                'stripe_session_id': transaction.stripe_session_id,
                'created_at': transaction.created_at.isoformat(),
            }
            backup_data['transactions'].append(transaction_data)
        
        # Write to file
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Backed up {len(backup_data['users'])} users and "
                f"{len(backup_data['transactions'])} transactions to {backup_file}"
            )
        )
    
    def restore_users(self, backup_file):
        """Restore users from backup file"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"Backup file {backup_file} not found")
            )
            return
        
        self.stdout.write(f"Restoring users from {backup_file}...")
        
        users_created = 0
        users_updated = 0
        transactions_created = 0
        
        # Restore users
        for user_data in backup_data.get('users', []):
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_superuser': user_data['is_superuser'],
                    'is_staff': user_data['is_staff'],
                    'is_active': user_data['is_active'],
                    'wallet_balance': Decimal(user_data['wallet_balance']),
                }
            )
            
            if created:
                users_created += 1
                self.stdout.write(f"Created user: {user.email}")
            else:
                # Update wallet balance for existing users
                user.wallet_balance = Decimal(user_data['wallet_balance'])
                user.save()
                users_updated += 1
                self.stdout.write(f"Updated user: {user.email}")
        
        # Restore transactions
        for transaction_data in backup_data.get('transactions', []):
            try:
                user = User.objects.get(email=transaction_data['user_email'])
                transaction, created = WalletTransaction.objects.get_or_create(
                    user=user,
                    amount=Decimal(transaction_data['amount']),
                    type=transaction_data['type'],
                    description=transaction_data['description'],
                    created_at=transaction_data['created_at'],
                    defaults={
                        'agent_slug': transaction_data.get('agent_slug', ''),
                        'stripe_session_id': transaction_data.get('stripe_session_id', ''),
                    }
                )
                
                if created:
                    transactions_created += 1
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"User {transaction_data['user_email']} not found for transaction"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Restore complete: {users_created} users created, "
                f"{users_updated} users updated, {transactions_created} transactions created"
            )
        )