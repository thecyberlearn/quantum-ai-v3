from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection, transaction
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = 'Reset database and migrations for clean development/deployment'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['migrations', 'database', 'full'],
            default='full',
            help='What to reset: migrations, database, or full (both)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the destructive action',
        )
        parser.add_argument(
            '--keep-superuser',
            action='store_true',
            help='Keep existing superuser data during database reset',
        )
    
    def handle(self, *args, **options):
        action = options['action']
        confirm = options['confirm']
        keep_superuser = options['keep_superuser']
        
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  This is a destructive operation! Add --confirm to proceed."
                )
            )
            self.stdout.write("This will:")
            if action in ['migrations', 'full']:
                self.stdout.write("  - Delete all migration files")
            if action in ['database', 'full']:
                self.stdout.write("  - Drop all database tables")
                self.stdout.write("  - Recreate fresh database")
            return
        
        if action in ['migrations', 'full']:
            self.reset_migrations()
        
        if action in ['database', 'full']:
            self.reset_database(keep_superuser)
        
        if action == 'full':
            self.create_fresh_migrations()
            self.run_migrations()
            if not keep_superuser:
                self.create_initial_data()
    
    def reset_migrations(self):
        """Delete all migration files except __init__.py"""
        self.stdout.write("🗑️  Deleting migration files...")
        
        apps_with_migrations = [
            'agent_base',
            'authentication', 
            'core',
            'wallet',
            'weather_reporter',
            'data_analyzer',
            'job_posting_generator',
            'social_ads_generator',
        ]
        
        for app in apps_with_migrations:
            migrations_dir = f"{app}/migrations"
            if os.path.exists(migrations_dir):
                # Keep __init__.py but delete all other migration files
                for file in os.listdir(migrations_dir):
                    if file.endswith('.py') and file != '__init__.py':
                        file_path = os.path.join(migrations_dir, file)
                        os.remove(file_path)
                        self.stdout.write(f"  Deleted: {file_path}")
        
        self.stdout.write(self.style.SUCCESS("✅ Migration files deleted"))
    
    def reset_database(self, keep_superuser=False):
        """Drop all tables and recreate database"""
        self.stdout.write("🗑️  Resetting database...")
        
        # Backup superuser if requested
        superuser_data = None
        if keep_superuser:
            superuser_data = self.backup_superuser()
        
        # Get database engine
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']
        
        if 'sqlite' in engine:
            # For SQLite, just delete the file
            db_file = db_config['NAME']
            if os.path.exists(db_file):
                os.remove(db_file)
                self.stdout.write(f"  Deleted SQLite file: {db_file}")
        
        elif 'postgresql' in engine:
            # For PostgreSQL, drop all tables
            self.drop_all_postgresql_tables()
        
        else:
            self.stdout.write(
                self.style.ERROR(f"Unsupported database engine: {engine}")
            )
            return
        
        self.stdout.write(self.style.SUCCESS("✅ Database reset"))
        
        # Restore superuser if backed up
        if superuser_data:
            self.restore_superuser(superuser_data)
    
    def drop_all_postgresql_tables(self):
        """Drop all tables in PostgreSQL database"""
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                # Drop all tables with CASCADE
                tables_str = ', '.join(f'"{table}"' for table in tables)
                cursor.execute(f'DROP TABLE IF EXISTS {tables_str} CASCADE')
                self.stdout.write(f"  Dropped {len(tables)} PostgreSQL tables")
    
    def backup_superuser(self):
        """Backup superuser data before reset"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                return {
                    'username': superuser.username,
                    'email': superuser.email,
                    'first_name': superuser.first_name,
                    'last_name': superuser.last_name,
                }
        except Exception:
            pass
        return None
    
    def restore_superuser(self, superuser_data):
        """Restore superuser after reset"""
        if superuser_data:
            self.stdout.write("🔑 Restoring superuser...")
            call_command(
                'create_user',
                superuser_data['email'],
                'admin123',  # Default password
                '--superuser',
                '--username', superuser_data['username'],
                '--first-name', superuser_data['first_name'],
                '--last-name', superuser_data['last_name'],
            )
    
    def create_fresh_migrations(self):
        """Create new migration files"""
        self.stdout.write("📝 Creating fresh migrations...")
        call_command('makemigrations')
        self.stdout.write(self.style.SUCCESS("✅ Fresh migrations created"))
    
    def run_migrations(self):
        """Apply all migrations"""
        self.stdout.write("🔄 Running migrations...")
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS("✅ Migrations applied"))
    
    def create_initial_data(self):
        """Create initial data (agents and admin user)"""
        self.stdout.write("👤 Creating initial data...")
        call_command('populate_agents', '--create-admin')
        self.stdout.write(self.style.SUCCESS("✅ Initial data created"))