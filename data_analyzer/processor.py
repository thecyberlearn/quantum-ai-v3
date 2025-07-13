from agent_base.processors import StandardWebhookProcessor
from django.utils import timezone
from django.conf import settings
from .models import DataAnalysisAgentRequest, DataAnalysisAgentResponse
import json
import requests
import time


class DataAnalysisAgentProcessor(StandardWebhookProcessor):
    """Webhook processor for Data Analysis Agent agent"""
    
    agent_slug = 'data-analyzer'
    webhook_url = settings.N8N_WEBHOOK_DATA_ANALYZER
    agent_id = 'data-analysis-001'
    
    def make_request(self, data, timeout=60):
        """Override to send PDF file as binary data instead of JSON"""
        try:
            request_obj = data.get('request_obj')
            if not request_obj or not request_obj.data_file:
                raise ValueError("No PDF file found in request")
            
            print(f"{self.agent_slug}: Sending PDF file to N8N webhook: {self.webhook_url}")
            
            # Read the PDF file
            pdf_file = request_obj.data_file
            pdf_file.seek(0)  # Reset file pointer to beginning
            file_content = pdf_file.read()
            
            print(f"{self.agent_slug}: File size: {len(file_content)} bytes")
            print(f"{self.agent_slug}: File name: {pdf_file.name}")
            
            # Prepare multipart form data
            files = {
                'file': (pdf_file.name, file_content, 'application/pdf')
            }
            
            start_time = time.time()
            response = requests.post(self.webhook_url, files=files, timeout=timeout)
            processing_time = time.time() - start_time
            
            print(f"{self.agent_slug}: Response status: {response.status_code}")
            print(f"{self.agent_slug}: Response text: {response.text[:500]}...")
            
            response.raise_for_status()
            
            # Check if response has content
            if not response.text.strip():
                raise ValueError("Empty response from webhook")
            
            # Parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                raise ValueError("Invalid JSON response from N8N workflow")
            
            # Handle array response from N8N (extract first item)
            if isinstance(response_data, list) and len(response_data) > 0:
                response_data = response_data[0]
            elif isinstance(response_data, list) and len(response_data) == 0:
                raise ValueError("Empty array response from N8N workflow")
            
            # Add processing metadata
            response_data['processing_time'] = processing_time
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"{self.agent_slug}: Webhook request error: {e}")
            raise ValueError(f"Webhook error: {e}")
        except Exception as e:
            print(f"{self.agent_slug}: Processing error: {e}")
            raise ValueError(f"Processing error: {e}")
    
    def prepare_request_data(self, **kwargs):
        """Prepare request data - for binary upload, we pass the request object"""
        return {
            'request_obj': kwargs.get('request_obj'),
            'analysis_type': kwargs.get('analysis_type', 'summary')
        }
    
    def process_response(self, response_data, request_obj):
        """Process webhook response from N8N"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Extract N8N response data based on workflow format
            analysis_text = response_data.get('analysis', '')
            status = response_data.get('status', 'unknown')
            processed_at = response_data.get('processed_at', '')
            
            # Map N8N response to Django fields
            analysis_results = {
                'status': status,
                'processed_at': processed_at,
                'analysis_type': getattr(request_obj, 'analysis_type', 'summary')
            }
            
            # Use analysis text for multiple fields for compatibility
            insights_summary = analysis_text
            report_text = analysis_text
            raw_response = response_data
            
            # Determine success based on N8N status
            success = status == 'success' and bool(analysis_text)
            
            # Create response object
            response_obj = DataAnalysisAgentResponse.objects.create(
                request=request_obj,
                success=success,
                processing_time=response_data.get('processing_time', 0),
                analysis_results=analysis_results,
                insights_summary=insights_summary,
                report_text=report_text,
                raw_response=raw_response,
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"Data Analysis Agent - {request_obj.data_file.name if request_obj.data_file else 'PDF Analysis'}",
                    'data-analyzer'
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
            error_response = DataAnalysisAgentResponse.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=response_data.get('processing_time', 0) if response_data else 0
            )
            
            raise Exception(f"Failed to process Data Analysis Agent response: {e}")