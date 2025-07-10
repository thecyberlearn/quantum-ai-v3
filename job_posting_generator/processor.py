from agent_base.processors import StandardWebhookProcessor
from django.utils import timezone
from django.conf import settings
from .models import JobPostingGeneratorRequest, JobPostingGeneratorResponse
import json


class JobPostingGeneratorProcessor(StandardWebhookProcessor):
    """Webhook processor for Job Posting Generator agent"""
    
    agent_slug = 'job-posting-generator'
    webhook_url = settings.N8N_WEBHOOK_JOB_POSTING
    agent_id = 'job-posting'
    
    def prepare_message_text(self, **kwargs):
        """Prepare detailed job posting prompt for N8N webhook"""
        request_obj = kwargs.get('request_obj')
        if not request_obj:
            return "Create a professional job posting"
        
        # Build comprehensive job posting prompt
        prompt = f"""
Create a professional job posting for the following position:

Job Title: {request_obj.job_title}
Company: {request_obj.company_name}
Location: {request_obj.location}
Contract Type: {request_obj.get_contract_type_display()}
Seniority Level: {request_obj.get_seniority_level_display()}
Language: {request_obj.language}

Job Description:
{request_obj.job_description}
"""
        
        if request_obj.company_website:
            prompt += f"\nCompany Website: {request_obj.company_website}"
        
        if request_obj.how_to_apply:
            prompt += f"\n\nApplication Instructions:\n{request_obj.how_to_apply}"
        
        prompt += "\n\nPlease create a comprehensive, professional job posting that includes all necessary sections such as job overview, responsibilities, qualifications, benefits, and clear application instructions."
        
        return prompt
    
    def process_response(self, response_data, request_obj):
        """Process webhook response"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            # Handle array response from N8N (extract first item)
            if isinstance(response_data, list) and len(response_data) > 0:
                response_data = response_data[0]
            
            # Extract job posting content
            job_posting_content = ""
            if isinstance(response_data, dict):
                job_posting_content = response_data.get('output', response_data.get('text', response_data.get('content', '')))
            elif isinstance(response_data, str):
                job_posting_content = response_data
            
            # Determine success based on response
            success = bool(job_posting_content.strip()) and len(job_posting_content.strip()) > 50
            
            # Create response object
            response_obj = JobPostingGeneratorResponse.objects.create(
                request=request_obj,
                success=success,
                processing_time=response_data.get('processing_time', 0) if isinstance(response_data, dict) else 0,
                job_posting_content=job_posting_content,
                formatted_posting=job_posting_content,  # Same content for now
                raw_response=response_data if isinstance(response_data, dict) else {'content': response_data}
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"Job Posting Generator - {request_obj.job_title} at {request_obj.company_name}",
                    'job-posting-generator'
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
            error_response = JobPostingGeneratorResponse.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=0
            )
            
            raise Exception(f"Failed to process Job Posting Generator response: {e}")