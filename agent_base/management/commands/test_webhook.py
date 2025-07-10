from django.core.management.base import BaseCommand
from agent_base.processors import WebhookFormatDetector
import json


class Command(BaseCommand):
    help = 'Test webhook format detection'
    
    def add_arguments(self, parser):
        parser.add_argument('webhook_url', type=str, help='Webhook URL to test')
        parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
        parser.add_argument('--detect-best', action='store_true', help='Detect best format only')
    
    def handle(self, *args, **options):
        webhook_url = options['webhook_url']
        timeout = options['timeout']
        
        self.stdout.write(f"Testing webhook format for: {webhook_url}")
        self.stdout.write("-" * 50)
        
        if options['detect_best']:
            # Just detect the best format
            best_format = WebhookFormatDetector.detect_best_format(webhook_url)
            self.stdout.write(self.style.SUCCESS(f"Best format detected: {best_format}"))
        else:
            # Test all formats
            results = WebhookFormatDetector.test_webhook_format(webhook_url, timeout)
            
            for result in results:
                status = self.style.SUCCESS("✓") if result['success'] else self.style.ERROR("✗")
                self.stdout.write(f"{status} {result['format']}")
                self.stdout.write(f"  Status Code: {result['status_code']}")
                
                if result['success']:
                    self.stdout.write(f"  Response: {result['response'][:100]}...")
                else:
                    self.stdout.write(f"  Error: {result['error']}")
                
                self.stdout.write("")
            
            # Show best format recommendation
            successful_formats = [r for r in results if r['success']]
            if successful_formats:
                best = successful_formats[0]['format']
                self.stdout.write(self.style.SUCCESS(f"Recommended format: {best}"))
            else:
                self.stdout.write(self.style.WARNING("No formats worked - webhook may be down"))
        
        self.stdout.write("-" * 50)
        self.stdout.write("Format descriptions:")
        self.stdout.write("• n8n_message: Standard N8N format with message object")
        self.stdout.write("• direct_data: Direct data format with input field")
        self.stdout.write("• simple: Simple key-value format")