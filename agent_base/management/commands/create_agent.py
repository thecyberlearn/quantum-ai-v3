from django.core.management.base import BaseCommand
from django.template import Template, Context
from django.conf import settings
from pathlib import Path
import os
import shutil
from agent_base.models import BaseAgent


class Command(BaseCommand):
    help = 'Create a new agent with standardized structure'
    
    def add_arguments(self, parser):
        parser.add_argument('agent_name', type=str, help='Name of the agent (e.g., "Weather Reporter")')
        parser.add_argument('agent_slug', type=str, help='Slug for the agent (e.g., "weather-reporter")')
        parser.add_argument('agent_type', choices=['webhook', 'api'], help='Type of agent: webhook or api')
        parser.add_argument('--category', default='utilities', help='Category for the agent')
        parser.add_argument('--price', type=float, default=1.0, help='Price for the agent')
        parser.add_argument('--description', default='', help='Description for the agent')
        parser.add_argument('--icon', default='🤖', help='Icon for the agent')
        
        # Webhook specific arguments
        parser.add_argument('--webhook-url', help='Webhook URL for webhook agents')
        parser.add_argument('--agent-id', help='Agent ID for webhook agents')
        
        # API specific arguments
        parser.add_argument('--api-base-url', help='Base URL for API agents')
        parser.add_argument('--api-key-env', help='Environment variable name for API key')
        parser.add_argument('--auth-method', default='query', choices=['bearer', 'api-key', 'basic', 'query'], help='Authentication method for API')
    
    def handle(self, *args, **options):
        agent_name = options['agent_name']
        agent_slug = options['agent_slug']
        agent_type = options['agent_type']
        
        self.stdout.write(f"Creating {agent_type} agent: {agent_name} ({agent_slug})")
        
        # Create agent directory
        agent_dir = Path(settings.BASE_DIR) / agent_slug.replace('-', '_')
        if agent_dir.exists():
            self.stdout.write(self.style.ERROR(f"Agent directory {agent_dir} already exists"))
            return
        
        agent_dir.mkdir()
        
        # Template directory
        template_dir = Path(settings.BASE_DIR) / 'agent_base' / 'templates' / 'agent_generator'
        
        # Common context for all templates
        context = {
            'agent_name': agent_name,
            'agent_slug': agent_slug,
            'agent_slug_underscore': agent_slug.replace('-', '_'),
            'agent_name_camel': self.to_camel_case(agent_name),
            'agent_type': agent_type,
        }
        
        if agent_type == 'webhook':
            context.update(self.get_webhook_context(options))
        else:
            options['agent_slug'] = agent_slug
            context.update(self.get_api_context(options))
        
        # Copy and render templates
        self.create_file_from_template(template_dir / f'{agent_type}_models.py', agent_dir / 'models.py', context)
        
        # Use weather-specific processor for weather agents
        if agent_type == 'api' and 'weather' in agent_slug.lower():
            self.create_file_from_template(template_dir / 'weather_api_processor.py', agent_dir / 'processor.py', context)
        else:
            self.create_file_from_template(template_dir / f'{agent_type}_processor.py', agent_dir / 'processor.py', context)
        self.create_file_from_template(template_dir / 'views.py', agent_dir / 'views.py', context)
        self.create_file_from_template(template_dir / 'urls.py', agent_dir / 'urls.py', context)
        self.create_file_from_template(template_dir / 'apps.py', agent_dir / 'apps.py', context)
        self.create_file_from_template(template_dir / 'admin.py', agent_dir / 'admin.py', context)
        self.create_file_from_template(template_dir / '__init__.py', agent_dir / '__init__.py', context)
        
        # Create migrations directory
        migrations_dir = agent_dir / 'migrations'
        migrations_dir.mkdir()
        (migrations_dir / '__init__.py').write_text('')
        
        # Create database entry
        BaseAgent.objects.get_or_create(
            slug=agent_slug,
            defaults={
                'name': agent_name,
                'description': options.get('description', f'{agent_name} agent'),
                'category': options['category'],
                'price': options['price'],
                'icon': options['icon'],
                'agent_type': agent_type,
                'is_active': True,
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {agent_name} agent"))
        agent_slug_underscore = agent_slug.replace('-', '_')
        self.stdout.write(f"Next steps:")
        self.stdout.write(f"1. Add '{agent_slug_underscore}' to INSTALLED_APPS in settings.py")
        self.stdout.write(f"2. Run: python manage.py makemigrations {agent_slug_underscore}")
        self.stdout.write(f"3. Run: python manage.py migrate")
        self.stdout.write(f"4. Create agent template in templates/agents/{agent_slug}/detail.html")
        self.stdout.write(f"5. Add URL patterns to main urls.py")
    
    def get_webhook_context(self, options):
        """Get context for webhook agents"""
        webhook_url = options.get('webhook_url', '')
        agent_id = options.get('agent_id', '1')
        
        return {
            'webhook_url': webhook_url,
            'agent_id': agent_id,
            'request_fields': [
                {'name': 'input_text', 'type': 'TextField', 'args': "blank=True"},
            ],
            'response_fields': [
                {'name': 'output_text', 'type': 'TextField', 'args': "blank=True"},
                {'name': 'raw_response', 'type': 'JSONField', 'args': "default=dict, blank=True"},
            ],
            'message_template': [
                {'name': 'input_text', 'required': True},
            ],
            'message_format': 'Process: {input_text}',
            'additional_fields': [],
            'response_processing': [
                {'name': 'output_text', 'source': 'output', 'default': ''},
                {'name': 'raw_response', 'source': '', 'default': 'dict()'},
            ],
            'request_creation': [
                {'name': 'input_text', 'source': 'input_text', 'default': ''},
            ],
            'processor_params': [
                {'name': 'input_text', 'source': 'input_text'},
            ],
            'result_fields': [
                {'name': 'output_text'},
                {'name': 'raw_response'},
            ],
        }
    
    def get_api_context(self, options):
        """Get context for API agents"""
        api_base_url = options.get('api_base_url', '')
        api_key_env = options.get('api_key_env', '')
        auth_method = options.get('auth_method', 'query')
        agent_slug = options.get('agent_slug', '')
        
        # Weather-specific context
        if 'weather' in agent_slug.lower():
            return {
                'api_base_url': api_base_url,
                'api_key_env': api_key_env,
                'auth_method': auth_method,
                'endpoint_template': api_base_url + '?q={location}&units=metric',
                'endpoint_params': [
                    {'name': 'location'},
                ],
                'api_params': [
                    {'name': 'q', 'value': 'location'},
                    {'name': 'units', 'value': 'metric'},
                ],
                'use_get_method': 'True',
                'request_fields': [
                    {'name': 'location', 'type': 'CharField', 'args': "max_length=200"},
                    {'name': 'report_type', 'type': 'CharField', 'args': "max_length=50, choices=[('current', 'Current Weather'), ('detailed', 'Detailed Report')], default='current'"},
                ],
                'response_fields': [
                    {'name': 'weather_data', 'type': 'JSONField', 'args': "default=dict, blank=True"},
                    {'name': 'temperature', 'type': 'DecimalField', 'args': "max_digits=5, decimal_places=2, null=True, blank=True"},
                    {'name': 'description', 'type': 'CharField', 'args': "max_length=200, blank=True"},
                    {'name': 'humidity', 'type': 'IntegerField', 'args': "null=True, blank=True"},
                    {'name': 'wind_speed', 'type': 'DecimalField', 'args': "max_digits=5, decimal_places=2, null=True, blank=True"},
                    {'name': 'formatted_report', 'type': 'TextField', 'args': "blank=True"},
                ],
                'response_processing': [
                    {'name': 'weather_data', 'source': '', 'default': 'dict()'},
                    {'name': 'temperature', 'source': 'main.temp', 'default': 'None'},
                    {'name': 'description', 'source': 'weather.0.description', 'default': ''},
                    {'name': 'humidity', 'source': 'main.humidity', 'default': 'None'},
                    {'name': 'wind_speed', 'source': 'wind.speed', 'default': 'None'},
                    {'name': 'formatted_report', 'source': 'formatted_report', 'default': ''},
                ],
                'request_creation': [
                    {'name': 'location', 'source': 'location', 'default': ''},
                    {'name': 'report_type', 'source': 'report_type', 'default': 'current'},
                ],
                'processor_params': [
                    {'name': 'location', 'source': 'location'},
                    {'name': 'report_type', 'source': 'report_type'},
                ],
                'result_fields': [
                    {'name': 'weather_data'},
                    {'name': 'temperature'},
                    {'name': 'description'},
                    {'name': 'humidity'},
                    {'name': 'wind_speed'},
                    {'name': 'formatted_report'},
                ],
            }
        
        # Default API context
        return {
            'api_base_url': api_base_url,
            'api_key_env': api_key_env,
            'auth_method': auth_method,
            'endpoint_template': api_base_url,
            'endpoint_params': [],
            'api_params': [],
            'use_get_method': 'True',
            'request_fields': [
                {'name': 'query_param', 'type': 'CharField', 'args': "max_length=200, blank=True"},
            ],
            'response_fields': [
                {'name': 'result_data', 'type': 'JSONField', 'args': "default=dict, blank=True"},
                {'name': 'api_response', 'type': 'TextField', 'args': "blank=True"},
            ],
            'response_processing': [
                {'name': 'result_data', 'source': '', 'default': 'dict()'},
                {'name': 'api_response', 'source': 'result', 'default': ''},
            ],
            'request_creation': [
                {'name': 'query_param', 'source': 'query', 'default': ''},
            ],
            'processor_params': [
                {'name': 'query', 'source': 'query'},
            ],
            'result_fields': [
                {'name': 'result_data'},
                {'name': 'api_response'},
            ],
        }
    
    def to_camel_case(self, text):
        """Convert text to CamelCase"""
        return ''.join(word.capitalize() for word in text.replace('-', ' ').split())
    
    def create_file_from_template(self, template_path, output_path, context):
        """Create a file from template"""
        template_content = template_path.read_text()
        template = Template(template_content)
        rendered_content = template.render(Context(context))
        output_path.write_text(rendered_content)