from agent_base.processors import StandardAPIProcessor
from django.utils import timezone
from django.conf import settings
from .models import {{ agent_name_camel }}Request, {{ agent_name_camel }}Response
import json


class {{ agent_name_camel }}Processor(StandardAPIProcessor):
    """API processor for {{ agent_name }} agent"""
    
    agent_slug = '{{ agent_slug }}'
    api_base_url = '{{ api_base_url }}'
    api_key_env = '{{ api_key_env }}'
    auth_method = '{{ auth_method }}'
    
    def prepare_request_data(self, **kwargs):
        """Prepare API request data"""
        {% if api_params %}data = {}
        {% for param in api_params %}data['{{ param.name }}'] = kwargs.get('{{ param.value }}', '')
        {% endfor %}return data{% else %}return {
            'query': kwargs.get('query', ''),
        }{% endif %}
    
    def should_use_get(self, **kwargs):
        """Use GET method for API calls"""
        return {{ use_get_method }}
    
    def build_url(self, **kwargs):
        """Build the complete API URL"""
        {% if endpoint_params %}url = self.api_base_url
        {% for param in endpoint_params %}url = url.replace('{{'{{ param.name }}}}', str(kwargs.get('{{ param.name }}', '')))
        {% endfor %}return url{% else %}return self.api_base_url{% endif %}
    
    def process_response(self, response_data, request_obj):
        """Process the API response"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract response data
            {% for field in response_processing %}{% if field.source %}{{ field.name }} = self.get_nested_value(response_data, '{{ field.source }}') or {{ field.default }}{% else %}{{ field.name }} = response_data if response_data else {{ field.default }}{% endif %}
            {% endfor %}
            
            # Determine success based on response (check for valid data)
            success = (response_data.get('success', True) if isinstance(response_data, dict) else True) and bool(response_data)
            
            # Create response object
            response_obj = {{ agent_name_camel }}Response.objects.create(
                request=request_obj,
                success=success,
                processing_time=response_data.get('processing_time', 0) if isinstance(response_data, dict) else 0,
                {% for field in response_processing %}{{ field.name }}={{ field.name }},
                {% endfor %}
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"{{ agent_name }} - API Request",
                    '{{ agent_slug }}'
                )
                print(f"{self.agent_slug}: Wallet deducted {request_obj.cost} AED for successful processing")
            
            # Update request as completed
            request_obj.status = 'completed' if success else 'failed'
            request_obj.processed_at = timezone.now()
            request_obj.save()
            
            return response_obj
            
        except Exception as e:
            # Handle error
            request_obj.status = 'failed'
            request_obj.save()
            
            # Create error response
            error_response = {{ agent_name_camel }}Response.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=0
            )
            
            raise Exception(f"Failed to process {{ agent_name }} response: {e}")
    
    def get_nested_value(self, data, path):
        """Get nested value from dictionary using dot notation"""
        if not path or not isinstance(data, dict):
            return None
        
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:
                return None
        
        return value