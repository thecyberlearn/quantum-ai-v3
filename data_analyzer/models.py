from django.db import models
from decimal import Decimal
from agent_base.models import BaseAgentRequest, BaseAgentResponse


class DataAnalysisAgentRequest(BaseAgentRequest):
    """Data Analysis Agent request tracking"""
    
    # Agent-specific request fields  
    data_file = models.FileField(upload_to='uploads/data_analyzer/', blank=True)
    analysis_type = models.CharField(
        max_length=50,
        choices=[
            ('summary', 'Summary Analysis'),
            ('detailed', 'Detailed Analysis'),
            ('statistical', 'Statistical Analysis'),
        ],
        default='summary'
    )
    # Legacy field (keeping for compatibility)
    input_text = models.TextField(blank=True, null=True)
    
    
    class Meta:
        db_table = 'data_analyzer_requests'
        verbose_name = 'Data Analysis Agent Request'
        verbose_name_plural = 'Data Analysis Agent Requests'


class DataAnalysisAgentResponse(BaseAgentResponse):
    """Data Analysis Agent response storage"""
    
    request = models.OneToOneField(
        DataAnalysisAgentRequest, 
        on_delete=models.CASCADE, 
        related_name='response'
    )
    
    # Agent-specific response fields
    analysis_results = models.JSONField(default=dict, blank=True)
    insights_summary = models.TextField(blank=True)
    report_text = models.TextField(blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    # Legacy field (keeping for compatibility)
    output_text = models.TextField(blank=True, null=True)
    
    
    class Meta:
        db_table = 'data_analyzer_responses'
        verbose_name = 'Data Analysis Agent Response'
        verbose_name_plural = 'Data Analysis Agent Responses'