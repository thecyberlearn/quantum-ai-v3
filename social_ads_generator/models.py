from django.db import models
from decimal import Decimal
from agent_base.models import BaseAgentRequest, BaseAgentResponse


class SocialAdsGeneratorRequest(BaseAgentRequest):
    """Social Ads Generator request tracking"""
    
    # Required fields
    description = models.TextField(help_text="Product/service description")
    social_platform = models.CharField(
        max_length=20,
        choices=[
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('twitter', 'Twitter'),
            ('linkedin', 'LinkedIn'),
            ('tiktok', 'TikTok'),
            ('youtube', 'YouTube'),
        ],
        default='facebook'
    )
    
    # Optional fields
    include_emoji = models.BooleanField(default=False, help_text="Include emojis in ad copy")
    language = models.CharField(
        max_length=20,
        choices=[
            ('English', 'English'),
            ('Arabic', 'Arabic (العربية)'),
            ('Spanish', 'Spanish (Español)'),
            ('French', 'French (Français)'),
            ('German', 'German (Deutsch)'),
            ('Chinese', 'Chinese (中文)'),
        ],
        default='English'
    )
    
    
    class Meta:
        db_table = 'social_ads_generator_requests'
        verbose_name = 'Social Ads Generator Request'
        verbose_name_plural = 'Social Ads Generator Requests'


class SocialAdsGeneratorResponse(BaseAgentResponse):
    """Social Ads Generator response storage"""
    
    request = models.OneToOneField(
        SocialAdsGeneratorRequest, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Agent-specific response fields
    ad_copy = models.TextField(blank=True, help_text="Generated ad copy")
    hashtags = models.TextField(blank=True, help_text="Suggested hashtags")
    targeting_suggestions = models.TextField(blank=True, help_text="Audience targeting suggestions")
    formatted_ad = models.TextField(blank=True, help_text="Formatted ad content")
    raw_response = models.JSONField(default=dict, blank=True)
    
    
    class Meta:
        db_table = 'social_ads_generator_responses'
        verbose_name = 'Social Ads Generator Response'
        verbose_name_plural = 'Social Ads Generator Responses'