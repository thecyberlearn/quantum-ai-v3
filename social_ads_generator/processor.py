from agent_base.processors import StandardWebhookProcessor
from django.utils import timezone
from django.conf import settings
from .models import SocialAdsGeneratorRequest, SocialAdsGeneratorResponse
import json


class SocialAdsGeneratorProcessor(StandardWebhookProcessor):
    """Webhook processor for Social Ads Generator agent"""
    
    agent_slug = 'social-ads-generator'
    webhook_url = settings.N8N_WEBHOOK_SOCIAL_ADS
    agent_id = 'social-ads'
    
    def prepare_message_text(self, **kwargs):
        """Prepare detailed social ads prompt for N8N webhook"""
        request_obj = kwargs.get('request_obj')
        if not request_obj:
            return "Create a social media advertisement"
        
        # Build comprehensive social ads prompt
        prompt = f"""
Create a compelling social media advertisement for the following:

Product/Service Description:
{request_obj.description}

Target Platform: {request_obj.get_social_platform_display()}
Language: {request_obj.language}
Include Emojis: {'Yes' if request_obj.include_emoji else 'No'}

Please create platform-optimized ad copy that:
- Captures attention instantly
- Highlights key benefits and unique selling points
- Uses persuasive messaging that motivates action
- Includes a strong call-to-action
- Is tailored to {request_obj.get_social_platform_display()} audience
- Uses {request_obj.language} language
"""
        
        if request_obj.include_emoji:
            prompt += "\n- Incorporates relevant emojis for engagement"
        
        prompt += "\n\nFormat the response as professional ad copy ready for social media posting."
        
        return prompt
    
    def process_response(self, response_data, request_obj):
        """Process webhook response"""
        try:
            request_obj.status = 'processing'
            request_obj.save()
            
            
            # Handle array response from N8N (extract first item)
            if isinstance(response_data, list) and len(response_data) > 0:
                response_data = response_data[0]
            
            # Extract ad copy content
            ad_copy = ""
            if isinstance(response_data, dict):
                ad_copy = response_data.get('output', response_data.get('text', response_data.get('content', '')))
            elif isinstance(response_data, str):
                ad_copy = response_data
            
            # Parse ad copy for different components (basic parsing)
            hashtags = ""
            targeting_suggestions = ""
            formatted_ad = ad_copy
            
            # Simple extraction of hashtags if present
            if '#' in ad_copy:
                lines = ad_copy.split('\n')
                hashtag_lines = [line for line in lines if line.strip().startswith('#')]
                if hashtag_lines:
                    hashtags = ' '.join(hashtag_lines)
            
            # Determine success based on response
            success = bool(ad_copy.strip()) and len(ad_copy.strip()) > 20
            
            # Create response object
            response_obj = SocialAdsGeneratorResponse.objects.create(
                request=request_obj,
                success=success,
                processing_time=response_data.get('processing_time', 0) if isinstance(response_data, dict) else 0,
                ad_copy=ad_copy,
                hashtags=hashtags,
                targeting_suggestions=targeting_suggestions,
                formatted_ad=formatted_ad,
                raw_response=response_data if isinstance(response_data, dict) else {'content': response_data}
            )
            
            # Only deduct wallet balance after successful processing
            if success:
                request_obj.user.deduct_balance(
                    request_obj.cost,
                    f"Social Ads Generator - {request_obj.get_social_platform_display()} ad for {request_obj.description[:50]}...",
                    'social-ads-generator'
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
            error_response = SocialAdsGeneratorResponse.objects.create(
                request=request_obj,
                success=False,
                error_message=str(e),
                processing_time=0
            )
            
            raise Exception(f"Failed to process Social Ads Generator response: {e}")