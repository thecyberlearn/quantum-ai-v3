import requests
from django.conf import settings
from django.utils import timezone
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime


class BaseAgentProcessor(ABC):
    """
    Base class for all agent processors.
    
    This class provides a standardized interface for processing agent requests,
    whether they use webhooks or direct API calls.
    """
    
    # These should be set in subclasses
    agent_slug = None
    processor_type = None  # 'webhook' or 'api'
    
    def __init__(self):
        if not self.agent_slug:
            raise ValueError("agent_slug must be defined in subclass")
        if not self.processor_type:
            raise ValueError("processor_type must be defined in subclass")
    
    @abstractmethod
    def prepare_request_data(self, **kwargs):
        """Prepare the request data for the webhook/API"""
        pass
    
    @abstractmethod
    def make_request(self, data, timeout=60):
        """Make the actual HTTP request"""
        pass
    
    @abstractmethod
    def process_response(self, response_data, request_obj):
        """Process the response and create database objects"""
        pass
    
    def process_request(self, **kwargs):
        """Main processing method - standardized across all agents"""
        try:
            # Prepare request data
            request_data = self.prepare_request_data(**kwargs)
            
            # Make the request
            response_data = self.make_request(request_data)
            
            # Create request object if provided
            request_obj = kwargs.get('request_obj')
            if request_obj:
                # Process response and create response object
                result = self.process_response(response_data, request_obj)
                return result
            else:
                # Return raw response for testing
                return response_data
            
        except Exception as e:
            print(f"{self.agent_slug}: Error processing request: {e}")
            if 'request_obj' in kwargs and kwargs['request_obj']:
                kwargs['request_obj'].status = 'failed'
                kwargs['request_obj'].save()
            raise


class StandardWebhookProcessor(BaseAgentProcessor):
    """
    Standardized webhook processor for N8N-based agents.
    
    This processor handles the common webhook format with message-based payload
    and standardized response processing.
    """
    
    processor_type = 'webhook'
    
    # These should be set in subclasses
    webhook_url = None
    agent_id = None
    
    def __init__(self):
        super().__init__()
        if not self.webhook_url:
            raise ValueError("webhook_url must be defined in subclass")
        if not self.agent_id:
            raise ValueError("agent_id must be defined in subclass")
    
    def prepare_message_text(self, **kwargs):
        """Prepare the message text for the webhook - override in subclasses"""
        return f"Process request for {self.agent_slug}"
    
    def prepare_request_data(self, **kwargs):
        """Prepare standard webhook request data"""
        user_id = kwargs.get('user_id')
        
        # Get the formatted message text
        message_text = self.prepare_message_text(**kwargs)
        
        return {
            'message': {
                'text': message_text
            },
            'sessionId': f'{self.agent_slug}_{int(datetime.now().timestamp() * 1000)}',
            'userId': str(user_id),
            'agentId': str(self.agent_id),
            **self.get_additional_fields(**kwargs)
        }
    
    def get_additional_fields(self, **kwargs):
        """Get additional fields for the webhook payload - override in subclasses"""
        return {}
    
    def make_request(self, data, timeout=60):
        """Make webhook request with standardized error handling"""
        try:
            print(f"{self.agent_slug}: Sending webhook request to {self.webhook_url}")
            print(f"{self.agent_slug}: Payload: {json.dumps(data, indent=2)}")
            
            start_time = time.time()
            response = requests.post(self.webhook_url, json=data, timeout=timeout)
            processing_time = time.time() - start_time
            
            print(f"{self.agent_slug}: Response status: {response.status_code}")
            print(f"{self.agent_slug}: Response text: {response.text[:500]}...")
            
            response.raise_for_status()
            
            # Check if response has content
            if not response.text.strip():
                raise ValueError("Empty response from webhook")
            
            # Try to parse JSON, fallback to text
            try:
                response_data = response.json()
            except ValueError:
                response_data = {'output': response.text}
            
            # Add processing metadata
            response_data['processing_time'] = processing_time
            response_data['success'] = True
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"{self.agent_slug}: Webhook request error: {e}")
            raise ValueError(f"Webhook error: {e}")
        except Exception as e:
            print(f"{self.agent_slug}: Unexpected error: {e}")
            raise ValueError(f"Processing error: {e}")


class StandardAPIProcessor(BaseAgentProcessor):
    """
    Standardized API processor for direct API integrations.
    
    This processor handles direct API calls with authentication and
    standardized response processing.
    """
    
    processor_type = 'api'
    
    # These should be set in subclasses
    api_base_url = None
    api_key_env = None
    auth_method = 'bearer'  # 'bearer', 'api-key', 'basic', 'query'
    
    def __init__(self):
        super().__init__()
        if not self.api_base_url:
            raise ValueError("api_base_url must be defined in subclass")
        if self.api_key_env and hasattr(settings, self.api_key_env):
            self.api_key = getattr(settings, self.api_key_env)
        else:
            self.api_key = None
    
    def get_headers(self):
        """Get headers for API request"""
        headers = {'Content-Type': 'application/json'}
        
        if self.api_key:
            if self.auth_method == 'bearer':
                headers['Authorization'] = f'Bearer {self.api_key}'
            elif self.auth_method == 'api-key':
                headers['X-API-Key'] = self.api_key
            elif self.auth_method == 'basic':
                import base64
                auth_string = base64.b64encode(f'{self.api_key}:'.encode()).decode()
                headers['Authorization'] = f'Basic {auth_string}'
        
        return headers
    
    def get_endpoint(self, **kwargs):
        """Get the API endpoint - override in subclasses"""
        return self.api_base_url
    
    def prepare_request_data(self, **kwargs):
        """Prepare API request data - override in subclasses"""
        return kwargs
    
    def make_request(self, data, timeout=60):
        """Make API request with standardized error handling"""
        try:
            endpoint = self.get_endpoint(**data)
            headers = self.get_headers()
            
            # For query-based auth, add API key to URL
            if self.auth_method == 'query' and self.api_key:
                separator = '&' if '?' in endpoint else '?'
                endpoint = f"{endpoint}{separator}appid={self.api_key}"
            
            print(f"{self.agent_slug}: Making API request to {endpoint}")
            print(f"{self.agent_slug}: Headers: {headers}")
            print(f"{self.agent_slug}: Data: {json.dumps(data, indent=2)}")
            
            start_time = time.time()
            
            # Use GET for most API calls, POST for data submission
            if self.should_use_get(**data):
                response = requests.get(endpoint, headers=headers, timeout=timeout)
            else:
                response = requests.post(endpoint, json=data, headers=headers, timeout=timeout)
            
            processing_time = time.time() - start_time
            
            print(f"{self.agent_slug}: Response status: {response.status_code}")
            print(f"{self.agent_slug}: Response text: {response.text[:500]}...")
            
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                response_data = response.json()
            except ValueError:
                response_data = {'result': response.text}
            
            # Add processing metadata
            response_data['processing_time'] = processing_time
            response_data['success'] = True
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"{self.agent_slug}: API request error: {e}")
            raise ValueError(f"API error: {e}")
        except Exception as e:
            print(f"{self.agent_slug}: Unexpected error: {e}")
            raise ValueError(f"Processing error: {e}")
    
    def should_use_get(self, **kwargs):
        """Determine if GET should be used instead of POST - override in subclasses"""
        return True


class WebhookFormatDetector:
    """
    Utility class to detect webhook format by testing endpoints.
    
    This helps determine what format a webhook expects by sending
    test requests and analyzing the response.
    """
    
    @staticmethod
    def test_webhook_format(webhook_url, timeout=10):
        """Test webhook to determine expected format"""
        test_formats = [
            # N8N message format
            {
                'name': 'n8n_message',
                'payload': {
                    'message': {'text': 'Test message'},
                    'sessionId': 'test_session',
                    'userId': 'test_user',
                    'agentId': '1'
                }
            },
            # Direct data format
            {
                'name': 'direct_data',
                'payload': {
                    'input': 'test data',
                    'user_id': 'test_user',
                    'agent_type': 'test_agent'
                }
            },
            # Simple format
            {
                'name': 'simple',
                'payload': {'test': 'data'}
            }
        ]
        
        results = []
        
        for format_test in test_formats:
            try:
                response = requests.post(
                    webhook_url, 
                    json=format_test['payload'], 
                    timeout=timeout
                )
                results.append({
                    'format': format_test['name'],
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response': response.text[:200],
                    'error': None
                })
            except Exception as e:
                results.append({
                    'format': format_test['name'],
                    'status_code': None,
                    'success': False,
                    'response': None,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def detect_best_format(webhook_url):
        """Detect the best format for a webhook"""
        results = WebhookFormatDetector.test_webhook_format(webhook_url)
        
        # Find the first successful format
        for result in results:
            if result['success']:
                return result['format']
        
        # If no format works, return the first one (n8n_message) as default
        return 'n8n_message'