from agent_base.processors import StandardWebhookProcessor
from django.utils import timezone
from django.conf import settings
from .models import {{ agent_name_camel }}Request, {{ agent_name_camel }}Response
import json


class {{ agent_name_camel }}Processor(StandardWebhookProcessor):
    """Webhook processor for {{ agent_name }} agent"""
    
    agent_slug = '{{ agent_slug }}'
    webhook_url = settings.N8N_WEBHOOK_{{ agent_slug_underscore|upper }}
    agent_id = '{{ agent_id }}'
    
    def prepare_message_text(self, **kwargs):
        """Prepare message for N8N webhook"""
        return "{{ message_format }}".format(**kwargs)
    
    def process_response(self, response_data, request_obj):
        """Process webhook response"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract response data
            {% for field in response_processing %}{% if field.source %}{{ field.name }} = response_data.get('{{ field.source }}', {{ field.default }}){% else %}{{ field.name }} = response_data if response_data else {{ field.default }}{% endif %}
            {% endfor %}
            
            # Determine success based on response
            success = response_data.get('success', True) and response_data.get('status') == 'success'
            
            # Create response object
            response_obj = {{ agent_name_camel }}Response.objects.create(
                request=request_obj,
                success=success,
                processing_time=response_data.get('processing_time', 0),
                {% for field in response_processing %}{{ field.name }}={{ field.name }},
                {% endfor %}
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"{{ agent_name }} - Processing",
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