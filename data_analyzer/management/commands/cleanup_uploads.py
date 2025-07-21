from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from data_analyzer.models import DataAnalysisAgentRequest
import os
import glob


class Command(BaseCommand):
    help = 'Clean up old uploaded files from data analyzer'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--age-hours',
            type=int,
            default=24,
            help='Delete files older than this many hours (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force-orphaned',
            action='store_true',
            help='Also delete orphaned files not associated with database records'
        )
    
    def handle(self, *args, **options):
        age_hours = options['age_hours']
        dry_run = options['dry_run']
        force_orphaned = options['force_orphaned']
        
        cutoff_time = timezone.now() - timedelta(hours=age_hours)
        
        self.stdout.write(f"Looking for files older than {age_hours} hours ({cutoff_time})")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No files will be deleted"))
        
        # Clean up files associated with old database records
        old_requests = DataAnalysisAgentRequest.objects.filter(
            created_at__lt=cutoff_time
        )
        
        deleted_count = 0
        error_count = 0
        
        for request in old_requests:
            if request.data_file:
                try:
                    file_path = request.data_file.path
                    if os.path.exists(file_path):
                        if not dry_run:
                            os.remove(file_path)
                            self.stdout.write(f"Deleted: {file_path}")
                        else:
                            self.stdout.write(f"Would delete: {file_path}")
                        deleted_count += 1
                    else:
                        self.stdout.write(f"File already gone: {file_path}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error deleting {request.data_file.path}: {e}")
                    )
                    error_count += 1
        
        # Clean up orphaned files if requested
        if force_orphaned:
            self.stdout.write("Checking for orphaned files...")
            
            try:
                from django.conf import settings
                upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads/data_analyzer/')
                
                if os.path.exists(upload_path):
                    # Get all files in upload directory
                    all_files = glob.glob(os.path.join(upload_path, '*'))
                    
                    # Get all files currently referenced in database
                    db_files = set()
                    for request in DataAnalysisAgentRequest.objects.filter(data_file__isnull=False):
                        if request.data_file:
                            try:
                                db_files.add(request.data_file.path)
                            except:
                                pass
                    
                    # Find orphaned files
                    for file_path in all_files:
                        if os.path.isfile(file_path) and file_path not in db_files:
                            file_age = timezone.now() - timezone.datetime.fromtimestamp(
                                os.path.getctime(file_path), 
                                tz=timezone.get_current_timezone()
                            )
                            
                            if file_age > timedelta(hours=age_hours):
                                if not dry_run:
                                    os.remove(file_path)
                                    self.stdout.write(f"Deleted orphaned file: {file_path}")
                                else:
                                    self.stdout.write(f"Would delete orphaned file: {file_path}")
                                deleted_count += 1
                            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error checking orphaned files: {e}")
                )
                error_count += 1
        
        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"DRY RUN: Would delete {deleted_count} files")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {deleted_count} files")
            )
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f"Encountered {error_count} errors")
            )