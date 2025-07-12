from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Check current database configuration and connection'
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 Database Configuration Check")
        self.stdout.write("=" * 40)
        
        # Environment detection
        is_railway = bool(os.environ.get('RAILWAY_ENVIRONMENT'))
        database_url = os.environ.get('DATABASE_URL', '')
        
        self.stdout.write(f"Environment: {'Railway' if is_railway else 'Local Development'}")
        self.stdout.write(f"DATABASE_URL set: {'Yes' if database_url else 'No'}")
        
        if database_url:
            # Mask password in URL for display
            masked_url = database_url
            if '@' in masked_url and '://' in masked_url:
                parts = masked_url.split('://')
                if len(parts) == 2:
                    scheme = parts[0]
                    rest = parts[1]
                    if '@' in rest:
                        auth_part, host_part = rest.split('@', 1)
                        if ':' in auth_part:
                            user, password = auth_part.split(':', 1)
                            masked_url = f"{scheme}://{user}:***@{host_part}"
            self.stdout.write(f"DATABASE_URL: {masked_url}")
        
        # Current Django database configuration
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']
        
        self.stdout.write(f"\\nCurrent Django Configuration:")
        self.stdout.write(f"Engine: {engine}")
        
        if 'postgresql' in engine:
            self.stdout.write(f"Database: {db_config.get('NAME', 'N/A')}")
            self.stdout.write(f"Host: {db_config.get('HOST', 'N/A')}")
            self.stdout.write(f"Port: {db_config.get('PORT', 'N/A')}")
            self.stdout.write(f"User: {db_config.get('USER', 'N/A')}")
        elif 'sqlite' in engine:
            self.stdout.write(f"Database file: {db_config.get('NAME', 'N/A')}")
        
        # Test connection
        self.stdout.write(f"\\n🔌 Testing Database Connection...")
        try:
            with connection.cursor() as cursor:
                if 'postgresql' in engine:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    self.stdout.write(f"✅ PostgreSQL Connection: {version}")
                elif 'sqlite' in engine:
                    cursor.execute("SELECT sqlite_version();")
                    version = cursor.fetchone()[0]
                    self.stdout.write(f"✅ SQLite Connection: {version}")
                
                # Check if tables exist
                if 'postgresql' in engine:
                    cursor.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """)
                
                table_count = cursor.fetchone()[0]
                self.stdout.write(f"📊 Database tables: {table_count}")
                
                if table_count == 0:
                    self.stdout.write("⚠️  No tables found. Run: python manage.py migrate")
                
        except Exception as e:
            self.stdout.write(f"❌ Connection failed: {e}")
            
            if 'postgresql' in engine:
                self.stdout.write("\\n💡 PostgreSQL Connection Tips:")
                self.stdout.write("1. Install PostgreSQL: brew install postgresql")
                self.stdout.write("2. Start PostgreSQL: brew services start postgresql")
                self.stdout.write("3. Create database: createdb netcop_hub")
                self.stdout.write("4. Create user: createuser netcop_user -P")
                self.stdout.write("5. Or use Docker: docker run --name netcop-postgres -e POSTGRES_DB=netcop_hub -e POSTGRES_USER=netcop_user -e POSTGRES_PASSWORD=netcop_pass -p 5432:5432 -d postgres:15")
        
        # Module availability check
        self.stdout.write(f"\\n📦 Module Availability:")
        try:
            import psycopg2
            self.stdout.write("✅ psycopg2 (PostgreSQL driver) available")
        except ImportError:
            self.stdout.write("❌ psycopg2 not available")
        
        try:
            import sqlite3
            self.stdout.write("✅ sqlite3 available")
        except ImportError:
            self.stdout.write("❌ sqlite3 not available")
        
        self.stdout.write("\\n" + "=" * 40)
        self.stdout.write("Database check complete!")