from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    help = 'Fix migration conflicts and sync database state'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            default='data_analyzer',
            help='App to fix migrations for (default: data_analyzer)',
        )
        parser.add_argument(
            '--migration',
            default='0002_auto_20250710_0431',
            help='Specific migration to mark as fake',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check migration status without fixing',
        )
    
    def handle(self, *args, **options):
        app_label = options['app']
        migration_name = options['migration']
        check_only = options['check_only']
        
        self.stdout.write(f"🔍 Checking migration status for {app_label}...")
        
        # Check if problematic migration is already applied
        recorder = MigrationRecorder(connection)
        applied_migrations = recorder.applied_migrations()
        
        migration_key = (app_label, migration_name)
        is_applied = migration_key in applied_migrations
        
        self.stdout.write(f"Migration {migration_name}: {'✅ Applied' if is_applied else '❌ Not Applied'}")
        
        # Check if columns exist in database
        table_exists, columns = self.check_table_columns(app_label)
        
        if table_exists:
            self.stdout.write(f"Database table exists with {len(columns)} columns:")
            for col in sorted(columns):
                self.stdout.write(f"  - {col}")
        else:
            self.stdout.write("❌ Database table does not exist")
        
        if check_only:
            return
        
        # Fix strategy based on current state
        if not is_applied and table_exists and 'data_file' in columns:
            self.stdout.write("🔧 Marking problematic migration as fake...")
            try:
                call_command('migrate', '--fake', app_label, migration_name.split('_')[0])
                self.stdout.write("✅ Migration marked as fake")
            except Exception as e:
                self.stdout.write(f"❌ Failed to fake migration: {e}")
        
        # Try to apply remaining migrations
        self.stdout.write("🔄 Applying remaining migrations...")
        try:
            call_command('migrate', app_label)
            self.stdout.write("✅ Migrations applied successfully")
        except Exception as e:
            self.stdout.write(f"❌ Migration failed: {e}")
            self.stdout.write("💡 Try running: python manage.py reset_database --action migrations --confirm")
    
    def check_table_columns(self, app_label):
        """Check what columns exist in the database table"""
        table_map = {
            'data_analyzer': 'data_analyzer_requests',
            'weather_reporter': 'weather_reporter_weatheragentrequest',
            'job_posting_generator': 'job_posting_generator_jobpostingagentrequest',
            'social_ads_generator': 'social_ads_generator_socialadsagentrequest',
        }
        
        table_name = table_map.get(app_label, f'{app_label}_request')
        
        try:
            with connection.cursor() as cursor:
                # PostgreSQL query to get column names
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY column_name
                """, [table_name])
                
                columns = [row[0] for row in cursor.fetchall()]
                return True, columns
                
        except Exception as e:
            # Try SQLite format
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [row[1] for row in cursor.fetchall()]  # Column name is index 1
                    return True, columns
            except Exception:
                return False, []
    
    def show_migration_history(self, app_label):
        """Show migration history for debugging"""
        self.stdout.write(f"📜 Migration history for {app_label}:")
        
        recorder = MigrationRecorder(connection)
        applied_migrations = recorder.applied_migrations()
        
        app_migrations = [m for m in applied_migrations if m[0] == app_label]
        
        if app_migrations:
            for app, migration in sorted(app_migrations):
                self.stdout.write(f"  ✅ {migration}")
        else:
            self.stdout.write(f"  No migrations applied for {app_label}")