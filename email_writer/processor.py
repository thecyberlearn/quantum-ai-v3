import json
from agent_base.processors import BaseAgentProcessor
from .models import EmailWriterRequest


class EmailWriterProcessor(BaseAgentProcessor):
    """Email Writer agent processor"""
    
    model_class = EmailWriterRequest
    agent_name = "Email Writer"
    cost = 3.00  # AED per request
    
    def prepare_webhook_data(self, request_obj):
        """Prepare data for webhook processing"""
        return {
            'email_type': request_obj.email_type,
            'recipient': request_obj.recipient,
            'subject': request_obj.subject,
            'main_message': request_obj.main_message,
            'tone': request_obj.tone,
            'length': request_obj.length,
        }
    
    def process_webhook_response(self, request_obj, webhook_response):
        """Process webhook response and update request object"""
        try:
            if isinstance(webhook_response, str):
                response_data = json.loads(webhook_response)
            else:
                response_data = webhook_response
            
            # Extract email content from response
            email_content = ""
            
            # Try different possible response formats
            if 'email_content' in response_data:
                email_content = response_data['email_content']
            elif 'content' in response_data:
                email_content = response_data['content']
            elif 'output' in response_data:
                email_content = response_data['output']
            elif 'generated_email' in response_data:
                email_content = response_data['generated_email']
            elif isinstance(response_data, str):
                email_content = response_data
            else:
                # If no specific field found, try to extract text
                email_content = str(response_data)
            
            # Update request object
            request_obj.email_content = email_content
            request_obj.save()
            
            return {
                'success': True,
                'email_content': email_content,
                'status': 'completed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to process email generation: {str(e)}",
                'status': 'failed'
            }
    
    def get_result_summary(self, request_obj):
        """Get a summary of the results for display"""
        if request_obj.email_content:
            return {
                'email_type': request_obj.get_email_type_display(),
                'recipient': request_obj.recipient,
                'tone': request_obj.get_tone_display(),
                'length': request_obj.get_length_display(),
                'email_content': request_obj.email_content,
                'has_subject': bool(request_obj.subject),
                'subject': request_obj.subject
            }
        return None